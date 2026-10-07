# Cross-component contract backlog

**Design backlog; no published contract versions.** Derived from
[platform plan revision 4](../platform-plan.md), sections 7–19 and Appendices C–D.
Stage 1 now has proposed schemas/vectors and experimental consumers. The
[acceptance packet](stage1-acceptance.md) records their exact inputs and open
dispositions. Remaining scaffold interfaces are not shared wire contracts or
permission to choose incompatible definitions. [HUB-03](../decisions/0010-stage2-authority-durability.md)
prepares the next action boundary without accepting or activating it.

## Decision register

The founder is the accountable design owner and acceptance authority for every row until a
named maintainer accepts that responsibility. Component names below identify technical owners,
not separate people or implicit approvals. IDs identify design questions, not accepted ADRs.
Each decision closes only with a reviewed ADR, pinned candidate evidence, consumer migration
notes, and the accepted contract/vectors needed by its blocked packets. A timebox that expires
produces a gap and revised estimate; it does not select a dependency by default.

| ID / state | Technical owners | Decision, alternatives and bounded investigation | Blocks / first gate |
|---|---|---|---|
| DEC-01 / proposed ADR-0003 | Server, Warden, Council | [Bootstrap and principal proposal](../decisions/0003-bootstrap-principal-context.md): compare explicit transition attestation with existing Server authority seams; define issuer/audience, service origin, attenuation, retirement and replay protection. Inspect source and produce valid/forged/delegated/retired-key vectors in a 12–20 hour design packet. | S1; WARDEN-01; Stage 0–1 |
| DEC-02 / proposed ADR-0004/0006 | Registry, Gate, Harness, Server | [Decision-only proposal](../decisions/0004-decision-only-contracts.md): compare restricted canonical JSON with an existing canonicalization standard against duplicate keys, numbers, Unicode, defaults and attachment limits. Bind tenant, target, operation identity, policy/manifest digests, enforcement mode and activation epoch; distinguish candidate from active. [Manifest admission proposal](../decisions/0006-registry-manifest-admission.md) adds artifact signatures, tenant/owner binding and exact-byte identity; the [Registry v2 candidate](../decisions/registry-v2/README.md) supplies separate schemas and signed artifact vectors for the authorized local experiment. Formal acceptance remains pending. 12–20 hours, re-estimate remaining integration work at intake. | REG-01, GATE-01, HARNESS-01; S2–S4; Stage 1 |
| DEC-03 / experimental choice; acceptance pending | Gate, Harness | [ADR 0007](../decisions/0007-stage1-composition.md) implements pinned Windows OPA 1.21.1; Harness has independent Rust/Python clients. The [comparison](../decisions/evaluator-comparison.md) remains review evidence. Formally dispose the engine/profile and client scope in the acceptance packet; Linux worker qualification remains a Stage 2 profile dependency. | GATE-01, HARNESS-01 acceptance; Stage 2 profile |
| DEC-04 / proposed ADR-0010 | Council, Registry, Server | [HUB-03](../decisions/0010-stage2-authority-durability.md) proposes distinct human approval with exact bindings and a resumable artifact-set activation barrier. Resolve human admission and partial-transition recovery; no cross-store atomicity claim. Original 12–20 hour design range is re-estimated at intake. | COUNCIL-01–03, REG-02, Council trust transition; Stage 2 |
| DEC-05 / proposed ADR-0002/0010 | Gate, Warden, Server | [Execution protocol](../decisions/0002-action-execution-protocol.md) retains one Gate consumption owner; [HUB-03](../decisions/0010-stage2-authority-durability.md) adds concrete failure histories and consumer work. Real-store crash/fencing/restore evidence remains required; original 16–24 hour design estimate needs intake revision. | GATE-02–04, WARDEN-02–04, S9; Stage 2 |
| DEC-06 / proposed ADR-0002/0010 | Gate; Gateway consulted | Atomic action-capacity reservation and unresolved carry-over remain separate from model spend. HUB-03 defines the two-publication admission oracle and concurrent/window-rollover histories; no runtime qualification yet. | GATE-02–03; C2/C3 aggregate-limit claims; Stage 2 |
| DEC-07 / Stage 1 implemented; effect profile proposed | Warden, Gate, Server; all deployable components | Direct mTLS and workload admission exist under ADR 0008. The [foundation assessment](stage2-foundation-assessment.md) identifies unqualified agent/credential/network edges. HUB-03 recommends the [Linux effect profile](reference-profile.md), with new evaluator qualification and exact IdP/broker pins still required. | Stage 1 acceptance; S7, WARDEN-03 and Stage 2 action scenario |
| DEC-08 / Stage 1 implemented; action extension proposed | Server, Sentinel, Assure, Harness | Stage 1 has proposal/decision/refusal records and archives. HUB-03 proposes a separately versioned action path and mandatory outbox/acknowledgement bindings; the current single-result conflict rule cannot represent the full lifecycle. S6 export and S5 verification remain later work. | S2 action records; S6, SENTINEL-01, ASSURE-01 |

These are provisional founder effort ranges, including design review, not delivery commitments
or implementation estimates. Re-estimate at packet intake from observed work. No paid test
environment or reviewer availability is assumed. Later decisions separately cover Gateway
admission/settlement, browser/session architecture and federation before those packets begin.

## Definitions in dependency order

The [platform-wide second pass](platform-contract-review.md) supplements DEC-01–08
with [ADR 0011](../decisions/0011-platform-contract-evolution.md). Its next-cut
requirements cover stable identity/attempts, qualified references and epoch scopes,
activation participant sets, common event envelopes, typed obligations and profile
compatibility. Coverage/export, invocation settlement, UI, suspension and federation
remain later implementation packets. Existing candidate schemas and locks stay
unchanged; accepting Stage 1 does not accept these future contracts implicitly.

The subsequent [ADR 0012](../decisions/0012-stage2-candidate-profile.md) and
[Stage 2 candidate](../decisions/stage2-v1/README.md) make those next-cut choices
reviewable as closed schemas and fixed vectors. Their offline evidence is separate
from pending exact-wire acceptance, consumer conformance and runtime qualification.

| Design item | Responsible design owners / consumers | Questions and acceptance vectors required before implementation |
|---|---|---|
| Principal context | Warden and Server; Gate, Council, Registry, Gateway | Verified tenant/origin/actor evidence, issuer/audience/expiry, narrowing, depth/cycles and forbidden ratifier transitions |
| Manifest and activation | Registry and Council; Gate, Server | Immutable identity/digest, schema compatibility, target/environment, credential audience, effect/idempotency/compensation, expected prior epoch, attestation and cache revocation |
| Action proposal and canonicalization | Hub specification with Gate and Harness | Included fields, defaults, encoding, ordering, bounded attachments, numeric/money representation, rejected ambiguity, exact accepted bytes/digests; DEC-02 |
| Decision and provenance snapshot | Gate and Server; Council, Harness, Assure | Pinned policy/evaluator/manifest, source revisions, trust scope, authoritative field binding, C0–C4 with upward-only modifiers, obligations and missing inputs; applied enforcement mode and activation epoch, distinct shadow result and enforceable decision |
| Approval and bootstrap transition | Council and Server; Registry, Gate, Warden | Exact-request/context binding, distinct authority, quorum, expiry, target preconditions, explicit non-agent bootstrap scope and retirement |
| Claim, grant and consumption | Gate and Warden with Server S9 | Stable semantic operation identity, conflict on changed content, atomic consumption/acquisition, fencing, crash points, revocation and restore |
| Outcome and reconciliation | Gate and Harness; Console, Server, connectors | [Lifecycle](action-lifecycle.md): denied, approval-required, API admission, completed, failed-before-dispatch, sent-with-proven-no-effect, predispatch cancellation and unresolved; recording-pending is distinct; lookup without resubmission, compensation as a linked new action |
| Invocation and budget | Gateway with Server S8; Harness, Sentinel | Root/child reservations, durable admission, price assumptions, exact/conservative/token-only bounds, streaming, cancellation and corrections |
| Action cumulative limits | Gate with durable claim owner; Server records, Gateway vocabulary | Counter scope/window, atomic reservation, concurrent requests, pending/unresolved holds, governed reconciliation and retention; DEC-06 is separate from model-spend admission |
| Events, coverage and suspension | Server and Sentinel; Warden, Console, Assure | Source IDs, watermarks, missing intervals, pinned telemetry convention, authenticated scope/duration and measured suspension acknowledgement |
| Evidence package and composition | Assure with Server; all component maintainers | Boundary, exact versions/digests, ranges, signatures/trust context, omissions, retention, independent verification and compatibility evidence |
| Federation constraints | Council, Registry and Warden; Gate | Mandatory parent prohibitions, local restrictions, both-domain permission and degraded operation; Stage 5 |

## Decisions that block advancement from Stage 1

1. Review the recorded FOUNDATION-01 gaps alongside the subsequent Stage 1
   authority implementation and exact-revision CI. Do not schedule delivered work again.
2. Formally dispose DEC-01/02/03 and minimum DEC-07/08 against the pinned
   [acceptance packet](stage1-acceptance.md). The Stage 1 grant permitted
   experimental implementation while these dispositions were pending; it grants no dispatch authority.
3. Accept and version the definitions/vectors through their own review; this planning PR does
   not publish a contract. Pin each consumer's exact bundle digest.
4. Resolve DEC-04–07, DEC-08's mandatory recording semantics and ADR 0011's
   next-cut requirements before effect-producing work.
   A protocol spike using fake storage is design evidence, not concurrency qualification.
5. Qualify Stage 2 against the real selected persistence and isolation boundary, including
   restore quarantine and action reservations. Later packaging cannot defer these safety gates.

OPA and Rust/Python clients are implemented experimental Stage 1 choices, with
formal acceptance pending. ADR 0002 and HUB-03 propose the effect persistence,
identity and isolation profile; they do not qualify those dependencies or imply
that remaining scaffold components have selected their runtime stacks.

## Acceptance and change policy

A future contract proposal includes owner, consumers, threat assumptions, valid and invalid
vectors, compatibility/version policy and a migration plan. Cross-language consumers must compare
bytes, digests, error codes and outcome interpretation. Concurrent and recovery claims require
tests of the real supported persistence protocol, not just schema validation.

Accepted normative definitions will live in the hub's contract artifacts under its review process;
runtime libraries remain with one owning component or the foundation. Harness-generated bindings
identify the exact contract digest. New schemas and vectors receive their checks when introduced.
Until then Appendix D examples remain illustrative.

Use expand, migrate, remove for breaking changes. Record compatibility against immutable component
revisions in a tested composition; matching package version numbers or floating main branches
are not evidence of compatibility.
