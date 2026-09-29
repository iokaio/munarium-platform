# Cross-component contract backlog

**Design backlog; no published contract versions.** Derived from
[platform plan revision 4](../platform-plan.md), sections 7–19 and Appendices C–D.
The current Rust associated types are unspecified local interfaces. They are not shared
wire schemas, generated bindings or permission to choose incompatible definitions.

## Definitions in dependency order

| Design item | Responsible design owners / consumers | Questions and acceptance vectors required before implementation |
|---|---|---|
| Principal context | Warden and Server; Gate, Council, Registry, Gateway | Verified tenant/origin/actor evidence, issuer/audience/expiry, narrowing, depth/cycles and forbidden ratifier transitions |
| Manifest and activation | Registry and Council; Gate, Server | Immutable identity/digest, schema compatibility, target/environment, credential audience, effect/idempotency/compensation, expected prior epoch, attestation and cache revocation |
| Action proposal and canonicalization | Hub specification with Gate and Harness | Included fields, defaults, encoding, ordering, bounded attachments, numeric/money representation, rejected ambiguity, exact accepted bytes/digests |
| Decision and provenance snapshot | Gate and Server; Council, Harness, Assure | Pinned policy/evaluator/manifest, source revisions, trust scope, authoritative field binding, C0–C4 with upward-only modifiers, obligations and missing inputs |
| Approval and bootstrap transition | Council and Server; Registry, Gate, Warden | Exact-request/context binding, distinct authority, quorum, expiry, target preconditions, explicit non-agent bootstrap scope and retirement |
| Claim, grant and consumption | Gate and Warden with Server S9 | Stable semantic operation identity, conflict on changed content, atomic consumption/acquisition, fencing, crash points, revocation and restore |
| Outcome and reconciliation | Gate and Harness; Console, Server, connectors | Denied, approval-required, accepted-for-execution, completed, failed-before-dispatch, unresolved; lookup without resubmission, compensation as new action |
| Invocation and budget | Gateway with Server S8; Harness, Sentinel | Root/child reservations, durable admission, price assumptions, exact/conservative/token-only bounds, streaming, cancellation and corrections |
| Events, coverage and suspension | Server and Sentinel; Warden, Console, Assure | Source IDs, watermarks, missing intervals, pinned telemetry convention, authenticated scope/duration and measured suspension acknowledgement |
| Evidence package and composition | Assure with Server; all component maintainers | Boundary, exact versions/digests, ranges, signatures/trust context, omissions, retention, independent verification and compatibility evidence |
| Federation constraints | Council, Registry and Warden; Gate | Mandatory parent prohibitions, local restrictions, both-domain permission and degraded operation; Stage 5 |

## Decisions that block the first usable increment

1. Pin and qualify the foundation, then settle S1 bootstrap and verified principal context.
2. Decide the manifest, proposal/canonicalization and decision snapshot together.
3. Select one evaluator using a bounded comparison: expressiveness, deterministic execution,
   schema support, integration effort, resource bounds and testability.
4. Publish reviewed vectors and then implement Registry lookup, Gate replay and Harness clients.
5. Before effect-producing work, resolve approval, claim/grant consumption, connector boundary,
   durable acknowledgements and restore semantics as a coordinated design.

Cedar and OPA/Rego remain candidates from the plan, not selected dependencies.
Database, async runtime, HTTP framework, identity library, signing format, browser framework
and practical application-client language are likewise not selected by the scaffold.

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
