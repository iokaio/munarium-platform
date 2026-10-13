#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Closed-wire, complete-row, conservative-custody and committed-export controls."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from journal_contract import JournalOracle
from stage2_contract import digest, encoded
from test_stage2_candidate import changed
from vendor_journal import RELATIVE
from vendor_stage2 import read_committed, verify_lock, write_export

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / RELATIVE
PROFILE = "stage2-journal-checkpoint-v1"


class JournalCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema, cls.profile, cls.vectors = [json.loads((DIRECTORY / n).read_text())
            for n in ("schema.json", "profile.json", "vectors.json")]
        cls.oracle = JournalOracle(cls.schema, cls.profile)
        cls.records = cls.vectors["records"]

    def trusted(self, kind="journal-intent"):
        r = self.records
        trusted = {"scope": r["enrollment"]["journal"]["scope"], "enrollment": r["enrollment"],
            "audit": r["enrollment"]["audit"], "sequence": 0, "checkpoint": digest("journal-enrollment", r["enrollment"]),
            "rows": [], "pending": None, "authorized": True, "service": r["enrollment"]["owner"],
            "readers": r["policy"]["readers"], "receipt": r["receipt"]}
        if kind == "journal-commit":
            trusted["pending"] = r["intent"]
        if kind in {"journal-head", "journal-receipt", "journal-policy"}:
            trusted.update(service="fixture-reader", sequence=1,
                checkpoint=digest("journal-commit", r["commit"]),
                rows=self.oracle.replay([], r["commit"]["delta"], trusted["scope"]))
        return trusted

    def test_fixed_bytes_digests_and_refusals(self):
        for name, value in self.records.items():
            with self.subTest(record=name):
                trusted = self.trusted(value["type"])
                self.oracle.verify(value, trusted)
                self.assertEqual(encoded(value).decode(), self.vectors["canonical"][name])
                self.assertEqual(digest(value["type"], value), self.vectors["digests"][name])
                self.assertEqual(self.oracle.wire(encoded(value), trusted), value)
        for case in self.vectors["cases"]:
            with self.subTest(case=case["id"]):
                value = changed(self.records[case["record"]], case["changes"])
                with self.assertRaisesRegex(ValueError, "^" + case["expected"] + "$"):
                    self.oracle.verify(value, self.trusted())

    def test_closed_shapes_and_ambiguous_wire(self):
        for value in self.records.values():
            for field in value:
                missing = dict(value)
                del missing[field]
                with self.assertRaisesRegex(ValueError, "InvalidShape"):
                    self.oracle.verify(missing, self.trusted(value["type"]))
            with self.assertRaisesRegex(ValueError, "InvalidShape"):
                self.oracle.verify(dict(value, send_permitted=True), self.trusted(value["type"]))
        raw = encoded(self.records["intent"])
        for bad in (b" " + raw, raw + b"\n", b'\xef\xbb\xbf' + raw,
                    b'{"sequence":1,' + raw[1:], raw.replace(b'"sequence":1', b'"sequence":true'),
                    raw.replace(b'"sequence":1', b'"sequence":1.0'), b'{"x":"' + b'x' * 65536 + b'"}'):
            with self.assertRaises(ValueError):
                self.oracle.wire(bad, self.trusted())

    def test_all_table_columns_keys_and_immutable_history(self):
        self.assertEqual(len(self.profile["tables"]), 14)
        for name, table in self.profile["tables"].items():
            node = self.schema["$defs"][name + "-row"]
            self.assertEqual(set(table["columns"]), set(node["required"]))
            self.assertFalse(node["additionalProperties"])
            self.assertTrue(set(table["keys"]) <= set(table["columns"]))
            def sample(column):
                if "anyOf" in column:
                    return None
                if column["type"] == "boolean":
                    return False
                if column["type"] == "integer":
                    return max(1, column.get("minimum", 0))
                return "sha256:" + "1" * 64 if column.get("maxLength") == 71 else "{}"
            row = {k: sample(v) for k, v in table["columns"].items()}
            row["scope"] = encoded(self.trusted()["scope"]).decode()
            key = {k: row[k] for k in table["keys"]}
            self.oracle.row(name, key, row, self.trusted()["scope"])
            for column in row:
                incomplete = dict(row)
                del incomplete[column]
                with self.assertRaisesRegex(ValueError, "InvalidShape"):
                    self.oracle.row(name, key, incomplete, self.trusted()["scope"])
            with self.assertRaisesRegex(ValueError, "InvalidShape"):
                self.oracle.row(name, key, dict(row, uncovered_column=True), self.trusted()["scope"])
            omitted = copy.deepcopy(self.profile)
            del omitted["tables"][name]
            weakened = JournalOracle(self.schema, omitted)
            self.assertNotEqual(weakened.state_digest([], self.trusted()["scope"]),
                                self.records["enrollment"]["initial_state_digest"])
        delta = self.records["intent"]["proposed_delta"]
        for bad in (delta * 2, changed(delta, {"0.after.epoch": True}),
                    changed(delta, {"0.after.scope": "{}"}), changed(delta, {"0.after": None})):
            with self.assertRaises(ValueError):
                self.oracle.replay([], bad, self.trusted()["scope"])
        rows = self.oracle.replay([], delta, self.trusted()["scope"])
        no_op = changed(delta, {"0.before": delta[0]["after"]})
        with self.assertRaisesRegex(ValueError, "InvalidBinding"):
            self.oracle.replay(rows, no_op, self.trusted()["scope"])
        mutation = changed(no_op, {"0.after.initial_epoch": 2})
        with self.assertRaisesRegex(ValueError, "InvalidBinding"):
            self.oracle.replay(rows, mutation, self.trusted()["scope"])

    def test_pending_intent_conflict_and_current_admission(self):
        intent = self.records["intent"]
        trusted = dict(self.trusted(), pending=intent)
        self.oracle.verify(intent, trusted)
        with self.assertRaisesRegex(ValueError, "InvalidSequence"):
            self.oracle.verify(dict(intent, sequence=2), trusted)
        for change in ({"authorized": False}, {"service": "other-owner"}):
            with self.assertRaisesRegex(ValueError, "Unauthorized"):
                self.oracle.verify(intent, dict(trusted, **change))
        with self.assertRaisesRegex(ValueError, "InvalidSequence"):
            self.oracle.verify(self.records["commit"], self.trusted())
        commit = changed(self.records["commit"], {"delta.0.after.paused": False})
        with self.assertRaisesRegex(ValueError, "InvalidBinding"):
            self.oracle.verify(commit, self.trusted("journal-commit"))
        for record in ("receipt", "head"):
            value = changed(self.records[record], {"source_generation": 2})
            with self.assertRaisesRegex(ValueError, "Unauthorized"):
                self.oracle.verify(value, self.trusted(value["type"]))
        for trusted in (dict(self.trusted("journal-head"), readers=[]),
                        dict(self.trusted("journal-head"), authorized=False)):
            with self.assertRaisesRegex(ValueError, "Unauthorized"):
                self.oracle.verify(self.records["head"], trusted)
        with self.assertRaisesRegex(ValueError, "InvalidBinding"):
            self.oracle.verify(dict(self.records["receipt"], received_at=1001), self.trusted("journal-receipt"))

    def consumption_fixture(self):
        actions = json.loads((ROOT / "docs/decisions/stage2-v1/vectors.json").read_text())["records"]
        scope = self.trusted()["scope"]
        consume, send = actions["consumption-reserved"], actions["send-intent"]
        p = consume["payload"]
        second = copy.deepcopy(p["reservations"][0])
        second["reservation"]["id"] = "policy-reservation"
        p["reservations"].append(second)
        consume["payload_digest"] = digest("event-payload", p)
        target = p["reservations"][0]["target"]
        consumption = {"binding": {"grant_event": actions["grant-issued"], "grant_ack": actions["ack"],
                                        "worker": p["worker"], "limits": {"admission": 3}},
            "consumption": consume, "predispatch": actions["predispatch"], "execution_enabled": False}
        sql_scope, operation = encoded(scope).decode(), p["operation"]["id"]
        before = {"scope": sql_scope, "operation": operation, "binding": "{}",
                      "claim": encoded(actions["claim-created"]).decode(), "consumption": None}
        claim = dict(before, consumption=encoded(consumption).decode())
        grant = {"scope": sql_scope, "operation": operation, "grant_id": p["grant"]["id"]}
        reservation = {"scope": sql_scope, "operation": operation, "bucket": "target:" + encoded(target).decode(),
                           "window_start": p["reservations"][0]["window_start"], "unresolved": True}
        policy_reservation = dict(reservation, bucket="policy:admission")
        def entry(table, row):
            return {"table": table, "key": {k: row[k] for k in self.profile["tables"][table]["keys"]}, "row": row}
        rows = [entry("gate_action_claims", before)]
        delta = [{"table": e["table"], "key": e["key"], "before": before if e["table"] == "gate_action_claims" else None,
                      "after": e["row"]} for e in (entry("gate_action_claims", claim),
                      entry("gate_action_grants", grant), entry("gate_action_reservations", policy_reservation),
                      entry("gate_action_reservations", reservation))]
        exposure = {"operation": p["operation"], "attempt": p["attempt"], "target": target, "grant": p["grant"],
            "worker": p["worker"], "worker_fence": p["worker_fence"], "invocation": None, "send_spent": False,
            "buckets": [{"bucket": policy_reservation["bucket"], "window_start": reservation["window_start"], "units": 1, "limit": 3},
                     {"bucket": reservation["bucket"], "window_start": reservation["window_start"], "units": 1, "limit": 2}]}
        intent = dict(self.records["intent"], proposed_delta=delta, mutation_kinds=["consume"],
            operations=[{"operation": p["operation"], "attempt": p["attempt"]}], exposure=[exposure])
        after = self.oracle.replay(rows, delta, scope)
        intent.update(before_state_digest=self.oracle.state_digest(rows, scope),
                      after_state_digest=self.oracle.state_digest(after, scope), delta_digest=digest("journal-delta", {"rows": delta}))
        return intent, dict(self.trusted(), rows=rows), after, send, entry

    def test_consumption_and_send_custody_cannot_omit_exposure(self):
        intent, trusted, rows, send, entry = self.consumption_fixture()
        self.oracle.verify(intent, trusted)
        for changes in ({"exposure": []}, {"exposure.0.buckets": []}, {"exposure.0.worker": "other-worker"},
                        {"exposure.0.buckets.0.limit": 4}, {"operations": []}, {"mutation_kinds": ["claim"]},
                        {"exposure.0.buckets": intent["exposure"][0]["buckets"][:1]}):
            with self.assertRaises(ValueError):
                self.oracle.verify(changed(intent, changes), trusted)
        orphan_delta = intent["proposed_delta"][1:]
        orphan_rows = self.oracle.replay(trusted["rows"], orphan_delta, trusted["scope"])
        orphan = dict(intent, proposed_delta=orphan_delta, exposure=[], operations=[],
            after_state_digest=self.oracle.state_digest(orphan_rows, trusted["scope"]),
            delta_digest=digest("journal-delta", {"rows": orphan_delta}))
        with self.assertRaisesRegex(ValueError, "InvalidBinding"):
            self.oracle.verify(orphan, trusted)
        released_delta = changed(intent["proposed_delta"], {"2.after.unresolved": False})
        released_rows = self.oracle.replay(trusted["rows"], released_delta, trusted["scope"])
        released = dict(intent, proposed_delta=released_delta,
            after_state_digest=self.oracle.state_digest(released_rows, trusted["scope"]),
            delta_digest=digest("journal-delta", {"rows": released_delta}))
        with self.assertRaisesRegex(ValueError, "InvalidBinding"):
            self.oracle.verify(released, trusted)
        dispatch = entry("gate_action_dispatch", {"scope": encoded(trusted["scope"]).decode(),
            "operation": send["payload"]["operation"]["id"], "admission": encoded(send).decode(), "outcome": None})
        delta = [{"table": dispatch["table"], "key": dispatch["key"], "before": None, "after": dispatch["row"]}]
        footprint = dict(intent["exposure"][0], invocation=send["payload"]["invocation"], send_spent=True)
        send_intent = dict(intent, proposed_delta=delta, mutation_kinds=["send"], exposure=[footprint],
            before_state_digest=self.oracle.state_digest(rows, trusted["scope"]),
            after_state_digest=self.oracle.state_digest(self.oracle.replay(rows, delta, trusted["scope"]), trusted["scope"]),
            delta_digest=digest("journal-delta", {"rows": delta}))
        self.oracle.verify(send_intent, dict(trusted, rows=rows))
        for changes in ({"exposure.0.send_spent": False}, {"exposure.0.invocation": None}):
            with self.assertRaisesRegex(ValueError, "InvalidBinding"):
                self.oracle.verify(changed(send_intent, changes), dict(trusted, rows=rows))
        outbox = entry("gate_action_outbox", {"scope": encoded(trusted["scope"]).decode(),
                      "sequence": 1, "event": encoded(send).decode(), "acknowledgement": None})
        missing_send = [{"table": outbox["table"], "key": outbox["key"], "before": None, "after": outbox["row"]}]
        unsupported = dict(send_intent, proposed_delta=missing_send, exposure=[],
            after_state_digest=self.oracle.state_digest(self.oracle.replay(rows, missing_send, trusted["scope"]), trusted["scope"]),
            delta_digest=digest("journal-delta", {"rows": missing_send}))
        with self.assertRaisesRegex(ValueError, "InvalidBinding"):
            self.oracle.verify(unsupported, dict(trusted, rows=rows))

    def test_state_streaming_bounds_and_order(self):
        trusted = self.trusted()
        self.assertEqual(self.oracle.state_digest([], trusted["scope"]), self.records["enrollment"]["initial_state_digest"])
        rows = self.oracle.replay([], self.records["commit"]["delta"], trusted["scope"])
        self.assertEqual(self.oracle.state_digest(rows, trusted["scope"]), self.records["commit"]["after_state_digest"])
        with self.assertRaises(ValueError):
            self.oracle.state_digest(rows * 2, trusted["scope"])
        rows = [{"table": "gate_action_sources", "key": {"scope": encoded(trusted["scope"]).decode(), "operation": f"op-{i:04}"},
                     "row": {"scope": encoded(trusted["scope"]).decode(), "operation": f"op-{i:04}",
                              "source": encoded({"payload": "x" * 1024}).decode()}} for i in range(100)]
        self.assertGreater(len(json.dumps(rows).encode()), 65536)
        original = self.oracle.state_digest(rows, trusted["scope"])
        rows[-1]["row"]["source"] = "{}"
        self.assertNotEqual(self.oracle.state_digest(rows, trusted["scope"]), original)
        with self.assertRaises(ValueError):
            self.oracle.state_digest(list(reversed(rows)), trusted["scope"])

    def test_reproduction_lock_and_export_controls(self):
        subprocess.run([sys.executable, str(ROOT / "scripts/generate_journal_candidate.py"), "--check"], check=True, capture_output=True)
        files = {p.name: p.read_bytes().replace(b"\r\n", b"\n") for p in DIRECTORY.iterdir() if p.is_file()}
        refused = subprocess.run([sys.executable, str(ROOT / "scripts/generate_journal_candidate.py")], check=False, capture_output=True)
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(files, {p.name: p.read_bytes().replace(b"\r\n", b"\n") for p in DIRECTORY.iterdir() if p.is_file()})
        lock = verify_lock(files, PROFILE)
        with self.assertRaises(ValueError):
            verify_lock(files)  # action profile cannot accept journal bytes
        changed_files = dict(files, **{"schema.json": files["schema.json"] + b" "})
        with self.assertRaises(ValueError):
            verify_lock(changed_files, PROFILE)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / RELATIVE
            source.mkdir(parents=True)
            for name, raw in files.items():
                (source / name).write_bytes(raw)
            git = ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root)]
            for args in (["init", "-q"], ["add", "."], ["-c", "user.name=Fixture Contributor",
                         "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture"]):
                subprocess.run(git + args, check=True, capture_output=True)
            contents = read_committed(root, RELATIVE, PROFILE)
            self.assertEqual(json.loads(contents["vendor-lock.json"])["bundle_sha256"], lock["bundle_sha256"])
            destination = root / "consumer"
            write_export(contents, destination)
            write_export(contents, destination)
            (destination / "schema.json").write_bytes(b"different")
            with self.assertRaises(ValueError):
                write_export(contents, destination)
            self.assertEqual((destination / "schema.json").read_bytes(), b"different")
            collision = root / "collision"
            collision.mkdir()
            (collision / "vectors.json").write_bytes(b"different")
            with self.assertRaises(ValueError):
                write_export(contents, collision)
            self.assertEqual([p.name for p in collision.iterdir()], ["vectors.json"])
            (source / "schema.json").write_bytes(files["schema.json"] + b" ")
            with self.assertRaisesRegex(ValueError, "differs from committed"):
                read_committed(root, RELATIVE, PROFILE)


if __name__ == "__main__":
    unittest.main()
