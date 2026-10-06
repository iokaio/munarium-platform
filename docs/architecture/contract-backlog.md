# Cross-component contract backlog

**Design backlog; no published contract versions.** Derived from
[platform plan revision 4](../platform-plan.md), sections 7–19 and Appendices C–D.
The current Rust associated types are unspecified local interfaces. They are not shared
wire schemas, generated bindings or permission to choose incompatible definitions.

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
| DEC-02 / proposed ADR-0004 | Registry, Gate, Harness, Server | [Decision-only proposal](../decisions/0004-decision-only-contracts.md): compare restricted canonical JSON with an existing canonicalization standard against duplicate keys, numbers, Unicode, defaults and attachment limits. Bind tenant, target, operation identity, policy/manifest digests, enforcement mode and activation epoch; distinguish candidate from active. 12–20 hours. | REG-01, GATE-01, HARNESS-01; S2–S4; Stage 1 |
| DEC-03 / open | Gate, Harness | [Evaluator comparison](../decisions/evaluator-comparison.md) informs the still-open selection of one evaluator and application client. Compare Cedar and OPA/Rego with the same allow/deny/approval-required corpus, bounded execution, deterministic replay and unavailable-input cases; compare Python/.NET client effort on the same vectors. 8–16 hours, no live providers. | GATE-01, HARNESS-01; Stage 1 |
| DEC-04 / open | Council, Registry, Server | Approval/activation: compare single-artifact transitions with coordinated multi-artifact activation; define approver eligibility, exact bindings, veto/expiry and partial activation recovery. DEC-01 already owns minimum bootstrap retirement; this extends it to Council promotion. No claim of atomic updates across independent stores. 12–20 hours. | COUNCIL-01–03, REG-02, Council trust transition; Stage 2 |
| DEC-05 / proposed ADR-0002 | Gate, Warden, Server | [Execution protocol](../decisions/0002-action-execution-protocol.md): compare Gate-owned consumption with separate-store coordination; test crash/acknowledgement, fencing, revocation and restore histories. 16–24 hour protocol review/spike before runtime work. | GATE-02–04, WARDEN-02–04, S9; Stage 2 |
| DEC-06 / proposed ADR-0002 | Gate; Gateway consulted | Action cumulative limits: transactionally reserve action capacity with claim admission; compare per-action versus task/tenant/window scope, unresolved holds and reconciliation. Share vocabulary with model budgets without creating two owners of one balance. 8–12 hours; include a concurrent over-limit history. | GATE-02–03; C2/C3 aggregate-limit claims; Stage 2 |
| DEC-07 / proposed profile | Warden, Gate, Server; all deployable components | [Local profile](reference-profile.md): select minimum decision-only identity/topology in HUB-02, then broker/storage/effect isolation in HUB-03; pin artifacts, assess licenses and maintainability, and prove the credential boundary. 8–16 hours total selection, split at intake; isolation implementation separately estimated. | WARDEN-01/Stage 1 installation; S7, WARDEN-03 and Stage 2 action scenario |
| DEC-08 / open with proposed evidence shape | Server, Sentinel, Assure, Harness | [Event/run evidence](reference-scenario.md): source IDs, ordering, deduplication, ranges, omissions, retention and independently supplied trust roots; compare polling with outbox-fed delivery. 8–16 hours; define minimal Stage 1 records before Stage 3 telemetry and Stage 4 verifier. | S2, S6, SENTINEL-01, ASSURE-01; first integrated run |

These are provisional founder effort ranges, including design review, not delivery commitments
or implementation estimates. Re-estimate at packet intake from observed work. No paid test
environment or reviewer availability is assumed. Later decisions separately cover Gateway
admission/settlement, browser/session architecture and federation before those packets begin.

## Definitions in dependency order

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

## Decisions that block the first usable increment

1. Record FOUNDATION-01 observations and qualification gaps. Settle DEC-01 before S1 changes;
   the audit must not automatically schedule changes already delivered upstream.
2. Resolve DEC-02 and DEC-03 together with minimum DEC-08 event/run records. Implement Stage 1
   Warden identity verification, Registry candidate resolution, Gate replay and Harness clients
   only against accepted definitions. A decision-only fixture has no dispatch authority.
3. Accept and version the definitions/vectors through their own review; this planning PR does
   not publish a contract. Pin each consumer's exact bundle digest.
4. Resolve DEC-04–07 and DEC-08's mandatory recording semantics before effect-producing work.
   A protocol spike using fake storage is design evidence, not concurrency qualification.
5. Qualify Stage 2 against the real selected persistence and isolation boundary, including
   restore quarantine and action reservations. Later packaging cannot defer these safety gates.

Cedar and OPA/Rego remain candidates from the plan, not selected dependencies.
Database, async runtime, HTTP framework, identity library, signing format, browser framework
and practical application-client language are not selected by the scaffold. ADR-0002 and the
reference profile now propose specific persistence/identity choices for review; they do not
make those dependencies accepted or qualified.

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
