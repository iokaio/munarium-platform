# 0004: first decision-only contract profile

**State: proposed for maintainer review; not accepted or published.** Date: 6 October 2026.
Packet: HUB-02 / DEC-02, DEC-03, minimum DEC-07 and DEC-08. Depends on
[0003](0003-bootstrap-principal-context.md). Owner: founder/maintainer; consumers: Registry,
Warden, Gate, Harness, Server and Matrix. No target authority is enabled by this proposal.

## Canonical requests and candidate artifacts

Propose profile `decision-json-v1`: UTF-8 JSON objects, ASCII member names, strings containing
Unicode scalar values, booleans, null, arrays and integers from -9007199254740991 through
9007199254740991. Reject duplicate decoded keys, floats/exponents, negative zero, nonfinite
numbers, invalid UTF-8, a BOM and isolated surrogates. Maximum request: 65536 bytes;
maximum nesting: 16 containers. Sort object names lexically; preserve array order and string
code points without Unicode normalization; use minimal JSON escapes and no whitespace.
Do not infer defaults or discard unknown fields before hashing. Schema validation rejects
unknown fields; explicit null and omission remain distinct unless the schema forbids them.

This restricted profile avoids cross-language floating-point serialization and UTF-16 key
ordering differences. It is deliberately narrower than
[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html), which supports binary64 number
serialization and orders names by UTF-16 code units. It does not claim general JCS support.
Money/decimal quantities use schema-defined integer units and a separate unit/currency;
no client rounds a decimal into an accepted integer. Broader numeric formats need a version.

Hash domain: `munarium:decision-request:v1` followed by one NUL byte and canonical request
bytes, SHA-256, rendered as `sha256:` plus lowercase hex. An operation ID identifies semantic
intent; the digest identifies its exact content. Reusing an operation ID with another digest
is a conflict, not a new action. Tenant is part of every operation key.

| Record | Required bindings in the proposed version-1 schema |
|---|---|
| Request | schema/profile version, tenant, operation ID, principal-context digest, target ID/environment, capability ID, manifest digest, policy digest, activation epoch, mode, parameters, attachment descriptors |
| Attachment descriptor | immutable content digest, media type and byte count; no inline implicit fetch; bound aggregate limits |
| Manifest | schema version, immutable ID/version, capability, target/environment, credential audience, parameter/result schemas, base consequence class, upward modifiers, required authoritative inputs, effect/idempotency/compensation declarations |
| Decision snapshot | request digest, verified principal digest, manifest/policy/evaluator/version digests, activation epoch, applied mode, input pins/lineage/trust bindings, computed consequence, outcome, reason codes and obligations |

Attachments are references to already admitted immutable content. A missing, changed or
oversize attachment refuses evaluation; a URL is not a digest or authorization to fetch it.
Candidate manifests remain inactive. Gate requires a separately verified active binding to
the exact digest/epoch and does not accept an `active` flag from the submitter. Incompatible
schema, stale activation state, unavailable required input and cross-tenant references refuse.

## S4 lineage and evaluation outcome

An input binding records tenant, source ID and revision/content digest, extraction or mapping
identity/version, derived-field path, observation time, evidence reference, declared trust
state (`unknown`, `untrusted`, `verified`) and verifier/policy provenance. Missing fields do
not default to verified. A verified source does not make every derived field authoritative:
the manifest/policy must designate the exact field, derivation and permitted use. A model
cannot promote its text or self-reported confidence to policy authority. Keep existing
Matrix logical-result and artifact-byte hashes distinct.

The Stage 1 outcomes are `denied`, `approval-required` and `decision-only-allow`. The last
means only that pinned policy permitted the evaluated proposal. It is not admission,
approval, a grant, dispatch or completion. Applied mode is mandatory; observe/advise shadow
results never become executable decisions. Stage 2 lifecycle stays in
[0002](0002-action-execution-protocol.md) and needs HUB-03 acceptance.

Propose Cedar as the first evaluator candidate and Python as the first Harness application
client, with .NET as the second canonical-vector consumer. The
[executed evaluator comparison](evaluator-comparison.md) supports further Cedar investigation;
this remains a recommendation, not an accepted dependency or a performance claim.

| Candidate | Documented behavior / integration question | Required adapter behavior |
|---|---|---|
| Cedar | Default deny and forbid precedence; evaluation errors can coexist with other policy results ([authorization](https://docs.cedarpolicy.com/auth/authorization.html)) | Refuse the whole platform decision on diagnostics; schema-check policies and input entities; encode approval as a separate obligation |
| OPA/Rego | Built-in runtime errors normally become undefined ([language](https://www.openpolicyagent.org/docs/policy-language)) | Strict errors, exactly one typed result, explicit deny default; disable network/time/random built-ins and pin capabilities |
| Python / .NET | Both already have foundation clients; neither is a platform client | Independently reproduce canonical bytes, hashes, rejections and outcome meaning |

The comparison corpus must include allow, deny, deny-overrides-allow, approval-required,
missing attribute, invalid type, unknown policy, unavailable source, tenant mismatch and
replay after input ordering changes. Pin both engines, policies and all inputs; prohibit
ambient clock/network inputs; enforce 100 ms and 64 MiB per evaluation in a killable worker
for the initial experiment. These are proposed bounds to measure, not observed limits.
The [comparison](evaluator-comparison.md) records 36 bounded CLI invocations of OPA 1.21.1
and Cedar 4.13.0, actual errors and matching reordered replays. Its negative controls verified
timeout and memory enforcement. This is not a typed platform evaluator: obligation mapping,
mixed allow/error cases, dependency review and service integration remain open under DEC-03.

## Minimum topology and events

Use the [local profile](../architecture/reference-profile.md) only as a decision-only
candidate: separate Harness, Warden, Registry, Gate and Server process identities; Matrix
only when a declared input needs it. Authenticate every service hop with mTLS and bind
principal assertions to the receiving service and actual peer identity. Authentication
proxies, if any, are explicit trust hops with direct-backend access refused. Loopback or
membership in a container network alone is not identity. Keep operator enrollment outside
Harness; no connector, broker or target credential is provisioned in Stage 1. Pin issuer,
CA, service and database artifacts and test denied edges before calling topology qualified.
The existing proposed Keycloak integration still needs immutable version/license/security
review and installation evidence. No cloud/paid environment is assumed available.

S2/S6 event fields: schema/convention version, tenant, authenticated source service,
source epoch, event ID, per-source sequence, prior-event digest, operation ID, request
digest, kind, recorded time, payload digest, causation/correlation references and payload.
Kinds cover proposal, decision, approval, activation, claim, grant, dispatch, outcome and
correction. Stage 1 emits proposal/decision/refusal records; later kinds are reserved and
cannot claim that their producing protocol exists. Canonical payload digests use a distinct
event domain; final wire schemas must define its exact bytes before implementation.

Server acknowledgement must bind tenant, event ID, payload digest and durable ledger
position. Duplicate same-ID/same-content returns the original acknowledgement; changed
content conflicts. A transport 200 without that binding is insufficient. Sequences order
one source epoch, not all services. Corrections append and link the prior event; holes and
omissions stay visible. Retention records explicit missing ranges and never silently
renumbers history. Polling with stable tenant/source/epoch cursors is the initial export
candidate; mandatory outbox/durability and dispatch barriers remain HUB-03. Metrics may be
loss-tolerant; required accountability events may not. S2 shapes alone prove no durability.

## Evidence, migration and acceptance

[Canonical vectors](decision-json-v1-vectors.json) and
[their checker](../../scripts/test_decision_json_vectors.py) exercise candidate bytes,
digests and ambiguous-input rejection. They are an offline fixture oracle, not a runtime
library, principal verifier, manifest validator or evaluator comparison. They intentionally
do not mark S1–S4 passed. An independent [.NET 10 consumer](../../scripts/canonical-dotnet/Program.cs) also
passed all 19 fixed vectors. This establishes agreement for these candidates, not a
complete application client or general canonical-JSON conformance. Python additionally
checks invalid UTF-8, BOM, exact size and nesting boundaries.

Reproduce from the hub root:

```console
python -m unittest discover -s scripts -p "test_*.py"
dotnet run --file scripts/canonical-dotnet/Program.cs -- docs/decisions/decision-json-v1-vectors.json
```

The Python tests are discovered by existing CI; the .NET consumer is a separate local
check and is not covered by the current Python-only hub workflow.

Before acceptance: supply signed identity vectors from 0003; complete the evaluator adapter
and remaining negative controls identified by the comparison; add reviewed
request/manifest/event schemas with positive
and negative vectors; pin the topology and contract bundle; explicitly dispose of
[0001](0001-scaffold-boundaries.md). Record the exact reviewed revision and acceptance date.
Do not infer acceptance from merge of preparation or tests of this oracle.

After acceptance, publish through the reviewed contract workflow; consumers pin the bundle
digest. Server adds S2–S4 semantics and additive migrations upstream; existing evidence
contracts and clients retain their versions until the compatible expand/migrate/remove
transition is approved. This proposal does not hand-edit vendored foundation contracts.
