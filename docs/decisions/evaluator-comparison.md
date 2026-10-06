# HUB-02 synthetic evaluator comparison

**Executed 6 October 2026; review evidence, not evaluator acceptance or production
qualification.** This bounded local experiment informs [ADR 0004](0004-decision-only-contracts.md).
It exercised native Windows command-line releases with fictional inputs. No platform service,
verified principal, live source, activation, grant or target operation was involved.

## Artifacts and execution boundary

Official release assets were downloaded with `gh release download`, without global installation.
SHA-256 matched both GitHub's release-asset digest and the adjacent `.sha256` file:

| Release | Asset | Verified SHA-256 |
|---|---|---|
| [OPA v1.21.1](https://github.com/open-policy-agent/opa/releases/tag/v1.21.1) | `opa_windows_amd64.exe` | `25406f7c6e147d687fd7fd546f835bafa160a6242c605ee94a23ba6cd7bccdcd` |
| [Cedar CLI v4.13.0](https://github.com/cedar-policy/cedar/releases/tag/cedar-policy-cli-v4.13.0) | `cedar-policy-cli-x86_64-pc-windows-msvc.zip` | `93eb36eff9469f09a25293ec07349a7554187b61353bd05c193c59e99572a138` |

`opa version` reported 1.21.1, Windows/amd64, Rego v1, Go 1.27.1 and build commit
`2a109e54103370d2ef288782ef3cb4c8a37902b2-dirty`. The official binary's `-dirty` suffix is
retained; checksum verification does not establish a reproducible build. `cedar --version`
reported `cedar-policy-cli 4.13.0`. Both official repository license endpoints reported
Apache-2.0; transitive dependency/security review remains open.

The host used Windows amd64, Python 3.13.7 and PowerShell 7.6.6. Each process started suspended,
was assigned to a Windows Job Object, then resumed. Limits were one process, 64 MiB committed
memory and kill-on-job-close; a supervising 100 ms timeout killed an unfinished process.
OPA additionally used its `--timeout 100ms`. Measured elapsed time starts at resume and includes
CLI execution, but excludes suspended process creation. Memory is peak process commit reported
by the Job Object, **not resident memory**. Timeout supervision is not a hard real-time guarantee.

Negative controls passed: a one-second Python sleep was killed by the timeout; allocation of a
128 MiB byte array failed with `MemoryError`. These test the supervisor, not malicious-policy
containment. Engine-specific environment overrides were removed. OPA capabilities allowed only
`eq`, `equal`, `plus` and `lte`, retaining its version feature declarations and setting
`allow_net: []`; no clock, randomness, HTTP or other network built-in was available. No network
input appears in either policy. An OS network isolation boundary was not tested.

## Reproducible synthetic corpus

The exact baseline `input.json` is:

```json
{"allow":true,"blocked":false,"approval_required":false,"source_available":true,"tenant":"alpha","target_tenant":"alpha","amount":1}
```

Save this OPA policy as `policy.rego`:

```rego
package study
import rego.v1
default result := {"outcome": "denied"}
eligible if {
    input.allow == true
    input.source_available == true
    input.tenant == "alpha"
    input.target_tenant == input.tenant
    input.blocked == false
    plus(input.amount, 0) <= 10
}
result := {"outcome": "decision-only-allow"} if {
    eligible
    input.approval_required == false
}
result := {"outcome": "approval-required"} if {
    eligible
    input.approval_required == true
}
```

Save this Cedar policy as `policy.cedar`; use an empty entity array `[]` in `entities.json`:

```cedar
permit(principal, action, resource)
when {
    context.allow && context.source_available &&
    context.tenant == "alpha" && context.target_tenant == context.tenant &&
    context.amount + 0 <= 10 && !context.approval_required
};
permit(principal, action, resource)
when {
    context.allow && context.source_available &&
    context.tenant == "alpha" && context.target_tenant == context.tenant &&
    context.amount + 0 <= 10 && context.approval_required
};
forbid(principal, action, resource)
when { context.blocked };
```

The experiment labels Cedar's generated `policy0` as ordinary allow, `policy1` as approval
required and `policy2` as deny. These labels demonstrate a mapping requirement; they are not
an implemented typed obligation contract. OPA's deny precedence is explicitly encoded in
`eligible`; Cedar's forbid competes with the permit. Neither is inferred from a numeric score.

Generate `capabilities.json` from `opa capabilities --current`, retaining only the four built-in
names listed above and setting `allow_net` to an empty array. From the fixture directory:

```powershell
./opa_windows_amd64.exe eval --strict --strict-builtin-errors --fail --timeout 100ms --format json --capabilities capabilities.json --data policy.rego --input input.json data.study.result
./cedar/cedar.exe authorize --principal 'User::"alice"' --action 'Action::"evaluate"' --resource 'Target::"example"' --context input.json --entities entities.json --policies policy.cedar --verbose --error-format json
```

For each table row, start from the baseline and apply only its change. Run twice, reversing
JSON object member order for the second run. For unknown policy, query `data.unknown.result`
in OPA; give Cedar an empty policy file. Those are distinct native representations of absent
requested policy, not evidence of a shared policy lookup API.

| Case / change | OPA native result; exit | Cedar native result; exit |
|---|---|---|
| Allow / unchanged | `decision-only-allow`; 0 | `ALLOW`, policy0; 0 |
| Deny / `allow=false` | `denied`; 0 | `DENY`, no policy applies; 2 |
| Deny overrides allow / `blocked=true` | `denied`; 0 | `DENY`, policy2; 2 |
| Approval / `approval_required=true` | `approval-required`; 0 | `ALLOW`, policy1; 0 |
| Missing attribute / omit `amount` | `denied`; 0 | `DENY` plus missing-attribute diagnostics for policy0/1; 2 |
| Invalid type / `amount="one"` | `eval_type_error`, plus operand must be number; 2 | `DENY` plus expected-long/got-string diagnostics for policy0/1; 2 |
| Unknown policy / as above | undefined, `{}`; 1 | `DENY`, no policy applies; 2 |
| Unavailable source / `source_available=false` | `denied`; 0 | `DENY`, no policy applies; 2 |
| Tenant mismatch / `target_tenant="beta"` | `denied`; 0 | `DENY`, no policy applies; 2 |

All nine exit/stdout/stderr triples were byte-identical across the two reordered replays for
each engine: 36 invocations, no timeouts. The missing-field OPA result demonstrates that strict
built-in errors do not make absent input fields an error. Cedar's native decision and diagnostics
must be inspected together. This corpus does not exercise the separate case of an `ALLOW`
coexisting with diagnostics.

A separate Cedar schema probe, outside the measured corpus, declared empty `User` and `Target`
entity shapes and action `evaluate` applicable to them. Its context required the baseline's four
Boolean fields, two String fields and Long `amount`. `cedar validate --schema schema.json
--schema-format json --policies policy.cedar --deny-warnings --error-format json` passed, exit 0.
Authorization with that schema allowed the baseline, exit 0, and rejected both missing amount and
string amount before evaluation, exit 1. Those outcomes support schema validation; the measured
corpus deliberately omitted it to expose native error behavior.

## Measurements, adapter implications and remaining work

| Engine | Elapsed range over 18 invocations | Maximum process commit |
|---|---|---|
| OPA | 69.463–82.760 ms | 61,603,840 bytes |
| Cedar | 17.231–23.242 ms | 1,601,536 bytes |

These are one host's short CLI runs under the stated limits, including parsing and process
execution, not an engine benchmark, steady-state service latency or general capacity claim.
Two runs establish only this replay observation, not universal determinism.

The proposed adapter must validate input types and required fields before either engine, bind
the requested policy digest to an admitted artifact, and refuse undefined/missing policy or
any evaluation diagnostic. **Errors refuse the whole platform decision, including a Cedar
`ALLOW` accompanied by errors.** Do not turn absent source evidence into an ordinary business
denial without preserving the unavailable-input reason. Require exactly one typed result.
Approval must come from a reviewed, typed policy obligation bound to the decision snapshot;
freeform annotations, native `ALLOW`, or this study's generated policy labels cannot authorize it.
OPA strict-error mode and Cedar schema validation help but do not replace those checks.

The experiment supports continued Cedar investigation, not engine selection. Acceptance still
needs the typed obligation/error adapter, schema and policy admission tests, mixed allow/error
negative controls, adversarial resource tests, dependency/security review and actual service
integration. No component status or invariant evidence field advances here.

Local study outputs remain under the hub checkout's ignored `target/evaluator-comparison/`:
`run_study.py`, both policy files, the 18 input files, `capabilities.json`, `schema.json`,
`results.json`, `summary.json`, `controls.json`, `transcript.jsonl` and `artifacts.sha256.json`.
These paths are local output references, not published artifacts. The public synthetic policy,
input mutations and commands above reconstruct the semantic comparison; reproducing the timing
boundary also requires the described Windows supervisor. No foundation scratch logs were copied.
