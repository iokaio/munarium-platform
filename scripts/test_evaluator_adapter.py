# SPDX-License-Identifier: Apache-2.0
"""Proposed, offline evaluator fixture oracle; never import into a runtime service."""
import copy
import hashlib
import json
import re
import unittest

from test_decision_json_vectors import canonical


VERSIONS = {"cedar": "4.13.0", "opa": "1.21.1"}
DIGEST_FIELDS = {"request", "principal", "manifest", "policy", "evaluator", "inputs"}
CONTEXT_FIELDS = DIGEST_FIELDS | {"tenant", "epoch", "mode"}
APPROVAL = {"kind": "distinct-approval", "approver_scope": "council:ratify"}


def encode(value):
    return canonical(json.dumps(value, ensure_ascii=False).encode())


def digest(value):
    return "sha256:" + hashlib.sha256(b"munarium:evaluator-fixture:v1\0" + encode(value)).hexdigest()


def context_valid(context):
    return (isinstance(context, dict) and set(context) == CONTEXT_FIELDS
            and all(isinstance(context[k], str) and re.fullmatch(r"sha256:[0-9a-f]{64}", context[k])
                    for k in DIGEST_FIELDS)
            and isinstance(context["tenant"], str) and bool(context["tenant"])
            and type(context["epoch"]) is int and context["epoch"] >= 1
            and context["mode"] in ("observe", "advise", "guard", "enforce", "assure"))


def adapt(raw, engine, artifact, expected, evaluated, inputs):
    """Model the trusted adapter boundary; expected pins are supplied by a fixture.

    evaluated is the context actually sent to the worker, not an engine assertion.
    Refusal is a denied result with a machine-readable reason, never an approval.
    """
    def result(outcome, reason, obligations=()):
        return {"outcome": outcome, "reasons": [reason],
                "binding": copy.deepcopy(expected), "obligations": list(obligations)}

    def refuse(reason):
        return result("denied", reason)

    if not context_valid(expected) or not context_valid(evaluated) or expected != evaluated:
        return refuse("context-mismatch")
    if engine not in VERSIONS or not isinstance(artifact, dict):
        return refuse("policy-not-admitted")
    if (set(artifact) != {"engine", "version", "source", "rules"}
            or artifact["engine"] != engine or artifact["version"] != VERSIONS[engine]
            or not isinstance(artifact["source"], str) or not artifact["source"]
            or not isinstance(artifact["rules"], dict) or not artifact["rules"]):
        return refuse("policy-not-admitted")
    rules = artifact["rules"]
    if any(not isinstance(k, str) or not k or v not in ([], [APPROVAL]) for k, v in rules.items()):
        return refuse("policy-not-admitted")
    try:
        admitted = (digest(artifact) == expected["policy"]
                    and digest({"engine": engine, "version": VERSIONS[engine]}) == expected["evaluator"])
    except (ValueError, UnicodeError):
        admitted = False
    if not admitted:
        return refuse("policy-not-admitted")
    if not isinstance(inputs, dict) or set(inputs) != {"available", "amount"}:
        return refuse("input-invalid")
    if (type(inputs["available"]) is not bool or type(inputs["amount"]) is not int
            or abs(inputs["amount"]) > 9007199254740991):
        return refuse("input-invalid")
    if digest(inputs) != expected["inputs"]:
        return refuse("context-mismatch")
    if not inputs["available"]:
        return refuse("input-unavailable")
    try:
        value = json.loads(canonical(raw))
        if engine == "cedar":
            # Typed SDK boundary, not a parser for the human-oriented CLI stdout.
            if set(value) != {"decision", "reasons", "errors"}:
                raise ValueError()
            if not isinstance(value["errors"], list):
                raise ValueError()
            if value["errors"]:
                return refuse("evaluation-error")
            if value["decision"] not in ("ALLOW", "DENY"):
                raise ValueError()
            outcome = "decision-only-allow" if value["decision"] == "ALLOW" else "denied"
            reasons = value["reasons"]
        else:
            if value == {}:
                return refuse("evaluation-undefined")
            if "errors" in value:
                return refuse("evaluation-error")
            if set(value) != {"result"} or len(value["result"]) != 1:
                raise ValueError()
            row = value["result"][0]
            if set(row) != {"expressions"} or len(row["expressions"]) != 1:
                raise ValueError()
            expression = row["expressions"][0]
            if set(expression) != {"value", "text", "location"} or expression["text"] != "data.study.result":
                raise ValueError()
            native = expression["value"]
            if set(native) != {"outcome", "reasons"}:
                raise ValueError()
            outcome, reasons = native["outcome"], native["reasons"]
            if outcome not in ("denied", "decision-only-allow", "approval-required"):
                raise ValueError()
        if (not isinstance(reasons, list) or any(not isinstance(x, str) for x in reasons)
                or len(set(reasons)) != len(reasons) or any(x not in rules for x in reasons)
                or (outcome != "denied" and not reasons)):
            raise ValueError()
        obligations = [APPROVAL] if any(rules[x] for x in reasons) else []
        if engine == "opa" and (outcome == "approval-required") != bool(obligations):
            if outcome != "denied":
                raise ValueError()
        if outcome == "denied":
            return result("denied", "policy-deny")
        if obligations:
            return result("approval-required", "policy-approval", [
                dict(APPROVAL, policy_digest=expected["policy"], request_digest=expected["request"])])
        return result("decision-only-allow", "policy-allow")
    except (ValueError, TypeError, KeyError, UnicodeError):
        return refuse("evaluation-malformed")


def fixture(engine="cedar", approval=False):
    artifact = {"engine": engine, "version": VERSIONS[engine], "source": "fictional-policy-v1",
                "rules": {"allow": [], "approve": [APPROVAL], "forbid": []}}
    inputs = {"available": True, "amount": 1}
    context = {k: "sha256:" + "a" * 64 for k in DIGEST_FIELDS}
    context.update(tenant="fictional-alpha", epoch=1, mode="advise", policy=digest(artifact),
                   evaluator=digest({"engine": engine, "version": VERSIONS[engine]}), inputs=digest(inputs))
    reasons = ["approve" if approval else "allow"]
    if engine == "cedar":
        native = {"decision": "ALLOW", "reasons": reasons, "errors": []}
    else:
        native = {"result": [{"expressions": [{"value": {
            "outcome": "approval-required" if approval else "decision-only-allow", "reasons": reasons},
            "text": "data.study.result", "location": {"row": 1, "col": 1}}]}]}
    return dict(raw=encode(native), engine=engine, artifact=artifact, expected=context,
                evaluated=copy.deepcopy(context), inputs=inputs)


class EvaluatorAdapterVectors(unittest.TestCase):
    def assert_refused(self, args, reason):
        output = adapt(**args)
        self.assertEqual((output["outcome"], output["reasons"], output["obligations"]),
                         ("denied", [reason], []))

    def test_positive_outcomes_and_obligation_binding(self):
        for engine in VERSIONS:
            for approval in (False, True):
                with self.subTest(engine=engine, approval=approval):
                    args = fixture(engine, approval)
                    output = adapt(**args)
                    self.assertEqual(output["outcome"], "approval-required" if approval else "decision-only-allow")
                    self.assertEqual(output["binding"], args["expected"])
                    self.assertEqual(output["obligations"],
                                     [dict(APPROVAL, policy_digest=args["expected"]["policy"],
                                           request_digest=args["expected"]["request"])] if approval else [])

    def test_every_binding_is_mandatory_and_exact(self):
        for engine in VERSIONS:
            for key in CONTEXT_FIELDS:
                for missing in (True, False):
                    with self.subTest(engine=engine, key=key, missing=missing):
                        args = fixture(engine)
                        if missing:
                            del args["evaluated"][key]
                        else:
                            args["evaluated"][key] = 2 if key == "epoch" else "changed"
                        self.assert_refused(args, "context-mismatch")

    def test_exact_policy_and_typed_obligation_admission(self):
        for engine in VERSIONS:
            for key, value in (("source", "changed"), ("version", "floating"), ("rules", {}),
                               ("rules", {"allow": [{"kind": "approve"}]}),
                               ("rules", {"allow": [dict(APPROVAL, approver_scope="requester:self")]}),
                               ("rules", {"allow": [dict(APPROVAL, request_digest="forged")]})):
                with self.subTest(engine=engine, key=key, value=value):
                    args = fixture(engine)
                    args["artifact"][key] = value
                    self.assert_refused(args, "policy-not-admitted")
            for template in ({"kind": "distinct-approval"},
                             dict(APPROVAL, approver_scope="requester:self")):
                args = fixture(engine)
                args["artifact"]["rules"]["approve"] = [template]
                args["expected"]["policy"] = args["evaluated"]["policy"] = digest(args["artifact"])
                self.assert_refused(args, "policy-not-admitted")
            for key in ("policy", "evaluator"):
                args = fixture(engine)
                args["expected"][key] = args["evaluated"][key] = "sha256:" + "b" * 64
                self.assert_refused(args, "policy-not-admitted")

    def test_missing_invalid_and_unavailable_inputs(self):
        for engine in VERSIONS:
            for inputs, reason in (({}, "input-invalid"), ({"available": True, "amount": True}, "input-invalid"),
                                   ({"available": False, "amount": 1}, "input-unavailable")):
                args = fixture(engine)
                args["inputs"] = inputs
                args["expected"]["inputs"] = args["evaluated"]["inputs"] = digest(inputs)
                self.assert_refused(args, reason)
            args = fixture(engine)
            args["inputs"]["amount"] = 2
            self.assert_refused(args, "context-mismatch")

    def test_cedar_diagnostics_and_deny_precedence(self):
        for decision in ("ALLOW", "DENY"):
            args = fixture()
            args["raw"] = encode(dict(decision=decision, reasons=["allow"], errors=["missing attribute"]))
            self.assert_refused(args, "evaluation-error")
        args["raw"] = encode(dict(decision="DENY", reasons=["forbid"], errors=[]))
        self.assert_refused(args, "policy-deny")
        args["raw"] = encode(dict(decision="ALLOW", reasons=["allow", "approve"], errors=[]))
        self.assertEqual(adapt(**args)["outcome"], "approval-required")

    def test_opa_undefined_errors_and_ambiguous_outputs(self):
        for native, reason in (({}, "evaluation-undefined"), ({"errors": ["bad type"]}, "evaluation-error"),
                               ({"result": []}, "evaluation-malformed")):
            args = fixture("opa")
            args["raw"] = encode(native)
            self.assert_refused(args, reason)
        for mutation in ("rows", "expressions", "missing-obligation", "untyped-obligation"):
            args = fixture("opa", True)
            native = json.loads(args["raw"])
            expression = native["result"][0]["expressions"][0]
            if mutation == "rows":
                native["result"] *= 2
            elif mutation == "expressions":
                native["result"][0]["expressions"] *= 2
            elif mutation == "missing-obligation":
                expression["value"]["reasons"] = ["allow"]
            else:
                expression["value"]["obligations"] = ["approve me"]
            args["raw"] = encode(native)
            self.assert_refused(args, "evaluation-malformed")
        args = fixture("opa")
        native = json.loads(args["raw"])
        native["result"][0]["expressions"][0]["value"] = {"outcome": "denied", "reasons": ["forbid"]}
        args["raw"] = encode(native)
        self.assert_refused(args, "policy-deny")

    def test_malformed_outputs_and_unadmitted_reasons(self):
        for engine in VERSIONS:
            for raw in (b'null', b'[]', b'{"decision":"ALLOW","decision":"DENY"}', b'{', b'{"x":NaN}'):
                args = fixture(engine)
                args["raw"] = raw
                self.assert_refused(args, "evaluation-malformed")
        for reasons in ([], ["unknown"], ["allow", "allow"], [1], "allow"):
            args = fixture()
            args["raw"] = encode(dict(decision="ALLOW", reasons=reasons, errors=[]))
            self.assert_refused(args, "evaluation-malformed")

    def test_reordered_input_replay_preserves_exact_snapshot(self):
        for engine in VERSIONS:
            args = fixture(engine, True)
            original = adapt(**args)
            args["inputs"] = dict(reversed(list(args["inputs"].items())))
            args["artifact"] = dict(reversed(list(args["artifact"].items())))
            args["evaluated"] = dict(reversed(list(args["evaluated"].items())))
            self.assertEqual(adapt(**args), original)


if __name__ == "__main__":
    unittest.main()
