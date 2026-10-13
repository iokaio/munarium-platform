# ADR 0018: retained journal checkpoints and governed restore reopening

**13 October 2026; experimental implementation directed; acceptance pending.**
This concretizes RECOVERY-01 under [ADR 0015](0015-stage2-linux-qualification.md)
and preserves [ADR 0010](0010-stage2-authority-durability.md)'s durability boundary.
Baseline: Server `a8e75ff6994cd946d69d651c9687abf0c5c3e2be`, Gate
`28f80b4054a45e29677cb72c495edefc701f47ab`, Harness
`a0594cfc2c206510d89e48775e736e5b917ae285` and the
[dynamic evidence](../stage2-implementation.md#full-dynamic-isolated-composition-13-october-2026).
Record exact fresh owner bases in each packet. Existing candidates/vectors remain
immutable; new operational adapters are experimental, not released wire versions.

## Required failure boundary

The current external recovery-generation mismatch quarantines a declared restore.
It does not detect a consistent older Gate snapshot when that external generation
has not changed. Server source-head lookup also cannot recover exact old custody:
operation lookup omits original ledger positions/receipt times. Send intent is local
before permission; its outbox may still be unacknowledged when the target changes.
Those are implementation gaps, not a reason to infer successful recovery.

Reopening must cover both acknowledged history and a transaction lost before its
outbox reached Server. A matching audit tail alone cannot prove the absence of
lost consumption, cancellations, reservations or spent send permission. Timers,
boolean resume, new operation IDs or a fresh database cannot erase that exposure.

## R1: pinned retained-record export

Add an authenticated `action-checkpoint` read to the existing Server records
REST/RPC dispatcher. It uses current action-record read admission, the actual
service peer, tenant/deployment/cell and protected ledger. The profile is
`stage2-recovery-checkpoint-v1`, with declared coverage
`action-artifacts-and-events`; it is not a journal-completeness or reopening proof.

The request selects an optional global ledger cutoff, continuation position and
bounded page limit. The first page may select current head; subsequent pages retain
that exact cutoff. Reject future/invalid cutoffs, invalid continuation/limits and
oversized records rather than dropping evidence. Authorization is current on every
page. Concurrent later writes cannot change an earlier pinned export.

Return qualified scope/ledger, cutoff, total record count, checkpoint digest,
retained per-stream/generation tails, page records and explicit continuation/
completion. Each record retains its global position, canonical producer bytes and
original archive receipt or event acknowledgement, including original receipt time.
The complete ordered record set and retained tails determine the same digest across
pages; page size/continuation cannot change it. Bound each page's encoded bytes and
count. Empty retained history is explicit. Retired historical sources remain visible
as retained facts, without being labelled current execution authority.

Consumers fetch their own complete pages, verify scope/ledger/cutoff, ordering,
counts, digests and exact receipts, and recheck current authority. They never accept
an agent-supplied checkpoint as proof. A partial export or digest mismatch refuses.
The export exposes neither credentials nor execution permission. This first packet
needs memory/PostgreSQL pin, pagination, retry, concurrent-write and tenant/refusal
tests, plus real REST/gRPC parity and current-binding removal controls.

## R2: independent coverage before effect-relevant journal mutation

Server retains an append-only, separately scoped operational checkpoint chain for
the enrolled Gate journal identity. Each effect-relevant mutation first records a
write-ahead intent against the exact independently committed prior checkpoint.
The intent binds qualified journal/owner/generation, operation/attempt, mutation
kind and conservative exposure footprint. It records possible work, not a claim
that consumption or dispatch already committed, and grants no execution rights.

Gate computes its actual canonical operational-state digest under its cell lock;
caller digests cannot establish that state. Coverage includes source/claim bindings,
cancellation and consumed-grant tombstones, worker/send state, all reservations,
outcomes/reconciliation, source/outbox sequences and exact acknowledgements,
activation/recovery enrollment and any read-side writes affecting these facts.
An independent prior checkpoint mismatch or outstanding unknown intent quarantines
admission before a new mutation. Fresh initialization requires a separately governed
empty-journal/empty-target baseline; an older or empty restored store cannot adopt
a new journal identity to bypass existing history.

Gate keeps consumption, worker ownership, all bucket reservations and outbox intent
atomic in its own PostgreSQL transaction. After commit it records the immutable
local commit receipt/state digest against that exact Server intent. Server's record
is retained producer evidence, not autonomous inspection of remote PostgreSQL.
Only then may the adapter publish the corresponding operational response. An
interrupted intent/commit exchange is never automatically treated as rolled back;
its conservative footprint stays charged until independently reconciled.

Consumption and send-intent custody must be independently retained before their
successful responses. Final permission remains one-shot: only the original live
admission path may finish acknowledgement and return permission. Restart/retry/
lookup cannot replace a lost reply or recover its private completion token. A late
acknowledgement, expired custody or changed authority leaves unresolved exposure.
Prepare the scoped Server recording identity before custody, following ADR 0017's
verification/retention principles for this separately admitted recording resource;
do not extend the five-second ticket or two-second clock bound.

Serialize journal admission/checkpoint exchange across instances. Owner reads used
by Warden/Council callbacks cannot deadlock that serialization, and no current-authority
fence is held across callbacks. Persist quarantine separately from activation pause.
Startup and each effect-relevant admission compare actual local state, independent
checkpoint and retained audit prefix. Unknown/missing/conflicting evidence refuses,
including undisclosed rollback and retained Server state moving backwards.

## R3: governed, durable reconciliation and reopening

Council coordinates a recovery plan approved by currently eligible distinct human
authority. Server's signed owner enrollment binds the exact plan, old journal/source
identities, independently retained cutoff/checkpoint digests and a strictly newer
external recovery epoch. Caller fields or an operator boolean cannot supply approval.

Exclude old dispatchers and establish the new target floor before restored workers
can start. Obtain the target's exact qualified floor receipt and independent effect
observations. Reconstruct through the frozen cutoff, importing immutable sources,
claims, approvals/cancellations, grants/consumptions, reservations, spent send
opportunities, outcomes and original acknowledgements. Reconcile pending checkpoint
intents and known committed outboxes; missing facts retain quarantine and conservative
exposure. Preserve history and minimal operation/tombstone identities indefinitely
under the first profile; never overwrite an uncertain outcome or refund by expiry.

Reconciliation is checkpointed/resumable and conflicts on changed plan/evidence.
Keep unresolved debt charged in every applicable new window. Separate per-source
generation/sequence from activation, recovery and target floors; retain old namespaces
and start fresh producer sequences only under new admitted source registration.
Historical outboxes drain original bytes in order under the existing exact
[recovery permits](0013-action-record-admission.md#historical-recovery), proving the
committed claim/source/cutoff. Audit delivery creates no grant or dispatch right.

Reopen only after the exact complete reconciliation, current participant/authority
heads, old-worker exclusion and target-floor receipts match the governed plan.
Persist that completion atomically with the new local recovery admission state.
Old operations/attempts remain closed to execution; only separately enrolled fresh
intent/context/approval may enter the reopened generation. No-effect settlement
requires its own explicit independent evidence and cannot be inferred from a missing
target row while an old dispatcher might still act.

## Packets and qualification

Proceed R1/Server export, R2/Server checkpoint plus Gate admission coverage, then
R3/Council/Warden/Gate/target adapters and Harness restores. Add any required closed
operational schemas through the documented candidate/export process; never edit an
existing candidate or applied migration. Each packet retains available local gates,
exact-head hosted checks, source pins, failed attempts and environment cleanup.

Harness must restore actual snapshots before and after effects and unacknowledged
journal commits, with and without declared epoch change. Missing pages/receipts,
conflicting prefix/footprints, unavailable owners, partial reconciliation, stale
workers, expired authority, lost reopening replies and pending old outboxes must
retain quarantine or immutable retry. Adjacent positives prove governed reopening,
held prior debt, no old resend and a new approved independent effect. Preserve all
activation/prepared/dynamic/isolation histories and existing checks.

The founder remains accountable owner/reviewer; independent human acceptance is
pending. Use the existing disposable local/CI authority, resource/expiry/cleanup
intake and eight-hour packet re-estimation boundary. No production trust, deployment,
paid run, release, catalog/invariant promotion or qualified reopening is created by
this decision or by the read-only export alone.
