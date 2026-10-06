#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Candidate schema/signature semantics; no service, persistence or authority claim."""
import copy
import hashlib
import json
import unittest

from candidate_contract import (FIXTURES, SCHEMA, check_schema, openssl_path,
                                record_digest, validate, validate_record, verify_ack, verify_chain)


class CandidateContract(unittest.TestCase):
    def test_declared_schema_vocabulary(self):
        check_schema(SCHEMA)
        with self.assertRaises(ValueError):
            check_schema({"type": "object", "ignoredConstraint": True})
        with self.assertRaises(ValueError):
            check_schema({"anyOf": [{"type": "integer"}], "maximum": 1})

    def test_signed_vectors(self):
        vectors = json.loads((FIXTURES / "identity-vectors.json").read_text(encoding="utf-8"))
        executable = openssl_path()  # Missing verification is a failure, never a skipped pass.
        for case in vectors["cases"]:
            with self.subTest(case=case["id"]):
                if case["expected"] == "accept":
                    verify_chain(case["tokens"], case["context"], vectors["keys"], executable)
                else:
                    with self.assertRaises(ValueError):
                        verify_chain(case["tokens"], case["context"], vectors["keys"], executable)

    def test_closed_record_shapes(self):
        examples = json.loads((FIXTURES / "record-vectors.json").read_text(encoding="utf-8"))["examples"]
        for name, value in examples.items():
            with self.subTest(record=name):
                validate_record(name, value)
                for key in value:
                    missing = copy.deepcopy(value)
                    del missing[key]
                    with self.assertRaises(ValueError, msg=key):
                        validate_record(name, missing)
                with self.assertRaises(ValueError):
                    validate_record(name, {**value, "unexpected": True})
                with self.assertRaises(ValueError):
                    validate_record(name, {**value, "schema_version": True})

    def test_scalar_and_collection_constraints(self):
        cases = [({"type": "integer", "minimum": 0, "maximum": 3}, [True, -1, 4, 1.5]),
                 ({"type": "string", "pattern": "^a+$", "minLength": 1, "maxLength": 2}, ["", "b", "aaa"]),
                 ({"type": "array", "items": {"type": "integer"}, "minItems": 1, "maxItems": 2, "uniqueItems": True}, [[], [1, 1], [1, 2, 3], [False]])]
        for schema, values in cases:
            for value in values:
                with self.subTest(schema=schema, value=value), self.assertRaises(ValueError):
                    validate(value, schema)

    def test_cross_record_refusals(self):
        examples = json.loads((FIXTURES / "record-vectors.json").read_text(encoding="utf-8"))["examples"]
        event, ack = examples["event"], examples["ack"]
        verify_ack(event, ack)
        for key, value in [("tenant", "other"), ("event_id", "other"), ("payload_digest", "sha256:" + "f" * 64),
                           ("event_digest", "sha256:" + "f" * 64)]:
            with self.subTest(ack=key), self.assertRaises(ValueError):
                verify_ack(event, {**ack, key: value})
        bad = copy.deepcopy(event)
        bad["payload"]["reasons"] = ["changed"]
        with self.assertRaises(ValueError):
            validate_record("event", bad)
        for patch in ({"kind": "proposal"}, {"sequence": 2}, {"kind": "dispatch"}, {"operation_id": "other"}):
            with self.assertRaises(ValueError):
                validate_record("event", {**event, **patch})
        with self.assertRaises(ValueError):
            validate_record("decision", {**examples["decision"], "outcome": "decision-only-allow"})
        with self.assertRaises(ValueError):
            validate_record("lineage", {**examples["lineage"], "trust": "verified"})
        with self.assertRaises(ValueError):
            validate_record("manifest", {**examples["manifest"], "base_consequence": "C2", "modifiers": [dict(field_path="amount", predicate_digest="sha256:" + "a" * 64, raise_to="C1")]})
        with self.assertRaises(ValueError):
            validate_record("request", {**examples["request"], "attachments": [dict(digest="sha256:" + "a" * 64, media_type="text/plain", bytes=600000)] * 2})
        proposal = {**event, "kind": "proposal", "payload": examples["request"],
                    "payload_digest": record_digest("decision-event-payload", examples["request"])}
        validate_record("event", proposal)
        with self.assertRaises(ValueError):
            validate_record("event", {**proposal, "operation_id": "other"})

    def test_candidate_bundle(self):
        lock = json.loads((FIXTURES / "candidate-lock.json").read_text(encoding="utf-8"))
        lines = []
        for name, expected in sorted(lock["files"].items()):
            raw = (FIXTURES / name).read_bytes().replace(b"\r\n", b"\n")
            digest = hashlib.sha256(raw).hexdigest()
            self.assertEqual(expected, digest, name)
            lines.append(name + "\0" + digest + "\n")
        self.assertEqual(lock["bundle_sha256"], hashlib.sha256("".join(lines).encode()).hexdigest())


if __name__ == "__main__":
    unittest.main()
