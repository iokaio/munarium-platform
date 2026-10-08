# Parallel build plan for two development machines

**Proposed work allocation, 6 October 2026.** This applies the dependencies and acceptance gates in the [build plan](build-plan.md) to two development machines. It is a scheduling recommendation, not an accepted contract, implementation authorization or qualification result. The build plan and [decision register](architecture/contract-backlog.md#decision-register) remain authoritative for prerequisites. Component repositories own their code and tests.

The subsequent [Stage 1 development authorization](stage1-authorization.md) directs
implementation of both Stage 1 rows in one workspace, including their foundation
prerequisites and supporting CI. It permits experimental development against
recorded proposals while acceptance is pending. The acceptance and completion
gates below remain requirements for claiming Stage 1 complete.

Use the machines for two bounded tasks within the same delivery stage. Complete a working slice across repositories before advancing; each repository receives several increments rather than being finished in isolation. Machine assignments can change between packets.

**Current position, 7 October 2026.** Both Stage 1 rows have experimental service
implementations and recorded local integration evidence. HUB-03 candidate
preparation and Server's S2-A action-record path are merged through hub PR 14 and
Server PR 76. The [next-step plan](next-steps.md) now directs C2-A approval and
activation implementation, followed by G2-A execution and H2-A integration.
The [pinned acceptance packet](architecture/stage1-acceptance.md) remains unchanged:
implementation and merging do not close contract acceptance or qualification gates.

## Shared prerequisites

1. **Qualify the foundations in parallel.** Machine A inspects and tests Server; Machine B inspects and tests Matrix. Combine the results into FOUNDATION-01, retaining exact source revisions, actual outcomes and unavailable checks. The [foundation baseline](architecture/foundation-baseline.md) records that Matrix is already separate; do not repeat extraction.
2. **Accept the initial hub contracts.** Resolve bootstrap/principal identity, canonical requests, manifests, evaluation, minimum identity/topology and event records through HUB-01/02. The second machine can investigate foundation gaps and prepare tests while decisions are reviewed. The scoped Stage 1 authorization permits experimental runtime implementation against recorded candidates; acceptance is still required to close this gate.
3. **Complete the required Server foundation changes.** Implement only confirmed gaps against the shared decisions, using the Stage 1 experimental authorization while acceptance is pending. Pass the S1 authority gate and supply the required S2 record shapes, S3 principal verification and S4 lineage support for the first integrated slice. Use the [foundation requirements](architecture/foundation-requirements.md) and Server's own tests; a planning description is not evidence that a gap exists or has been closed.

## Development sequence

The [Stage 1 implementation record](architecture/stage1-implementation.md) tracks the
single-workspace implementation, actual experimental runs and remaining acceptance gates.

The rows below are a recommended order within the build plan's stages. Normally,
two tasks in a row proceed once their shared contracts and individual prerequisites
are accepted; the scoped Stage 1 experimental authorization is the exception for
development, not completion. The completion column is an integration gate, not
merely two successful component builds.

| Order / stage | Machine A | Machine B | Completion gate |
|---|---|---|---|
| 1 / Stage 1: identity and inventory | **Registry:** candidate manifest validation and resolution | **Warden:** identity verification and delegation attenuation | Both conform to accepted contracts; candidates remain inactive. |
| 2 / Stage 1: decision-only path | **Gate:** deterministic evaluation and replay | **Harness:** typed proposals, canonicalization and outcome handling | Integrate with Registry, Warden and Server; pass REF-01 and the Stage 1 manifest, lineage and tenant refusal cases, retaining an experimental run record. |
| 3 / Stage 2 preparation | **Platform hub:** approval, execution, action-limit and durability decisions through HUB-03 | **Server:** inspect S7/S9 seams; implement confirmed gaps after their decisions are accepted | Accepted action contracts and required foundation gates before effect-producing work. |
| 4 / Stage 2: approval and activation | **Council:** request-bound approval and activation authority | **Registry:** activation, version compatibility and retired-artifact handling | Approval and activation work together with exact request/artifact bindings and recovery behavior. |
| 5 / Stage 2: controlled execution | **Gate:** durable journal, action reservations and disposable connector | **Warden:** grants, credential broker, consumption and revocation | Update Harness recovery handling, then pass REF-02–19 against actual persistence and isolation, including crash recovery and restore quarantine. Retain installation and investigation instructions. |
| 6 / Stage 3: model access | **Gateway:** extraction consumer, routing and model budgets | **Server:** S8 extraction and compatibility work | Preserve existing Server behavior before expanding model admission; test concurrent budget reservation and uncertain settlement. |
| 7 / Stage 3: operational visibility | **Sentinel:** timeline reconstruction and suspension | **Server:** S6 telemetry and authoritative event delivery | Rebuild, missing-event and suspension tests pass, including measured suspension acknowledgement. |
| 8 / Stage 3: operator interface | **Console:** read-only views, then governed commands | Integration, tenant/session tests and foundation maintenance | UI follows the same authority checks as headless APIs, with session and tenant isolation verified. |
| 9 / Stage 4: independent evidence | **Assure:** evidence packaging and offline verification | **Server:** S5 checkpoints, retention and recovery support | Pass REF-20 and full retention, upgrade and recovery exercises; retain gaps and immutable composition inputs. |

After each integration gate, review the evidence before starting the next major slice. Additional providers, connectors, identity profiles, federation and availability work remain demand-led Stage 5 packets with their own environments and acceptance evidence.

## What parallel implementation requires

Gate and Harness can develop against the same accepted request/outcome vectors before both runtimes are ready. Council and Registry can similarly use accepted approval/activation definitions, and Gate and Warden can use the accepted execution protocol. Fixtures allow independent implementation; they do not replace integration tests against the real components, supported persistence and deployment boundaries.

The [contract backlog](architecture/contract-backlog.md) identifies the blocking decisions. Pin both tasks to the same accepted contract revision and golden vectors. Changes to a shared definition return to the hub's decision process before consumers implement incompatible behavior.

Keep Console out of the first action milestone: Council's minimal authenticated interface is sufficient. Assure verification must work without Console. Gateway's model-spend budget and Gate's cumulative action limits remain separate responsibilities.

## Working across the two machines

- Give each active packet one owner, a separate branch, an explicit target repository and permitted files. Include the inputs, commands, environment, acceptance reviewer and limits required by the [work-packet rules](build-plan.md#work-packets-and-capacity).
- Assign shared Server and hub edits to one machine at a time. Their presence in every focused workspace does not imply concurrent editing or authorization to widen a component task.
- Use the target component workspace with Server and the hub available as references. Open additional component repositories only for a bounded integration task that requires them.
- Exchange reviewed changes through Git and record exact component revisions for integration. Synchronize accepted contract changes before continuing dependent work; do not treat two floating branches as a compatible composition.
- Preserve the [governance work-in-progress limit](../GOVERNANCE.md#the-work-packet-and-the-limits-on-parallel-work): one major capability slice, one foundation maintenance lane, and no more than two bounded implementation tasks awaiting substantive review. A second machine adds execution capacity, not a second human acceptance authority.
- Retain failed and unavailable checks alongside successful results in the [experimental run record](architecture/reference-scenario.md#experimental-run-record-from-the-first-integrated-slice). Passing local tests does not establish remote CI, qualification or release approval.

## First pair to start

The original starting pair was Server and Matrix qualification, recorded in
[FOUNDATION-01](architecture/foundation-01.md). Do not repeat extraction or
restart implemented Stage 1 packets from their scaffold descriptions. The current
next pair is **Council approval on Machine A and Registry activation storage on
Machine B**, under [ADR 0014](decisions/0014-stage2-service-integration.md).
Complete activation also requires Gate's durable pause/resume and matching
Server/Warden participant adapters before the integrated barrier can pass.
Use the [implementation packet](stage2-implementation.md) and
[next-step plan](next-steps.md) for scope and evidence gates; re-estimate from
observed runtime availability before assigning dates.
