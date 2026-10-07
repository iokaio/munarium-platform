# 0007: Stage 1 implementation and composition boundary

**Implementation authorized on 6 October 2026; proposed semantics, not accepted or released.**
The requested scope is both Stage 1 rows in the [parallel plan](../parallel-build-plan.md):
identity/inventory and the complete decision-only slice. The existing ADRs and immutable
candidate bundles remain unchanged. Human acceptance and production qualification are
separate from this implementation request.

The [development authorization](../stage1-authorization.md) records the supporting
guidance and CI scope, including the remaining S1 bootstrap authority, provider
identity admission and authenticated service topology work. Those prerequisites
are authorized implementation work; their evidence and contract acceptance remain
open until supplied.

## Inputs and ownership

Use ADRs [0003](0003-bootstrap-principal-context.md),
[0004](0004-decision-only-contracts.md), [0005](0005-warden-identity-admission.md) and
[0006](0006-registry-manifest-admission.md). Preserve their hashes, negative vectors and
unaccepted status. Registry owns signed candidate validation; Warden owns principal
verification and attenuation; Gate owns independent request validation, evaluation and
replay; Harness owns independent Rust/Python clients and the composition runner; Server
owns authoritative event storage, identity admission and lineage. Matrix is omitted when
the synthetic scenario has no structured-data dependency.

No target credential, execution grant, connector dispatch, Council approval or effect
is supplied by Stage 1. Warden's existing later-stage modules are outside this composition.
Candidate submission cannot install an effective binding. An independently provisioned
operator fixture supplies the initial decision-only catalog; it is never derived from
an agent's `active` field or from the hub checkout at runtime.

## Admission and evaluation

Receiving adapters obtain the actual peer from authenticated transport, select tenant
and current authority independently, and reverify original signed chains on each operation.
Every delegation edge binds its own child service, and every ancestor fits within current
task/policy validity. A prior successful verification is not a permanent authorization.

Gate recomputes ADR-0004 canonical bytes and the request digest. The exact Registry v2
manifest and signed artifact digests, tenant, target, environment, policy, mode and epoch
must match an independently selected current binding. Referenced schemas and attachments
must resolve to checked immutable bytes. Unknown or incompatible inputs refuse.

Lineage is selected from authoritative evidence storage, never trusted from the proposal.
Each required field must have complete verified source, content, derivation, version,
observation, evidence and verifier bindings and match the admitted policy's permitted use.
Unavailable, unknown, untrusted, substituted and cross-tenant inputs refuse. Consequence
modifiers may only raise the manifest base class; unsupported predicates refuse.

The first concrete worker uses OPA 1.21.1 Windows amd64 from ADR-0004's comparison,
raw SHA-256 `25406f7c6e147d687fd7fd546f835bafa160a6242c605ee94a23ba6cd7bccdcd`.
It pins the worker source and pure-builtin capabilities alongside the native binary;
the native build's `-dirty` suffix remains an explicit qualification limitation. Windows
Job Objects impose 64 MiB per process; strict evaluation and the invocation supervisor
impose a 100 ms deadline. Other native host profiles fail closed. OPA is the experimental
implementation choice, not a formal disposition of DEC-03. Engine
diagnostics, malformed/ambiguous output, unknown determining rules, exceeded bounds and
unavailable workers refuse the entire decision. Native allow does not override diagnostics.
Approval obligations bind the exact request and policy and cannot be dropped by a permit.
No Stage 1 outcome means execution admission, even in enforce mode.

The policy artifact contains engine, version, engine_digest, worker_digest,
capabilities_digest, code, inputs, rules and optional manifest_approver_scope.
Native output is exactly allow/forbid Booleans, determining rule IDs, Boolean modifier
predicates and an empty diagnostics array. Deny wins; unknown/duplicate rules refuse.
Each rule maps to null or a distinct-approval obligation with approver_scope. Manifest
obligations are additive. The policy artifact and capability/replay artifacts are
experimental local encodings pending review; the unchanged candidate schemas do not
silently acquire these new fields.

Artifact hashes use SHA-256 of the ASCII domain, one zero byte, then canonical JSON:
`munarium:decision-policy:v1`, `munarium:opa-capabilities:v1`, and
`munarium:decision-replay:v1`. Binary, worker and source-content digests use raw bytes.
Replay restores an integrity-checked bundle from protected Server storage, reconstructs
its evaluation input and requires exact decision equality. It does not authenticate a
reader or establish historical signing-key trust by itself.

## Records, replay and clients

Proposal/decision/refusal events and acknowledgements use the unchanged foundation
candidate. Server binds authenticated source and tenant, retains exact event and payload
digests, preserves same-ID retry receipts and rejects changed content. Per-source sequences
and predecessor references cannot be silently renumbered. A required recording failure
cannot return a successful recorded decision.

Replay uses the exact original request and pinned manifest, policy, evaluator and evidence
bundle; it never refreshes data or dispatches an action. Live lookup still authenticates the
reader and tenant. Clients persist operation identity before submit; an ambiguous response
leads only to lookup, with no automatic resubmission or new operation identity.

## Completion evidence

Run unchanged golden vectors in independent consumers, the Warden/Registry interoperability
checks and REF-01 with the actual component implementations. Include unknown/inactive/
incompatible manifests, missing and untrusted lineage, tenant substitution, evaluator
diagnostics, recording outage, changed operation content, and deterministic replay.
An experimental run record retains exact source/configuration pins, commands, actual outcomes,
failed attempts, unavailable coverage and cleanup. Source modifications do not constitute
immutable release pins. Formal acceptance, independent review and topology qualification
remain pending unless separately supplied by their accountable reviewer.

The [implementation record](../architecture/stage1-implementation.md) distinguishes
observed component/persistence behavior from the still-missing S1 authority profile and
separate mTLS service topology. In-process adapters cannot close those acceptance gates.
