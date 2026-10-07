# Architecture decision index

[Stage 1 source derivation and recovery](0009-stage1-recovery-profile.md) specifies
the first executable service profile's source verification and durable recovery.

A proposed record is not an accepted contract or release approval. Ordinarily,
cross-component semantic implementation waits for the applicable accepted decision
and versioned contract. The [Stage 1 development authorization](../stage1-authorization.md)
explicitly permits experimental implementation and testing against recorded candidates
while human acceptance remains pending. It does not accept or release those candidates.

| Record | State | Scope |
|---|---|---|
| [0001: scaffold boundaries](0001-scaffold-boundaries.md) | Proposed for maintainer review | Nine local Rust libraries, documentation-only hub, no runtime or wire semantics |
| [0002: action execution protocol](0002-action-execution-protocol.md) | Proposed for maintainer review | Single consumption owner, mandatory recording, bounded authority, cumulative action limits and recovery |
| [0003: bootstrap and principal context](0003-bootstrap-principal-context.md) | Proposed for maintainer review | HUB-01 authority, retirement, verification and semantic test oracles |
| [0004: decision-only contracts](0004-decision-only-contracts.md) | Proposed; acceptance evidence incomplete | HUB-02 canonical vectors, manifests, evaluation, minimum topology and events |
| [0005: Warden identity admission](0005-warden-identity-admission.md) | Proposed; not accepted | Provider identity mapping, registered delegation and attribution-only forwarding |
| [0006: Registry manifest admission](0006-registry-manifest-admission.md) | Proposed; implementation candidate present | DEC-02 signed artifacts, tenant/owner binding and recipient-bound candidate access |
| [0007: Stage 1 composition](0007-stage1-composition.md) | Proposed; implementation authorized | Decision-only component integration, independent clients, refusal/replay and retained run evidence |
| [0008: Stage 1 service boundary](0008-stage1-service-boundary.md) | Implementation directed; acceptance evidence pending | Durable bootstrap authority, authenticated services and client compatibility |
| [0009: Stage 1 recovery profile](0009-stage1-recovery-profile.md) | Implementation directed; human acceptance pending | Source derivation, immutable recording intent and authenticated recovery |
| [0010: Stage 2 authority and durability](0010-stage2-authority-durability.md) | Proposed for maintainer review | HUB-03 approval/activation, action records, reservations, effect profile and failure histories |
| [0011: platform contract evolution](0011-platform-contract-evolution.md) | Proposed for maintainer review | Second-pass identity/attempt binding, qualified context, shared events, coverage, profiles and later-component boundaries |

[HUB-02 evaluator comparison](evaluator-comparison.md) retains the synthetic OPA/Cedar
corpus and bounded runs. ADR 0007 subsequently selected OPA for experimental
Stage 1 implementation; formal DEC-03 acceptance remains pending in the
[review packet](../architecture/stage1-acceptance.md).
[HUB-02 evaluator adapter oracle](evaluator-adapter-oracle.md) adds executable typed
obligation/refusal fixtures and native mixed allow/error checks; it is not a runtime adapter.

Follow [CONTRIBUTING](../../CONTRIBUTING.md) and [GOVERNANCE](../../GOVERNANCE.md).
Future records name alternatives, evidence, owners, affected consumers, version policy and
consequences. The [contract backlog](../architecture/contract-backlog.md) identifies the next ones.

Record acceptance as an explicit maintainer disposition with the exact reviewed revision and
date; a merged preparation PR or compiled scaffold does not retrospectively accept ADR-0001's
proposed choices. Its status remains proposed pending that disposition. ADR-0002 likewise is a
candidate for review, not authorization to implement or activate a runtime contract. The
decision register distinguishes open questions from proposals with a concrete candidate.

[Foundation candidate schemas and signed vectors](candidates/README.md) supply
executable review inputs for ADR 0003/0004; they are not accepted or published contracts.

[Proposed Warden identity contract](warden-identity-contract.md) specifies the
WARDEN-01 consumer boundary against those unchanged candidates, with additional
offline checks of the exact principal result and decision-path refusal cases.

[Registry v2 candidate](registry-v2/README.md) supplies separate closed schemas, signed
artifact vectors and exact contract pins for REG-01; formal acceptance remains pending.
