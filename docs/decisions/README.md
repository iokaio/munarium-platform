# Architecture decision index

A proposed record is not an accepted contract or release approval. Cross-component semantic
implementation waits for the applicable accepted decision and versioned contract.

| Record | State | Scope |
|---|---|---|
| [0001: scaffold boundaries](0001-scaffold-boundaries.md) | Proposed for maintainer review | Nine local Rust libraries, documentation-only hub, no runtime or wire semantics |
| [0002: action execution protocol](0002-action-execution-protocol.md) | Proposed for maintainer review | Single consumption owner, mandatory recording, bounded authority, cumulative action limits and recovery |

Follow [CONTRIBUTING](../../CONTRIBUTING.md) and [GOVERNANCE](../../GOVERNANCE.md).
Future records name alternatives, evidence, owners, affected consumers, version policy and
consequences. The [contract backlog](../architecture/contract-backlog.md) identifies the next ones.

Record acceptance as an explicit maintainer disposition with the exact reviewed revision and
date; a merged preparation PR or compiled scaffold does not retrospectively accept ADR-0001's
proposed choices. Its status remains proposed pending that disposition. ADR-0002 likewise is a
candidate for review, not authorization to implement or activate a runtime contract. The
decision register distinguishes open questions from proposals with a concrete candidate.
