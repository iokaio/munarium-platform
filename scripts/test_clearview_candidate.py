# SPDX-License-Identifier: Apache-2.0
"""Offline ClearView candidate checks for export integrity and allowance vectors."""
import json
import unittest

from generate_clearview_candidate import DIRECTORY, PROFILE, generated_files
from vendor_stage2 import verify_lock


def run_attempt(profile, request):
    # Reference arithmetic for an individual attempt from an authorized fixture.
    digest = request["policy_digest"]
    if (not request["has_self"] or not digest
            or set(request["digests"]) != {digest}
            or len(set(request["payer"])) != 1):
        return {"refusal": "mcp-generation-not-authorized"}
    rule = profile["generation"]
    ratio = request.get("ratio", rule["default_bytes_per_token"])
    quotient, remainder = divmod(request["bytes"], ratio)
    estimate = quotient + bool(remainder) + rule["framing_tokens"] + request["max_tokens"]
    if estimate > min(request["request_remaining"], *request["daily_remaining"]):
        return {"estimated": estimate, "refusal": "mcp-allowance-exhausted"}
    actual = request.get("actual")
    charge = estimate if actual is None else actual
    return {"estimated": estimate, "charged": charge, "excess": max(0, charge - estimate)}


class ClearViewCandidate(unittest.TestCase):
    def test_locked_bytes_reproduce_and_tampering_is_refused(self):
        expected = generated_files((DIRECTORY / "README.md").read_bytes())
        checked = {name: (DIRECTORY / name).read_bytes().replace(b"\r\n", b"\n") for name in expected}
        self.assertEqual(expected, checked)
        verify_lock(checked, PROFILE)
        for name in ("profile.json", "schema.json", "vectors.json"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                verify_lock({**checked, name: checked[name] + b" "}, PROFILE)

    def test_attempt_controls(self):
        fixtures = json.loads((DIRECTORY / "vectors.json").read_bytes())
        profile = json.loads((DIRECTORY / "profile.json").read_bytes())
        for vector in fixtures["attempt_cases"]:
            with self.subTest(id=vector["id"]):
                self.assertEqual(run_attempt(profile, vector["input"]), vector["expected"])

    def test_current_producer_messages_and_open_consumer_code(self):
        fixtures = json.loads((DIRECTORY / "vectors.json").read_bytes())
        profile = json.loads((DIRECTORY / "profile.json").read_bytes())
        expected = profile["job_failure"]["codes"]
        live = {
            case["value"]["error_code"]: case["value"]["error"]
            for case in fixtures["shape_cases"]
            if case["definition"] == "build-job-failure" and case["valid"]
            and "error_code" in case["value"]
        }
        self.assertEqual(live, expected)
        self.assertIn("extraction_deferred", live)
        self.assertNotIn("enum", json.loads((DIRECTORY / "schema.json").read_bytes())
                         ["$defs"]["build-job-failure"]["properties"]["error_code"])
