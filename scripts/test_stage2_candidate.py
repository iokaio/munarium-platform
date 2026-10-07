#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fixed-vector, admission-boundary and export-integrity checks; no runtime effects."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from stage2_contract import Oracle, digest, encoded
from vendor_stage2 import RELATIVE, read_committed, verify_lock, write_export

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/decisions/stage2-v1"


def load():
    return [json.loads((DIRECTORY / name).read_text(encoding="utf-8"))
            for name in ("schema.json", "profile.json", "vectors.json")]


def changed(value, changes):
    value = copy.deepcopy(value)
    for path, replacement in changes.items():
        parent = value
        parts = path.split(".")
        for key in parts[:-1]:
            parent = parent[int(key)] if isinstance(parent, list) else parent[key]
        parent[int(parts[-1]) if isinstance(parent, list) else parts[-1]] = copy.deepcopy(replacement)
    return value


class Stage2Candidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema, cls.profile, cls.vectors = load()
        cls.records, cls.trusted = cls.vectors["records"], cls.vectors["trusted"]
        cls.oracle = Oracle(cls.schema, cls.profile, cls.records)

    def test_fixed_records_bytes_and_digests(self):
        for name, value in self.records.items():
            with self.subTest(record=name):
                self.oracle.verify(value, self.trusted)
                self.assertEqual(encoded(value).decode(), self.vectors["canonical"][name])
                self.assertEqual(digest(value["type"], value), self.vectors["digests"][name])
                self.assertEqual(self.oracle.wire(encoded(value), self.trusted), value)

    def test_fixed_refusal_cases(self):
        self.assertEqual(len({c["id"] for c in self.vectors["cases"]}), len(self.vectors["cases"]))
        for case in self.vectors["cases"]:
            with self.subTest(case=case["id"]):
                value = changed(self.records[case["record"]], case["changes"])
                context = changed(self.trusted, case["context_changes"])
                if case["expected"] == "accept":
                    self.oracle.verify(value, context)
                else:
                    with self.assertRaisesRegex(ValueError, "^" + case["expected"] + "$"):
                        self.oracle.verify(value, context)

    def test_required_and_extra_fields_on_each_record(self):
        for name, original in self.records.items():
            for key in original:
                with self.subTest(record=name, missing=key):
                    value = copy.deepcopy(original)
                    del value[key]
                    with self.assertRaisesRegex(ValueError, "InvalidShape"):
                        self.oracle.verify(value, self.trusted)
            value = dict(original, forwarded_authority=True)
            with self.assertRaisesRegex(ValueError, "InvalidShape"):
                self.oracle.verify(value, self.trusted)

    def test_wire_ambiguity_is_rejected(self):
        wire = encoded(self.records["request"])
        for raw in (b" " + wire, wire + b"\n", b'\xef\xbb\xbf' + wire,
                    b'{"schema_version":1,' + wire[1:], wire.replace(b'"schema_version":1', b'"schema_version":1.0'),
                    wire.replace(b'"schema_version":1', b'"schema_version":true'),
                    wire.replace(b'"schema_version":1', b'"schema_version":-0'),
                    wire.replace(b'"schema_version":1', b'"schema_version":9007199254740992')):
            with self.subTest(raw=raw[:55]):
                with self.assertRaises(ValueError):
                    self.oracle.wire(raw, self.trusted)
        value = changed(self.records["request"], {"operation.id": "operation\n"})
        with self.assertRaisesRegex(ValueError, "InvalidShape"):
            self.oracle.verify(value, self.trusted)

    def test_activation_completion_requires_every_exact_receipt(self):
        activation, pause = self.records["activation"], self.records["pause"]
        receipts = [self.records[p + "-receipt"] for p in self.profile["participants"]]
        self.oracle.completion(activation, pause, receipts, self.trusted)
        for bad in (receipts[:-1], receipts + [receipts[0]], receipts[:-1] + [receipts[0]], receipts[:-1] + [pause]):
            with self.subTest(receipts=len(bad)):
                with self.assertRaises(ValueError):
                    self.oracle.completion(activation, pause, bad, self.trusted)
        with self.assertRaisesRegex(ValueError, "StaleContext"):
            self.oracle.completion(activation, pause, receipts, dict(self.trusted, paused_transition_digest="sha256:" + "0" * 64))
        wrong = changed(pause, {"artifact_set_digest": "sha256:" + "0" * 64})
        with self.assertRaisesRegex(ValueError, "InvalidBinding"):
            self.oracle.completion(activation, wrong, receipts, self.trusted)

    def test_current_lookup_cannot_refresh_expiry_or_immutable_approval(self):
        approval = changed(self.records["approval"], {"expires_at": 1300})
        with self.assertRaisesRegex(ValueError, "Expired"):
            self.oracle.verify(approval, self.trusted)
        approval = changed(self.records["approval"], {"issued_at": 991, "expires_at": 1291})
        with self.assertRaisesRegex(ValueError, "InvalidBinding"):
            self.oracle.verify(approval, self.trusted)

    def test_recording_history_does_not_recheck_expired_execution_as_new_authority(self):
        context = copy.deepcopy(self.trusted)
        event = self.records["outcome"]
        context.update(now=5000, recovery_recorder_authorized=True, historical_events=[digest("accountability-event", event)])
        context["streams"][event["stream"]["id"]]["generation"] = 2
        self.oracle.verify(event, context)
        with self.assertRaises(ValueError):
            self.oracle.verify(self.records["approval"], context)
        with self.assertRaisesRegex(ValueError, "Unauthorized"):
            self.oracle.verify(event, dict(context, recovery_cutoff=999))

    def test_bindings_survive_rehashed_tampering(self):
        for name, path, replacement in (
                ("send-intent", "payload.effect_key", "new-send"),
                ("send-intent", "payload.predispatch_ack_digest", "sha256:" + "0" * 64),
                ("predispatch", "payload.consumption_event_digest", "sha256:" + "0" * 64),
                ("consumption-reserved", "payload.reservations.0.root.id", "other-root"),
                ("outcome", "payload.recovery_epoch", 2)):
            with self.subTest(record=name, field=path):
                event = changed(self.records[name], {path: replacement})
                event["payload_digest"] = digest("event-payload", event["payload"])
                with self.assertRaisesRegex(ValueError, "InvalidBinding"):
                    self.oracle.verify(event, self.trusted)

    def test_digest_domains_cannot_be_substituted(self):
        request = self.records["request"]
        digests = {digest(domain, request) for domain in ("action-request", "action-approval", "event-payload", "context")}
        self.assertEqual(len(digests), 4)
        old = "sha256:" + hashlib.sha256(b"munarium:decision-request:v1\0" + encoded(request)).hexdigest()
        self.assertNotIn(old, digests)

    def test_unsupported_schema_vocabulary_fails(self):
        bad = copy.deepcopy(self.schema)
        bad["$defs"]["scope"]["unevaluatedProperties"] = False
        with self.assertRaisesRegex(ValueError, "UnsupportedSchema"):
            Oracle(bad, self.profile, self.records)

    def test_lock_and_reproducibility(self):
        contents = {name: (DIRECTORY / name).read_bytes().replace(b"\r\n", b"\n") for name in
                    ("README.md", "schema.json", "profile.json", "vectors.json", "bundle-lock.json")}
        verify_lock(contents)
        result = subprocess.run([sys.executable, str(ROOT / "scripts/generate_stage2_candidate.py"), "--check"], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        corrupt = dict(contents, **{"profile.json": contents["profile.json"] + b" "})
        with self.assertRaisesRegex(ValueError, "lock mismatch"):
            verify_lock(corrupt)
        # A lock cannot redirect the exporter into an ignored or external path.
        lock = json.loads(contents["bundle-lock.json"])
        lock["files"]["../secret"] = "0" * 64
        corrupt = dict(contents, **{"bundle-lock.json": json.dumps(lock).encode()})
        with self.assertRaisesRegex(ValueError, "file set"):
            verify_lock(corrupt)

    def test_export_preflights_collisions_and_is_idempotent(self):
        contents = {name: (DIRECTORY / name).read_bytes().replace(b"\r\n", b"\n") for name in
                    ("README.md", "schema.json", "profile.json", "vectors.json", "bundle-lock.json")}
        contents["vendor-lock.json"] = b'{"fixture":"export-preflight-only"}\n'
        with tempfile.TemporaryDirectory(prefix="stage2-export-test-") as folder:
            destination = Path(folder) / "candidate"
            destination.mkdir()
            (destination / "vectors.json").write_bytes(b"unrelated content")
            with self.assertRaisesRegex(ValueError, "refusing different"):
                write_export(contents, destination)
            self.assertEqual([p.name for p in destination.iterdir()], ["vectors.json"])
            self.assertEqual((destination / "vectors.json").read_bytes(), b"unrelated content")
            fresh = Path(folder) / "fresh"
            write_export(contents, fresh)
            write_export(contents, fresh)
            self.assertEqual({p.name: p.read_bytes() for p in fresh.iterdir()}, contents)

    def test_export_refuses_uncommitted_candidate_bytes(self):
        contents = {name: (DIRECTORY / name).read_bytes().replace(b"\r\n", b"\n") for name in
                    ("README.md", "schema.json", "profile.json", "vectors.json", "bundle-lock.json")}
        # Supply immutable Git responses independently from the mutable filesystem.
        # The actual committed-source CLI export is also checked at packet handoff.
        revision = "a" * 40
        def git_output(command, **kwargs):
            if command[-2:] == ["rev-parse", "HEAD"]:
                return revision + "\n"
            self.assertEqual(command[-2], "show")
            self.assertTrue(command[-1].startswith(revision + ":"))
            return contents[command[-1].split("/")[-1]]
        with tempfile.TemporaryDirectory(prefix="stage2-source-test-") as folder:
            root = Path(folder)
            source = root / RELATIVE
            source.mkdir(parents=True)
            for name, raw in contents.items():
                (source / name).write_bytes(raw)
            with patch("vendor_stage2.subprocess.check_output", side_effect=git_output):
                exported = read_committed(root)
                self.assertEqual(json.loads(exported["vendor-lock.json"])["revision"], revision)
                (source / "README.md").write_bytes(contents["README.md"] + b"changed after review\n")
                with self.assertRaisesRegex(ValueError, "differs from committed source"):
                    read_committed(root)


if __name__ == "__main__":
    unittest.main()
