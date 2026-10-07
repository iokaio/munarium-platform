#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent Draft 2020-12 shape comparison; semantic cases remain separate."""
from importlib.metadata import version

from jsonschema import Draft202012Validator

from test_stage2_candidate import changed, load


def main():
    schema, _, vectors = load()
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    count = 0
    for name, value in vectors["records"].items():
        validator.validate(value)
        count += 1
        for field in value:
            missing = dict(value)
            del missing[field]
            if validator.is_valid(missing):
                raise ValueError("required field accepted: " + name + "/" + field)
            count += 1
    for case in vectors["cases"]:
        value = changed(vectors["records"][case["record"]], case["changes"])
        if validator.is_valid(value) != (case["expected"] != "InvalidShape"):
            raise ValueError("shape oracle disagreement: " + case["id"])
        count += 1
    print(f"jsonschema {version('jsonschema')}: {count} shape comparisons passed; not semantic/runtime conformance.")


if __name__ == "__main__":
    main()
