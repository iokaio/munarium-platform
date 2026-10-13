#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent Draft 2020-12 comparison; not runtime or authentication coverage."""
import json
from importlib.metadata import version

from jsonschema import Draft202012Validator
from test_journal_candidate import DIRECTORY
from test_stage2_candidate import changed


def main():
    schema, vectors = [json.loads((DIRECTORY / n).read_text()) for n in ("schema.json", "vectors.json")]
    Draft202012Validator.check_schema(schema)
    validator, count = Draft202012Validator(schema), 0
    for name, value in vectors["records"].items():
        validator.validate(value)
        count += 1
        for field in value:
            missing = dict(value)
            del missing[field]
            if validator.is_valid(missing):
                raise ValueError("required field accepted: " + name + "/" + field)
            count += 1
        if validator.is_valid(dict(value, send_permitted=True)):
            raise ValueError("extra authority accepted: " + name)
        count += 1
    for case in vectors["cases"]:
        value = changed(vectors["records"][case["record"]], case["changes"])
        if validator.is_valid(value) != (case["expected"] != "InvalidShape"):
            raise ValueError("shape oracle disagreement: " + case["id"])
        count += 1
    print(f"jsonschema {version('jsonschema')}: {count} journal shape comparisons passed; semantic checks are separate.")


if __name__ == "__main__":
    main()
