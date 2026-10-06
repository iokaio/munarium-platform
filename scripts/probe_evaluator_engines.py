# SPDX-License-Identifier: Apache-2.0
"""Reproduce synthetic native-engine edge cases; no service or authority is created."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cedar", type=Path, required=True)
    parser.add_argument("--opa", type=Path, required=True)
    args = parser.parse_args()
    pins = {"cedar": "02c5a18726edb0bfa4725076dbc4fd5d92adf8d1652916ecca40d2ff9f773549",
            "opa": "25406f7c6e147d687fd7fd546f835bafa160a6242c605ee94a23ba6cd7bccdcd"}
    for name, pin in pins.items():
        if hashlib.sha256(getattr(args, name).read_bytes()).hexdigest() != pin:
            raise ValueError(f"{name} binary digest mismatch")
    results = []
    with tempfile.TemporaryDirectory(prefix="munarium-evaluator-probe-") as directory:
        root = Path(directory)

        def write(name, content):
            (root / name).write_text(content, encoding="utf-8")

        def run(name, engine, command, expected_exit, contains):
            proc = subprocess.run([str(getattr(args, engine).resolve()), *command], cwd=root,
                                  capture_output=True, text=True, timeout=5, check=False)
            passed = proc.returncode == expected_exit and all(x in proc.stdout + proc.stderr for x in contains)
            results.append(dict(case=name, engine=engine, command=command, exit=proc.returncode,
                                stdout=proc.stdout, stderr=proc.stderr, passed=passed))
            if not passed:
                raise AssertionError(results[-1])

        write("entities.json", "[]")
        write("input.json", "{}")
        write("policy.cedar", "permit(principal, action, resource);\n"
              "permit(principal, action, resource) when { context.amount + 0 <= 10 };\n")
        entity = {"shape": {"type": "Record", "attributes": {}}}
        write("schema.json", json.dumps({"": {"entityTypes": {"User": entity, "Target": entity},
              "actions": {"evaluate": {"appliesTo": {"principalTypes": ["User"],
              "resourceTypes": ["Target"], "context": {"type": "Record", "attributes": {
              "amount": {"type": "Long", "required": True}}}}}}}}))
        cedar = ["authorize", "--principal", 'User::"alice"', "--action", 'Action::"evaluate"',
                 "--resource", 'Target::"example"', "--context", "input.json", "--entities",
                 "entities.json", "--policies", "policy.cedar", "--verbose", "--error-format", "json"]
        run("cedar-version", "cedar", ["--version"], 0, ["4.13.0"])
        run("cedar-mixed-allow-error", "cedar", cedar, 0, ["ALLOW", "amount"])
        run("cedar-policy-validation", "cedar", ["validate", "--schema", "schema.json", "--schema-format",
            "json", "--policies", "policy.cedar", "--deny-warnings", "--error-format", "json"], 0, [])
        run("cedar-missing-input-validation", "cedar", cedar + ["--schema", "schema.json", "--schema-format", "json"],
            1, ["amount"])
        write("input.json", '{"amount":"one"}')
        run("cedar-mixed-type-error", "cedar", cedar, 0, ["ALLOW", "long"])
        run("cedar-invalid-input-validation", "cedar", cedar + ["--schema", "schema.json", "--schema-format", "json"],
            1, ["amount"])
        write("policy.rego", 'package study\nimport rego.v1\nresult := {"outcome":"decision-only-allow",'
              '"reasons":["allow"]} if { plus(input.amount, 0) <= 10 }\n')
        opa = ["eval", "--strict", "--strict-builtin-errors", "--fail", "--timeout", "100ms", "--format", "json",
               "--data", "policy.rego", "--input", "input.json"]
        run("opa-version", "opa", ["version"], 0, ["1.21.1"])
        run("opa-type-error", "opa", opa + ["data.study.result"], 2, ["eval_type_error"])
        write("input.json", "{}")
        run("opa-missing-input-undefined", "opa", opa + ["data.study.result"], 1, ["{}"])
        run("opa-unknown-policy-undefined", "opa", opa + ["data.unknown.result"], 1, ["{}"])
    print(json.dumps({"binary_sha256": pins, "results": results}, indent=2))


if __name__ == "__main__":
    main()
