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
