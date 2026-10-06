#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optional independent standards-validator comparison; requires jsonschema."""
import copy
import json

from jsonschema import Draft202012Validator

from candidate_contract import FIXTURES, SCHEMA, check_schema, validate


def main():
    Draft202012Validator.check_schema(SCHEMA)
    check_schema(SCHEMA)
    examples = json.loads((FIXTURES / "record-vectors.json").read_text(encoding="utf-8"))["examples"]
    count = 0
    for name, value in examples.items():
        standard = Draft202012Validator({**SCHEMA, "$ref": "#/$defs/" + name})
        cases = [value, {**value, "unexpected": True}]
        for key in value:
            missing = copy.deepcopy(value)
            del missing[key]
            cases.append(missing)
        for case in cases:
            try:
                validate(case, SCHEMA["$defs"][name])
                portable = True
            except ValueError:
                portable = False
            if portable != standard.is_valid(case):
                raise AssertionError(f"validator disagreement: {name}")
            count += 1
    print(f"Draft 2020-12 meta-validation passed; {count} comparisons agreed")


if __name__ == "__main__":
    main()
