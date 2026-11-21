#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate the actual ClearView candidate's shape vectors with Draft 2020-12."""
import json

from jsonschema import Draft202012Validator

from generate_clearview_candidate import DIRECTORY


def main():
    schema = json.loads((DIRECTORY / "schema.json").read_bytes())
    vectors = json.loads((DIRECTORY / "vectors.json").read_bytes())
    Draft202012Validator.check_schema(schema)
    for case in vectors["shape_cases"]:
        validator = Draft202012Validator({
            **schema, "$ref": "#/$defs/" + case["definition"],
        })
        if validator.is_valid(case["value"]) != case["valid"]:
            raise SystemExit("ClearView shape vector mismatch: " + case["id"])
    print(f"{len(vectors['shape_cases'])} ClearView shape vectors passed.")


if __name__ == "__main__":
    main()
