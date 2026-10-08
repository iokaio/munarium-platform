# 0014: bounded Stage 2 service integration

**Experimental implementation directed, 7 October 2026; acceptance and
qualification pending.** The maintainer requested implementation of the
[next-step plan](../next-steps.md), tests, a second review pass and component PRs
with passing CI. This includes the source, additive storage, disposable tests and
build/test workflows needed for that plan. It grants no merge, release,
production deployment, paid-resource or production credential authority.

## Inputs and ownership

Use hub `d51aa1681a18ab57687f88f92cf07565b0f77df2`, Server
`61a350a98953837e2b1b6564608c5b6957873ae9` and the unchanged stage2-v1 bundle
`8aca66588c87107a0c7a7720c68f921dfd2bdcaecf6433728afa4b1c51420aa6`.
ADR 0010-0013 remain the semantic basis. Export candidates using the hub tool;
never modify their schema, vectors or lock in a consumer. Preserve Stage 1 APIs.

Council owns approval and transition coordination; Registry owns artifact
compatibility and activation; Gate owns action transactions and final admission;
Warden owns current grant/custody authority; Server owns protected audit custody;
Harness owns the independent target and composition oracle. Runtime APIs below
are experimental adapters, not publication of a new normative wire version.

## Authenticated service boundary

Reuse Warden's owner-exported direct mTLS transport, certificate enrollment and
bounded request/response handling. No forwarding header establishes identity.
Service calls bind the actual peer, tenant and recipient. Current authority is
read from the authenticated Server boundary; dependency failure refuses new
authority. Durable lookup remains non-executable.

Council's initial human admission is a separately operator-enrolled mTLS peer
mapped to a qualified human principal and current eligibility revision. The
current governing binding explicitly lists the peer, principal, tenant and
permitted approval scope. Workload assertions cannot assign human kind. This
profile proves credential/account separation, not two independent humans, and
does not claim general OIDC integration. A production identity-provider adapter
requires its own intake and tests.

Council obtains canonical request/decision records from an authenticated owner
lookup, not a caller-supplied approval summary. The service rejects unknown
fields, oversized/noncanonical records, foreign scope and mismatched digests.
Approval creation and its outbox are one local transaction. Exact retries return
the original approval and expiry alongside separately reported current status.
Eligibility changes and expiry invalidate current use without rewriting history.

## Approval withdrawal and activation

Withdrawal records a stable withdrawal ID and pending status. Council asks Gate
to commit a cancellation tombstone keyed by approval and operation/attempt.
Gate serializes cancellation against final admission and returns a bound durable
receipt: cancelled before admission or too-late after admission. Only that receipt
can complete withdrawal; lookup and lost replies cannot imply cancellation.

Activation uses the unchanged candidate transition and receipt records. Council
stores ratification and coordinator progress, obtains Gate's durable pause,
applies Registry/Server/Warden changes under the same transition, applies Gate's
epoch while paused and resumes only with the complete authenticated receipt set.
Every participant exposes exact-transition retry/lookup and expected-prior-state
conflicts. No service writes another owner's tables. An effective Registry pointer
is not a completed cell transition. Failed or partial transitions remain paused.

The minimal participant adapters are prerequisites of C2-A integration, even
though the complete Gate/Warden execution services belong to G2-A. Tests may
exercise these adapters with dispatch unavailable. Coordinator and participant
state changes must commit with their own durable outbox.

## Action transaction and target boundary

Gate uses PostgreSQL for action claims, attempt closure, cancellation, grant
consumption, worker fences, cumulative reservations and durable outboxes.
Consumption, worker acquisition, all bucket reservations and predispatch intent
share one transaction. Lock ordering is deterministic. Expiry, restart, new
attempts and UTC-hour rollover never refund unresolved exposure.

Warden issues once against an authenticated immutable claim and current approval,
context and authority. Identical retry never renews expiry. The connector alone
receives target credentials. Final admission checks the live invocation, worker
fence, grant/custody validity, current authority and exact predispatch audit
acknowledgement, then durably records send intent before returning permission.
Only a successful live response authorizes one send; a lost response is unresolved.

The synthetic target atomically binds mutation to target precondition, stable
effect identity and installed recovery/fence floor. Independent target lookup may
settle uncertainty but never resends. A new worker cannot replay an uncertain
operation. Restore quarantines issuance/dispatch until independently retained
evidence, cutoff reconciliation, a fresh external recovery epoch and target-floor
acknowledgement establish safe reopening. Missing evidence keeps quarantine.

## Environment and evidence

Use one disposable Linux cell and isolated PostgreSQL roles/stores. Keep the
Windows Stage 1 evaluator profile intact. A Linux evaluator needs separately
pinned bytes and demonstrated time/memory limits. Service authentication alone
does not prove denied network paths or secret-mount isolation.

Before any live qualification, record observed runtime/image pins, owner, resource
ceiling, expiry, synthetic credential custody and teardown. Initial inspection
found Docker available and local PostgreSQL images; that observation is not a
qualified topology or permission to use unrelated running resources.

Required evidence is REF-02-19 and H03-01-13 against actual persistence and service
boundaries, including independent send/effect counts. Retain every failed or
unavailable case. The second implementation review is advisory, not human
contract acceptance. CI results apply only to their exact tested PR heads.

## Participant adapter intake, 7 October 2026

The maintainer reported the first three PRs merged and directed continuation.
Verified inputs are hub `27c3e6c71a3030b209725778bacd88c00f6ff165`, Council
`6ea0822b6ad2da29ca051410289422d9ccaa4c54` and Registry
`eb08f75deaae664afd067194241ae4646c3d53ce`. The next two review tasks are Gate's
PostgreSQL activation barrier and Warden's durable participant adapter. Server's
participant adapter and real complete composition follow after this review pair.

Gate's existing `/v1/actions` experimental adapter uses `pause`, `pause-lookup`,
`apply-activation`, `activation-lookup`, `activation-head` and `resume` operations.
Warden uses `/v1/activation` with `apply`, `lookup` and `head`. Both require current
Server governing bindings at `stage2:<service>` with qualified `scope`, enrolled
`coordinator`, `readers`, `initial_epoch` and `initial_artifact_set_digest`.
Only the enrolled Council transport peer may mutate. Current Council lookup must
confirm the exact ratified transition and bounded validity. Warden independently
obtains Gate's pause and Registry's matching applied receipt/head. Gate independently
obtains the Registry, Server and Warden applied receipts/heads before resuming;
caller-supplied receipts alone are insufficient. Lookup is evidence, never resume.

The initial head is enrolled once and cannot be overwritten by later configuration.
Gate serializes each scope through a PostgreSQL row lock; pause, epoch install,
resume and their retained local outbox records commit atomically. Future consumption
and final-send transactions must take this same lock. Warden owns SQLite WAL/FULL
participant state and matching local outbox transactions. Retried transition IDs
cannot change bytes, and historical receipt lookup cannot alter the current head.
An expired transition cannot gain fresh authority through a retry. Scope includes
domain, tenant, deployment and cell. Only one pending transition may own a barrier.

Gate's resume response distinguishes the completed activation barrier from
execution availability: no execution route is enabled by this packet. Required
Server receipt/head endpoints remain a dependency, and absence keeps the barrier
closed. Participant outbox delivery, snapshot quarantine and target-floor recovery
remain later integration requirements; process restart tests are not restore tests.
The existing Stage 1 decision and identity paths remain separate.

Validation uses isolated test PostgreSQL, native services with disposable mTLS,
concurrent writers, restart after committed phases, immutable retries, changed
authority, incomplete/forged receipt sets and tenant refusals. Synthetic dependency
servers are explicitly identified. No full REF-18 or effect qualification is inferred
from component tests. Local resources have loopback-only ports, synthetic credentials,
no cost authority beyond the existing host, and expiry at test teardown.

## Server participant and complete barrier intake

The next review pair is Server activation custody and Harness's real-service
activation composition. Inputs are Gate `bc429ebcce47579419d88daa6a6aee644fd34221`,
Warden `ef08b587b259600864e3b4f48935e44fa00b7134`, and the Council, Registry and
Server revisions above. Candidate bytes and Stage 1 acceptance pins remain intact.

Server exposes the coordinator's existing `/v1/platform/{tenant}/activation`
adapter with `apply`, `lookup` and `head`. Its currently signed `stage2:<audience>`
binding supplies scope, coordinator, readers, initial epoch/set, audit stream and
the authenticated Council/Gate/Registry endpoints. Application requires the actual
enrolled coordinator peer, current Council ratification, Gate's current pause and
Registry's applied receipt/current head. Network checks happen outside Server's
authority checkpoint lock because those services independently call Server.
Server reacquires the fence and verifies the exact governing revision before commit.

Use the existing protected record ledger and its atomic expected-head batch,
rather than a separate mutable activation pointer. Persist initial enrollment once;
append the participant receipt/state, canonical Server accountability event and
Council transition archive in one transaction. The archive provenance names the
authenticated coordinator and independently fetched ratification, never a fabricated
Council principal. A direct audit append cannot install a participant epoch. Existing
record readers can inspect the canonical event; an authorized exact event retry
returns the original acknowledgement. Retries retain the original event, time,
receipt and acknowledgement. This participant epoch
does not replace the independently signed root governance epoch or enable execution.

Memory storage is disposable; PostgreSQL is the durable profile. Process restart
is not snapshot recovery qualification. Harness will exercise actual authenticated
services and persistence, partial progress, lost replies and retry. Delivery of
Registry/Gate/Warden local outboxes, restore quarantine, effects and network/secret
isolation remain explicit follow-up coverage; complete activation is not complete
Stage 2 execution qualification.

## Participant delivery and action journal intake

The maintainer reported the preceding three PRs merged and requested participant
outbox delivery and Gate's action journal, enabling execution when its dependencies
justify it. Verified merge inputs are Server `7d4a4d836fb483e7dad056f167f3a965d793d229`,
Harness `887d38b482b209662964e1cbce2b5c88bdc433bc` and hub
`748dc42dfb1cc0718458ef5e9e3fe2175eca9e67`; participant inputs above remain unchanged.
The two bounded review tasks are delivery across participant owners and Gate journal
storage. Component PRs retain their owners; this does not authorize merging them.

Participant `flush` is a coordinator-authenticated maintenance operation. It may
deliver retained evidence after a transition expires, but cannot apply or resume a
transition. The owner obtains its own current Warden assertion with `propose` scope
for Server's `action-records:<tenant>` resource. The signed Server action-record
policy registers a dedicated activation-only stream and current generation for each
owner. No request may supply authoritative stream coordinates or acknowledgements.
Source registration changes with pending events refuse; they do not rewrite history.

Only applied receipts map to the existing `activation-applied` event. Gate's pause
and resume records remain retained local history. Before the first send, the owner
transactionally materializes exact canonical event bytes, source sequence,
predecessor and timestamp from its retained intent. This timestamp records the
owner's observation for delivery, not an invented historical commit time. A stream
starts at one and belongs exclusively to this owner store; Server rejects a conflicting
head rather than the sender guessing past missing history. Subsequent events follow
the last locally materialized digest. Each event retains its original source and
bytes across restart, lost acknowledgement and retry. Outbox delivery does not
constitute snapshot recovery: restored or changed-generation stores remain refused
until a separately governed reconciliation protocol exists.

Delivery requires the archived transition (normally committed by Server's apply).
Missing prerequisites leave the event pending. Mark acknowledgement only after
validating the closed candidate acknowledgement, exact event/payload digests,
qualified ledger reference and positive ledger position. Never delete retained
intent or treat an HTTP success, source-head query or mismatched reply as custody.
Concurrent flushes may repeat the same event; they cannot allocate different bytes
or advance past an unacknowledged predecessor.

Gate journal transactions use the existing qualified activation-cell row lock.
They bind immutable operation/request and attempt/context/decision/approval inputs,
retain cancellation tombstones, establish one claim, and atomically consume a
grant, acquire a worker fence, reserve every supplied admitted bucket and append
durable intent. Adapters must provide independently verified inputs, never deserialize
trusted admission structs directly from callers. Storage support alone is not an
authenticated execution route. The mandatory publication bucket is tenant/target,
limit two per UTC hour; extra admitted buckets are conjunctive. Pending and uncertain
reservations count in later windows, and retry returns the original consumption
without a new fence, capacity charge or send opportunity. Cancellation and activation
pause serialize against consumption. No timer or process restart refunds exposure.

This packet does not introduce an executable wire profile or fabricate live Warden,
connector, recovery-floor or Linux isolation evidence. Final-send and target effects
remain unavailable until those controls are implemented and tested. Tests cover
real PostgreSQL races, atomic rollback, restart, cancellation, pause, immutable
retries and capacity across windows; owner delivery tests cover wrong/missing
acknowledgements, changed registration and lost replies. The same implementation
receives a second review pass before publication.

## Live execution intake (8 October 2026, proposed)

The preceding delivery and journal PRs are merged. This packet connects live grant
custody and final admission, then exercises a synthetic target and restore histories.
The review tasks are the execution service boundary (Gate, Warden and Council) and
its target/recovery composition (Harness). Candidate `stage2-v1` remains immutable;
these are experimental service adapters, not a newly accepted contract.

The first executable surface is deliberately narrow: operator-enrolled, immutable
prepared release requests under Server's signed `execution:<service>` binding.
Gate validates and hashes the request and decision itself, checks the current
activated artifact set and qualified scope, and binds the actual enrolled proposing
peer. Caller data selects an enrolled operation; it cannot supply context, evidence,
hashes, approval, consequence class, endpoints or credentials. This prepared-input
surface does not qualify arbitrary dynamic policy evaluation or Linux OPA. Existing
decision-only APIs and evaluator evidence retain their separate boundaries.

Council supplies current approval status plus the original approval event and exact
Server acknowledgement. Its recording assertion uses `propose`, the implemented
Server write scope. Gate archives request and decision before approval. Claims and
consumption use the existing PostgreSQL cell lock and canonical outbox. Warden
independently fetches Gate and Council state, retains stable grant issuance and
outbox bytes, and binds custody to an enrolled connector, worker and invocation.
Revocation and current authority are checked again immediately before final admission.

Final admission requires the exact stored predispatch acknowledgement, current
approval and custody, unchanged activation/recovery epochs and the owning worker.
In one PostgreSQL transaction Gate records `send-intent` and spends the one send
opportunity. Only that first live response permits a send; a lookup or repeated
request cannot replace a lost response. Cancellation serializes on the same lock
and reports `too-late` after admission. Uncertainty retains capacity. Outcome and
reconciliation append facts; they never erase a send intent or authorize a resend.

The synthetic target stores effects and its monotonic recovery floor outside the
Gate database. It atomically checks the exact target precondition, content digest,
stable effect identity and recovery fence with mutation. The connector has no retry
loop. Credentials are obtained through the broker only in the connector privilege
domain and never appear in action responses, journals or evidence logs.

Restore tests must retain the external target/floor and original Server custody.
Restored Gate state remains quarantined when it cannot demonstrate the current
recovery generation and retained exposure. Reopening requires reconciliation of
the Server cutoff, consumption/cancellation/reservation facts and target floor;
missing evidence cannot be replaced by an operator boolean. Tests distinguish
quarantine evidence from demonstrated safe reopening. This packet grants no
production activation, deployment, release or merge authority.
