# HUB-02 evaluator adapter oracle

**Proposed test profile, executed 6 October 2026; not an accepted evaluator, released
contract or component implementation.** This follows [ADR 0004](0004-decision-only-contracts.md)
and the [native-engine comparison](evaluator-comparison.md). Source baseline:
`iokaio/munarium-platform` at `767e4613d9e18a3ae9f93b7f49f983b6aaeee664`; this document and its
linked scripts define the proposed follow-up, whose exact revision is retained by its PR. Both parallel prerequisite
lanes used one Windows host, not independently operated machines.

## Executable boundary

The [stdlib oracle](../../scripts/test_evaluator_adapter.py) models a typed worker-response
boundary. It requires the adapter's expected and actually evaluated contexts to match:
tenant, request/principal/manifest/policy/evaluator/input digests, activation epoch and
applied mode. Every field is mandatory. These are trusted fixture inputs: equality does
not verify a principal signature, activation, input provenance or service identity.

The artifact digest pins the complete fictional policy source, engine/version and rule-to-
obligation mapping. No freeform annotation or generated native rule ID supplies authority.
An admitted rule may carry exactly `{kind: "distinct-approval", approver_scope: "council:ratify"}`.
The output obligation adds `policy_digest` and `request_digest` from the fixture's trusted
`policy` and `request` fields, using the proposed wire obligation vocabulary. The full context
remains bound at the decision-result level. The scope is a policy-designated approver selector;
future runtime processing must verify an actually authorized approver distinct from the requester.
Ordinary allow plus an approval rule still requires approval. Denial discards obligations.
This is a requirement for future Council processing, not an approval token.

The fixture-only digest domain is UTF-8 `munarium:evaluator-fixture:v1`, one NUL byte, then
`decision-json-v1` canonical bytes, hashed with SHA-256. This domain **does not replace**
request, artifact, principal or event digest domains in wire schemas. Here `evaluator` pins
engine/version identity, not a binary attestation; the native probe separately pins binaries.
Changing semantics, allowed obligations or engine versions requires new reviewed vectors
and a new fixture profile version. Released contracts still require their own admission,
version policy and expand/migrate/remove transition.

Cedar's typed response contains decision, determining rule IDs and diagnostics. Any
diagnostic refuses the whole decision, even native `ALLOW`. OPA requires exactly one result
and expression for `data.study.result`, with a typed outcome/reason object; undefined, errors,
multiple results, duplicate keys, unknown rule IDs and malformed obligations refuse. Missing
or invalid input refuses before evaluation; unavailable source has `input-unavailable`,
separate from `policy-deny`. Refusals use outcome `denied` and a distinct machine-readable
reason, preserving ADR 0004's three-outcome vocabulary. No output grants execution authority.

The eight unittest methods exercise positive allow/approval, deny precedence, both engines'
mandatory bindings, changed policy/evaluator pins, invalid obligation admission, bad and
unavailable inputs, mixed errors, undefined/ambiguous/malformed outputs, and reordered replay.
They are discovered by the existing Python CI job, without installing either native engine.
Fixtures are constructed directly in the test file; expected refusal reasons and outcomes
are explicit assertions. This is not a Cedar CLI text parser or a deployable adapter library.

## Actual native checks

The [probe](../../scripts/probe_evaluator_engines.py) creates only fictional files in a
temporary directory and removes them afterward. It verifies executable SHA-256 before
running; provenance of the original release assets is in the earlier comparison.

| Engine | Version | Executable SHA-256 |
|---|---|---|
| Cedar | 4.13.0 | `02c5a18726edb0bfa4725076dbc4fd5d92adf8d1652916ecca40d2ff9f773549` |
| OPA | 1.21.1 | `25406f7c6e147d687fd7fd546f835bafa160a6242c605ee94a23ba6cd7bccdcd` |

All ten invocations passed their explicit exit/output assertions. Two checked versions;
eight checked these native semantics. Cedar's two policies permit unconditionally and
permit when `context.amount + 0 <= 10`; the schema requires Long `amount`.

| Check | Observed native outcome | Exit |
|---|---|---|
| Cedar missing amount, no schema | `ALLOW` and missing-attribute error for policy1 | 0 |
| Cedar string amount, no schema | `ALLOW` and expected-long/got-string error for policy1 | 0 |
| Cedar policy/schema validation | No errors or warnings | 0 |
| Cedar missing amount, schema enabled | Request parse failure, required amount absent | 1 |
| Cedar string amount, schema enabled | Context invalid for evaluate | 1 |
| OPA string amount, strict built-in errors | `eval_type_error` | 2 |
| OPA missing amount, strict built-in errors | Undefined `{}` | 1 |
| OPA unknown policy query | Undefined `{}` | 1 |

Cedar diagnostics appeared in **stdout**, with empty stderr, despite `--error-format json`;
exit 0 alone is insufficient. OPA retains build commit
`2a109e54103370d2ef288782ef3cb4c8a37902b2-dirty`; checksum pinning does not establish reproducibility.
The probe uses a five-second subprocess timeout and OPA's 100 ms evaluation timeout.
It does not enforce the earlier study's 64 MiB Job Object limit, measure latency, disable
all capabilities or prove OS network isolation. The policies contain no network or clock use.

Reproduce from the hub root with those exact local binaries:

```console
python -m unittest discover -s scripts -p "test_*.py"
python scripts/probe_evaluator_engines.py --cedar PATH_TO_CEDAR --opa PATH_TO_OPA
```

The second command prints each exact command, stdout, stderr, exit and assertion result.
The executed transcript is retained locally at ignored `target/evaluator-oracle/native-results.json`;
the public probe reconstructs all inputs and expected checks. Binary execution is a separate
local check, not covered by hub CI. Remaining prerequisites include production adapter/SDK
integration, policy compiler admission and obligation consistency, adversarial resource tests,
dependency/security review, topology qualification and explicit maintainer acceptance.
No S1–S4 outcome, catalog state, invariant evidence field or release label advances here.

Local hub validation passed: all 34 Python unittest methods, licence headers, private-material
scan, documentation links/indexes, gitleaks 8.30.1 directory scan and `git diff --check`.
This is local evidence; remote CI results belong to the exact PR head.
