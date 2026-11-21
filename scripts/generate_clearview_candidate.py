#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generate a locked candidate for the approved ClearView C2 and MCP refinements."""
import argparse
import hashlib
import json
from pathlib import Path

from vendor_stage2 import ROOT

RELATIVE = Path("docs/decisions/clearview-c2-mcp-v1")
DIRECTORY = ROOT / RELATIVE
PROFILE = "clearview-c2-mcp-v1"
SOURCE = "67e368d88cd3275acdb71d91635cc40f336de718"
STATUS = "candidate-not-accepted-not-released"
GENERIC_FAILURE = "build job failed; no classified cause was recorded for this failure"
FAILURES = {
    "attempts_exhausted": "build job failed: its final attempt stopped renewing its lease before completing",
    "invalid_input": "build job failed: the build refused the job's target or parameters",
    "not_found": "build job failed: something the job names no longer exists",
    "storage_error": "build job failed: a storage error occurred; see the server log",
    "datastore_unavailable": "build job failed: a datastore artifact could not be read or written",
    "provider_error": "build job failed: an upstream model provider call failed",
    "artifact_blocked": "build job failed: its result is an artifact blocked by artifact damage; repair is required",
    "extraction_deferred": "build job failed: isolated PDF extraction was deferred; retry when extraction capacity returns",
}
UINT = {"type": "integer", "minimum": 0, "maximum": 2**64 - 1}
NONBLANK = {"type": "string", "pattern": r"\S"}
REFUSAL = "mcp-generation-not-authorized"
EXHAUSTED = "mcp-allowance-exhausted"


def closed(properties, *required):
    return {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }


def array(items):
    return {"type": "array", "items": items}


def schema():
    pair = {"request_tokens": UINT, "daily_tokens": UINT}
    override = closed(
        {"index_version": {"type": "string"}, **pair},
        "index_version", "request_tokens", "daily_tokens",
    )
    entry = closed(
        {
            "tenant": NONBLANK,
            "collection": NONBLANK,
            "budget_owner": {"type": ["string", "null"]},
            "request_tokens": {**UINT, "type": ["integer", "null"]},
            "daily_tokens": {**UINT, "type": ["integer", "null"]},
            "indexes": array(override),
        },
        "tenant", "collection",
    )
    policy = closed(
        {
            "version": {"const": 1},
            "collections": array(entry),
            "model_bytes_per_token": {
                "type": "object",
                "propertyNames": NONBLANK,
                "additionalProperties": {**UINT, "minimum": 1},
            },
        },
        "version",
    )
    failure = closed(
        {
            "state": {"enum": ["pending", "running", "succeeded", "failed", "cancelled", "superseded"]},
            "error": {"type": "string"},
            "error_code": {"type": "string", "pattern": "^[a-z][a-z0-9_]{0,63}$"},
        },
        "state",
    )
    failure["dependentRequired"] = {"error_code": ["error"]}
    failure["if"] = {"properties": {"state": {"const": "failed"}}}
    failure["else"] = {"not": {"anyOf": [{"required": ["error"]}, {"required": ["error_code"]}]}}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": {"generation-policy": policy, "build-job-failure": failure},
    }


def profile():
    return {
        "profile": PROFILE,
        "version": 1,
        "status": STATUS,
        "server_source": SOURCE,
        "decisions": ["0022", "0026"],
        "job_failure": {
            "codes": FAILURES,
            "unclassified_message": GENERIC_FAILURE,
            "extraction_deferred": {
                "problem": "extraction-deferred",
                "http_status": 429,
                "grpc_status": "RESOURCE_EXHAUSTED",
                "retryable": False,
                "retry_action": "retry_later",
            },
        },
        "generation": {
            "setting": "MUNARIUM_MCP_GENERATION_POLICY",
            "policy_version": 1,
            "default_bytes_per_token": 3,
            "framing_tokens": 64,
            "estimate": "ceil(serialized_request_and_schema_bytes / model_bytes_per_token) + framing_tokens + effective_max_tokens",
            "configuration_digest": "sha256 of exact startup bytes, lowercase hex",
            "fleet_guard": "live self heartbeat and agreement across the observed deployment environment",
            "request_limit": "largest effective allowance of the authorized contributors",
            "daily_limits": "all contributing collections and each applicable index override, deduplicated, per UTC day",
            "settlement": "charge reliable actual usage once and record and meter excess; preserve the reservation for uncertain usage",
        },
    }


def fixtures():
    legal = {
        "tenant": "fixture",
        "collection": "legal",
        "budget_owner": "shared",
        "request_tokens": 2000,
        "daily_tokens": 9000,
        "indexes": [{"index_version": "i-legal", "request_tokens": 3000, "daily_tokens": 4000}],
    }
    finance = {**legal, "collection": "finance", "request_tokens": 8000, "indexes": []}
    policy = {"version": 1, "collections": [legal, finance], "model_bytes_per_token": {"fixture-model": 4}}
    shape_cases = [
        {"id": name, "definition": "generation-policy", "value": value, "valid": valid}
        for name, value, valid in (
            ("empty-policy", {"version": 1}, True),
            ("indexed-allowance", policy, True),
            ("incomplete-collection-is-disabled", {"version": 1, "collections": [
                {"tenant": "fixture", "collection": "draft", "request_tokens": None}
            ]}, True),
            ("incomplete-index-override", {"version": 1, "collections": [
                {**legal, "indexes": [{"index_version": "i-legal", "request_tokens": 3000}]}
            ]}, False),
            ("zero-ratio", {**policy, "model_bytes_per_token": {"fixture-model": 0}}, False),
            ("unknown-policy-version", {**policy, "version": 2}, False),
            ("unknown-policy-member", {**policy, "actor": "fixture"}, False),
        )
    ]
    shape_cases += [
        {"id": code, "definition": "build-job-failure",
         "value": {"state": "failed", "error": message, "error_code": code}, "valid": True}
        for code, message in FAILURES.items()
    ]
    shape_cases += [
        {"id": name, "definition": "build-job-failure", "value": value, "valid": valid}
        for name, value, valid in (
            ("historical-failure", {"state": "failed", "error": GENERIC_FAILURE}, True),
            ("success-omits-failure", {"state": "succeeded"}, True),
            ("null-code-is-not-omission", {"state": "failed", "error": GENERIC_FAILURE, "error_code": None}, False),
            ("code-without-message", {"state": "failed", "error_code": "extraction_deferred"}, False),
            ("success-cannot-have-a-code", {"state": "succeeded", "error": GENERIC_FAILURE, "error_code": "storage_error"}, False),
        )
    ]
    local = "a" * 64
    peer = "b" * 64
    attempt = {"bytes": 7, "max_tokens": 16, "request_remaining": 100, "daily_remaining": [100, 80],
               "digests": [local, local], "has_self": True, "policy_digest": local, "payer": ["shared", "shared"]}
    attempt_cases = [
        {"id": name, "input": {**attempt, **update}, "expected": expected}
        for name, update, expected in (
            ("default-ratio-rounds-up", {}, {"estimated": 83, "refusal": EXHAUSTED}),
            ("all-balances-cover-attempt", {"daily_remaining": [100, 83]}, {"estimated": 83, "charged": 83, "excess": 0}),
            ("per-model-ratio", {"ratio": 4, "daily_remaining": [100, 82]}, {"estimated": 82, "charged": 82, "excess": 0}),
            ("request-ceiling-refusal", {"request_remaining": 82, "daily_remaining": [100]}, {"estimated": 83, "refusal": EXHAUSTED}),
            ("fleet-divergence", {"digests": [local, peer]}, {"refusal": REFUSAL}),
            ("fleet-missing-self", {"has_self": False}, {"refusal": REFUSAL}),
            ("fleet-missing-policy", {"digests": [local, None]}, {"refusal": REFUSAL}),
            ("mixed-payers", {"payer": ["legal", "finance"]}, {"refusal": REFUSAL}),
            ("settle-actual-above-estimate", {"actual": 101, "daily_remaining": [100, 100]}, {"estimated": 83, "charged": 101, "excess": 18}),
            ("settle-reliable-lower-usage", {"actual": 70, "daily_remaining": [100, 100]}, {"estimated": 83, "charged": 70, "excess": 0}),
            ("uncertain-holds-reservation", {"actual": None, "daily_remaining": [100, 100]}, {"estimated": 83, "charged": 83, "excess": 0}),
            ("later-attempt-refused-after-excess", {"request_remaining": 0, "daily_remaining": [100]}, {"estimated": 83, "refusal": EXHAUSTED}),
        )
    ]
    return {"version": 1, "shape_cases": shape_cases, "attempt_cases": attempt_cases}


def pretty(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def generated_files(readme):
    contents = {
        "README.md": readme.replace(b"\r\n", b"\n"),
        "schema.json": pretty(schema()),
        "profile.json": pretty(profile()),
        "vectors.json": pretty(fixtures()),
    }
    hashes = {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(contents.items())}
    aggregate = "".join(name + "\0" + value + "\n" for name, value in hashes.items()).encode()
    contents["bundle-lock.json"] = pretty({
        "status": STATUS, "profile": PROFILE, "files": hashes,
        "bundle_sha256": hashlib.sha256(aggregate).hexdigest(),
    })
    return contents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contents = generated_files((DIRECTORY / "README.md").read_bytes())
    if args.check:
        for name, raw in contents.items():
            if (DIRECTORY / name).read_bytes().replace(b"\r\n", b"\n") != raw:
                raise SystemExit("ClearView candidate differs from generator: " + name)
        print("ClearView reproducible candidate conforms to its bundle lock.")
        return
    artifacts = {name: raw for name, raw in contents.items() if name != "README.md"}
    if any((DIRECTORY / name).exists() for name in artifacts):
        raise SystemExit("refusing to overwrite an existing candidate artifact")
    for name, raw in artifacts.items():
        (DIRECTORY / name).write_bytes(raw)


if __name__ == "__main__":
    main()
