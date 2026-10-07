#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent offline Registry candidate checks; no activation or service."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from candidate_contract import openssl_path, validate
from test_decision_json_vectors import canonical

ROOT = Path(__file__).resolve().parents[1] / "docs/decisions/registry-v2"
SCHEMA = json.loads((ROOT / "registry.schema.json").read_text())


def hash_bytes(domain, raw):
    return "sha256:" + hashlib.sha256(domain.encode() + b"\0" + raw).hexdigest()


def strict(raw, limit):
    if len(raw) > limit or canonical(raw) != raw:
        raise ValueError("InvalidArtifact")
    return json.loads(raw)


def decode(segment, limit):
    if not segment or len(segment) > ((limit + 2) // 3) * 4:
        raise ValueError("InvalidArtifact")
    raw = base64.b64decode(segment + "=" * ((-len(segment)) % 4), altchars=b"-_", validate=True)
    if len(raw) > limit or base64.urlsafe_b64encode(raw).decode().rstrip("=") != segment:
        raise ValueError("InvalidArtifact")
    return raw


def verify(case, trust, openssl):
    # Select trusted context before considering any payload-selected namespace.
    tenant = next(t for t in trust["tenants"] if t["id"] == case["tenant"])
    envelope = case["envelope"]
    try:
        raw = envelope.encode("ascii")
        if len(raw) > 90000:
            raise ValueError()
        h, p, s = envelope.split(".")
        head = strict(decode(h, 512), 512)
        validate(head, SCHEMA["$defs"]["header"])
        payload_bytes = decode(p, 65536)
        payload = strict(payload_bytes, 65536)
        signature = decode(s, 64)
        if len(signature) != 64:
            raise ValueError()
    except (ValueError, UnicodeError):
        raise ValueError("InvalidArtifact") from None
    try:
        validate(payload, SCHEMA["$defs"]["manifest"])
        if any(m["raise_to"] <= payload["base_consequence"] for m in payload["modifiers"]):
            raise ValueError()
    except ValueError:
        raise ValueError("InvalidManifest") from None
    if payload["tenant"] != case["tenant"]:
        raise ValueError("Unauthorized")
    publisher = next((p for p in tenant["publishers"]
                      if p["id"] == payload["publisher_id"] and p["kid"] == head["kid"] and p["enabled"]), None)
    if publisher is None:
        raise ValueError("UntrustedPublisher")
    with tempfile.TemporaryDirectory(prefix="registry-signature-") as directory:
        folder = Path(directory)
        public = decode(publisher["public_key"], 32)
        (folder / "public.der").write_bytes(bytes.fromhex("302a300506032b6570032100") + public)
        (folder / "signature").write_bytes(signature)
        (folder / "message").write_bytes((h + "." + p).encode())
        outcome = subprocess.run([openssl, "pkeyutl", "-verify", "-pubin", "-keyform", "DER",
                                  "-inkey", str(folder / "public.der"), "-rawin",
                                  "-in", str(folder / "message"), "-sigfile", str(folder / "signature")],
                                 capture_output=True, check=False)
        if outcome.returncode:
            raise ValueError("InvalidArtifact")
    if payload["owner_id"] not in publisher["owner_ids"] or not any(o["id"] == payload["owner_id"] for o in tenant["owners"]):
        raise ValueError("UntrustedPublisher")
    fields = ("target_id", "environment", "operation_id", "credential_audience", "capability_id",
              "parameter_schema_digest", "result_schema_digest")
    operation = next((o for o in tenant["operations"] if all(o[f] == payload[f] for f in fields)), None)
    if operation is None or any(c not in tenant["classifications"] for c in payload["data_classifications"]):
        raise ValueError("MissingReference")
    if operation not in publisher["operations"]:
        raise ValueError("UntrustedPublisher")
    return payload_bytes, hash_bytes("munarium:manifest:v2", payload_bytes), hash_bytes("munarium:manifest-artifact:v2", raw)


class RegistryCandidate(unittest.TestCase):
    def test_signed_artifact_vectors(self):
        vectors = json.loads((ROOT / "signed-vectors.json").read_text())
        trust = json.loads((ROOT / "trust.json").read_text())
        executable = openssl_path()
        self.assertEqual(len(vectors["cases"]), 32)
        for case in vectors["cases"]:
            with self.subTest(case=case["id"]):
                if case["expected"] == "accept":
                    raw, manifest, artifact = verify(case, trust, executable)
                    self.assertEqual(raw, case["payload"].encode())
                    self.assertEqual((manifest, artifact), (case["manifest_digest"], case["artifact_digest"]))
                else:
                    with self.assertRaisesRegex(ValueError, "^" + case["expected"] + "$"):
                        verify(case, trust, executable)

    def test_bundle_and_schema_references(self):
        lock = json.loads((ROOT / "bundle-lock.json").read_text())
        parts = []
        for name, expected in sorted(lock["files"].items()):
            self.assertEqual(Path(name).name, name)
            raw = (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
            observed = hashlib.sha256(raw).hexdigest()
            self.assertEqual(observed, expected, name)
            parts.append(name + "\0" + observed + "\n")
        self.assertEqual(hashlib.sha256("".join(parts).encode()).hexdigest(), lock["bundle_sha256"])
        trust = json.loads((ROOT / "trust.json").read_text())
        validate(trust, SCHEMA["$defs"]["trust"])
        for tenant in trust["tenants"]:
            refs = {}
            for record in tenant["schemas"]:
                raw = record["canonical"].encode()
                self.assertEqual(canonical(raw), raw)
                self.assertEqual(hash_bytes("munarium:capability-schema:v1", raw), record["digest"])
                refs[record["digest"]] = raw
            for op in tenant["operations"]:
                self.assertIn(op["parameter_schema_digest"], refs)
                self.assertIn(op["result_schema_digest"], refs)


if __name__ == "__main__":
    unittest.main()
