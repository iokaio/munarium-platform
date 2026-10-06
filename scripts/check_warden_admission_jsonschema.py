#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optional independent Draft 2020-12 comparison; requires installed jsonschema."""
from jsonschema import Draft202012Validator

from test_warden_admission import SCHEMA, VECTORS, record


def main():
    Draft202012Validator.check_schema(SCHEMA)
    examples = {
        "provider_binding": VECTORS["bases"]["mapping"]["bindings"][0],
        "delegation_registration": VECTORS["bases"]["delegation"]["registrations"][0],
        "forwarded_attribution": VECTORS["bases"]["forwarding"]["record"],
    }
    count = 0
    for name, example in examples.items():
        standard = Draft202012Validator({**SCHEMA, "$ref": "#/$defs/" + name})
        cases = [example, {**example, "active": True}, {**example, "schema_version": True}]
        cases.extend({key: item for key, item in example.items() if key != missing}
                     for missing in example)
        for case in cases:
            try:
                record(name, case)
                portable = True
            except ValueError:
                portable = False
            if portable != standard.is_valid(case):
                raise AssertionError(f"validator disagreement: {name}")
            count += 1
    print(f"Draft 2020-12 meta-validation passed; {count} comparisons agreed")


if __name__ == "__main__":
    main()
