#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optional independent Draft 2020-12 validation; requires jsonschema."""
import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1] / "docs/decisions/registry-v2"
records = json.loads((ROOT / "registry.schema.json").read_text())
capability = json.loads((ROOT / "capability.schema.json").read_text())
Draft202012Validator.check_schema(records)
Draft202012Validator.check_schema(capability)
trust = json.loads((ROOT / "trust.json").read_text())
count = 0
for kind, value in [("trust", trust)] + [
    ("manifest", json.loads(c["payload"]))
    for c in json.loads((ROOT / "signed-vectors.json").read_text())["cases"]
    if c["expected"] == "accept"
]:
    validator = Draft202012Validator({"$defs": records["$defs"], "$ref": "#/$defs/" + kind})
    validator.validate(value)
    count += 1
    for name in value:
        missing = copy.deepcopy(value)
        del missing[name]
        assert not validator.is_valid(missing), (kind, name)
        count += 1
    assert not validator.is_valid({**value, "unknown": True})
    count += 1
for tenant in trust["tenants"]:
    for record in tenant["schemas"]:
        Draft202012Validator(capability).validate(json.loads(record["canonical"]))
        count += 1
print(f"Two schema documents meta-valid; {count} positive/negative shape checks passed")
