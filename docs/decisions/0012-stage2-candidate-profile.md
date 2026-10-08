# 0012: first Stage 2 wire candidate and offline profile

**Candidate preparation directed, 7 October 2026; wire acceptance pending.**
The maintainer reviewed and merged [PR 13](https://github.com/iokaio/munarium-platform/pull/13)
at `8a58292e55d9785d57763524f849d9aa0c13a77b`, then directed proceeding with the
next packet. [The packet](../stage2-contract-packet.md) records that direction and
its limits. This record makes [ADR 0010](0010-stage2-authority-durability.md) and
[ADR 0011](0011-platform-contract-evolution.md) concrete as a new, inert wire
candidate. It does not retrospectively accept old schemas or enable dispatch.

## Selected basis and alternatives

Use one cell, the synthetic `release.publish_approved_artifact` capability, one
distinct enrolled human approver, Gate-owned action transactions, participant-bound
activation and a shared event envelope. Linux isolation and PostgreSQL are the
selected reference direction for subsequent qualification. Exact Linux evaluator,
database, human IdP and broker versions remain runtime intake requirements; this
offline candidate neither installs them nor invents qualified dependency pins.

Choose explicitly typed references and closed records rather than arbitrary
extension dictionaries. Restrict this profile to its synthetic parameter schema,
supported obligations and local authority scope; other capabilities need their own
admitted parameter/profile definitions. Old decision-json/Registry bundles retain
their exact bytes. A digest or passing fixture is not current permission.

## Candidate identities and bytes

The [bundle](stage2-v1/README.md) uses profile `stage2-single-cell-v1`, wire
`schema_version: 1`, and distinct top-level `type` tags. This version belongs to
the new action namespace, not the existing decision-request namespace. References
bind domain, tenant, deployment, cell, object kind and ID. Principal references
add subject generation and origin kind. Authentication proofs are separate input
to admission, not mutable fields in the durable action request.

Canonical JSON retains the existing 65,536-byte, 16-container, safe-integer,
ASCII-member-name restrictions. Object member order is canonical; array order
is significant. Authoritative sets use the exact profile order or explicitly
unique IDs, never an implicit sort during verification. Reject duplicate members,
unknown fields, floating point, nonfinite values and noncanonical wire bytes.

Every new digest is lowercase `sha256:` hex over UTF-8
`munarium:stage2:<domain>:v1`, one NUL, then canonical object bytes. Domains are
`intent`, `context`, `participants`, `artifact-set`, `profile`, and the closed
top-level type tags. Payload digest uses `event-payload`. Arrays are hashed in
wrapper objects with the field names `participants` or `artifacts`. No value
includes its own digest. Schema and lock files use the documented LF file-hash
convention instead; those are integrity pins, not semantic record digests.

## Request, decision and approval

An operation binds immutable intent: qualified actor/origin, registered task
lineage, target/environment, capability operation, parameters, attachments and
target precondition. An authorization attempt binds this intent plus an immutable
context containing activation/recovery revisions, authority pins, manifest,
policy, evaluator and evidence. Required evidence names its source, field,
derivation, observation, expiry, trust and verifier. The independently admitted
fixture context supplies the expected facts; self-asserted `verified` is insufficient.

The decision binds request/context digests and the ordered required obligation
set: distinct approval, mandatory recording, action capacity and credential
custody, with typed owner/parameters. Only an `approval-required` decision is an
approval input. A denied result has no executable obligations. No shadow allow
or unsupported obligation can authorize action in this enforce-only profile.

Approval binds exact operation/attempt/request/context/decision, the enrolled
human approver, eligibility revision, issue time and expiry. Maximum lifetime is
300 seconds with a two-second uncertainty margin; current status, context and
eligibility are checked on lookup. Council's authenticated durable record is the
authority source. This candidate contains no bearer approval token or signature
scheme: receiving or hashing a JSON approval never substitutes for the current
authenticated Council lookup. Offline signed evidence is a later contract.

The oracle checks immutable bindings and current supplied state, not atomic
attempt replacement. ADR 0011's Gate/Warden closure receipts and real-store race
tests remain necessary before claim supersession. Consumed or unresolved work is
never made reusable by a new approval, grant, expiry or arbitrary client key.

## Activation and acknowledgement

The coordinator is Council; the ordered receipt participants are Gate, Registry,
Server and Warden. A transition binds qualified scope, immutable profile digest,
expected prior artifact set/epoch, exact successor set and its digest, participant
set/digest, human ratification reference, not-before and expiry. Successor epoch
must be strictly greater than the prior epoch; rollback is a new transition.

Each apply receipt binds participant, transition digest, selected artifact and
participant sets, prior/successor epochs and phase. Resume requires the complete
authenticated applied-receipt set plus Gate's prior pause receipt and current
paused transition. Receipt JSON cannot prove its own source or committed state.
Missing, duplicate, stale or unexpected participants refuse; observing one
Registry active pointer cannot stand for complete cell activation.

## Shared records and recovery

The envelope binds qualified scope, producer, registered stream/generation,
sequence/predecessor, occurrence time/clock provenance, family/kind, payload digest
and causal references. Action payloads bind operation, attempt, request/context
digests and separate activation/recovery epochs. Their kinds are approval-recorded,
claim-created, grant-issued, consumption-reserved, predispatch, send-intent, outcome
and reconciliation. Activation-applied is a separate payload family without fake
action IDs. Gateway, suspension and export payloads are deliberately unsupported
until their own reviewed version exists.

Kinds constrain producer ownership. Every producer needs a transactional outbox
or qualified equivalent. Stream continuity is tenant-scoped and checked against
the independently supplied registered predecessor. Acknowledgements bind the full
event and payload digests plus qualified ledger position and receipt time. They
attest only to the specified validated durable append, not effect or completeness.

Historical recovery supplies a currently authorized recorder and independent
evidence of the exact original committed event, source generation and recovery
cutoff. It preserves bytes and sequence, and cannot grant new execution rights.
The offline oracle exercises that boundary with fictional retained facts; it does
not prove their persistence, signatures, production trust or restore custody.

## Owners, migration and evidence gate

Hub owns candidate generation, lock/export and reference oracles; Server owns the
new append path; Council/Registry own approvals and activation; Gate/Warden own
the action transaction and custody; Harness owns independent client and real-store
integration checks. Export pins a committed candidate revision and exact bundle.
Re-vendor into a new namespace only after consumer intake, preserving Stage 1.

The candidate's checks establish shape, bytes, selected cross-record bindings and
negative cases. They do not execute H03 crash histories or establish all EV cases.
The bundle README maps that distinction. Wire acceptance, independent consumer
conformance, human identity admission, signed evidence and effect qualification
remain separate gates. Existing service APIs must reject this profile until an
explicitly reviewed consumer implements it; there is no downgrade to Stage 1.
