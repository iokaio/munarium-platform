# Stage 1 closeout and Stage 2 preparation

**Maintainer-directed preparation, 7 October 2026.** The maintainer approved the
next-step plan: prepare Stage 1 acceptance evidence, reconcile stale planning
text, develop HUB-03 proposals and assess Server S7/S9 in parallel. This is the
scope of the current packet. Specific contract acceptance, effect implementation,
publication, merge and operational activation remain separate decisions.

**Follow-on direction:** after reviewing and merging this packet in PR 13, the
maintainer directed the [Stage 2 contract candidate packet](stage2-contract-packet.md).
That packet records the selected design basis and its new schema/vector work;
this page retains the original closeout scope and evidence.

## Current result and next gate

Both Stage 1 rows have implementations and recorded local integration evidence.
The [acceptance packet](architecture/stage1-acceptance.md) pins the six source
revisions and candidate digests, checks component CI and identifies missing review
and composition evidence. The [foundation assessment](architecture/stage2-foundation-assessment.md)
confirms existing mTLS and command recovery, and identifies action-record,
transaction and isolation work still required.

[ADR 0010](decisions/0010-stage2-authority-durability.md) is the concrete HUB-03
proposal for approval, activation, action durability, reservations and the effect
profile. It retains ADR 0002's single Gate transaction owner and adds a crash-point
review matrix. Proposed does not become accepted through these documents.

The maintainer requested a second pass against the whole platform plan.
[The findings](architecture/platform-contract-review.md) and
[ADR 0011](decisions/0011-platform-contract-evolution.md) now extend HUB-03 with
durable identity/attempt binding, qualified context and epochs, scoped activation,
shared event families and explicit later-component boundaries. Settle its next-cut
requirements before freezing action schemas; retain Gateway, Sentinel, Assure,
Console and federation implementation in their planned stages.

## Bounded work packets

| Packet | Inputs and permitted scope | Deliverable / exit |
|---|---|---|
| CLOSE-01 / hub | Stage 1 pins in the acceptance packet; hub documentation and review metadata only | Evidence map, exact-revision CI observations, preserved gaps and a human disposition for each blocking contract |
| HUB-03 / hub | Stage 1 definitions, ADR 0002 and full-platform second pass; design records and synthetic contract/vector preparation | Reviewed ADR 0010/0011 semantics, next-cut findings and negative cases; approval/activation, identity/attempt, action transaction, shared records and profile/version decisions explicit |
| FOUNDATION-02 / Server inspected | Server `7cc0c97`; read-only source/test inspection and relevant existing offline checks | S7/S9 evidence map plus confirmed S2 action-record gap; no speculative extraction or unrelated TLS rewrite |

The founder is the accountable owner and acceptance authority under governance.
No independent reviewer is assigned. Preparation permits local public-source
inspection and existing offline tests, with no paid resources or external model
calls. Do not convert design estimates into an instruction to spend. Remaining
implementation/review estimates and environment availability are re-estimated at
the next packet intake; their absence blocks scheduling effect qualification,
not this bounded preparation. Each runtime packet must supply the complete intake
fields in [the build plan](build-plan.md#work-packets-and-capacity).

Work is isolated from main and unrelated worktrees. Candidate bundles, public API
compatibility, trusted approval/release workflows, signing and catalog/invariant
labels stay unchanged. Evidence lives in the indexed hub records; raw local test
outputs remain local and are never promoted into public fixtures indiscriminately.

## After the review gate

1. Record bounded Stage 1 dispositions and accepted ADR 0010/0011 revisions with
   the exact profile. Resolve CR-01–06/08/10/12 next-cut requirements; retain the
   later consumer gates in the review. Prepare versioned action request,
   approval/activation and shared-envelope/action-payload schemas and negative vectors;
   export and re-vendor through the owners' documented process. Obtain the bounded
   Stage 2 implementation direction against these concrete inputs.
2. **Foundation:** add Server's compatible action-record path; qualify the selected
   effect topology and Gate's Linux evaluator profile if that proposal is accepted.
   Preserve Stage 1 and legacy command behavior. Implement only confirmed gaps.
3. **Council + Registry:** exact-request approval, distinct human authority,
   compatibility/retirement and resumable activation. Run without target dispatch
   until the execution protocol and environment gates are met.
4. **Gate + Warden:** atomic claims/consumption/reservations, bounded validation,
   isolated broker/connector, final-send fencing and durable outcome recovery.
5. **Harness integration:** REF-02–19 with real persistence, denied edges,
   independently observed target effects, crash/restore controls and an operator
   investigation/cleanup recipe. Retain failures and unavailable cases.

Use one major capability slice and one foundation maintenance lane, with no more
than two bounded implementation tasks awaiting substantive review. Hub and Server
edits each have one owner at a time. Console, Gateway, Sentinel and Assure remain
in their later stages. The immediate milestone is one approved, controlled,
recoverable action against a disposable target, not a production deployment.

## Environment intake before effect qualification

The Linux cell, PostgreSQL journal, human IdP and broker are proposed choices.
No installed or available environment is claimed. Before scheduling the run,
record owner, observed availability, immutable image/tool pins, cost authority,
resource ceiling, expiry, credential custody and teardown. Reuse disposable
resources only when ownership and isolation are established. The prior Windows
decision profile does not qualify a Linux worker or container network boundary.

Stop admission/qualification on missing accepted inputs, unavailable required
dependencies, unknown authority, failed recording, missing isolation, unresolved
restore evidence or failed independent effect counts. Preserve the receipt;
never weaken the oracle or rename an unavailable case as passed.

## Preparation validation and review size

Local hub checks on 7 October passed: license headers/texts, documentation links
and indexes, all 60 Python regression tests, the private-material scan of this
isolated worktree and `git diff --check`. The local gitleaks executable was
unavailable; no local secret-scan success is claimed. Existing exact-revision
remote hygiene success is recorded separately in the acceptance packet and does
not validate this uncommitted preparation diff.

The packet exceeds 500 changed non-generated lines because one review must connect
the pinned Stage 1 evidence, confirmed foundation gaps, proposed action semantics
and reconciled scheduling documents. The machine-readable review inputs are
generated from committed public source; their contract hashes and vendor byte
comparisons were checked. No generated runtime artifact or contract bundle changes.
Component implementation remains in subsequent bounded packets after the review
gate, so this preparation does not mix runtime changes across repositories.
