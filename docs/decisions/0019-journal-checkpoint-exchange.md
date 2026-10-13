# ADR 0019: independently retained Gate journal exchange

**13 October 2026; experimental implementation directed; acceptance pending.**
This specifies the R2 exchange required by
[ADR 0018](0018-restore-checkpoint-protocol.md). The implementation baseline is
Server `bb18085f3d407e9b77d551fbf7ac68a6572fce27`, Gate
`28f80b4054a45e29677cb72c495edefc701f47ab` and Harness
`a0594cfc2c206510d89e48775e736e5b917ae285`. The
[R1 evidence](../stage2-implementation.md#retained-action-checkpoints-13-october-2026)
establishes a pinned action export; it does not establish complete journal custody.
The separate [journal candidate](journal-v1/README.md) supplies locked schemas and
offline vectors. It is not accepted; runtime consumers and their independent
conformance/restore evidence remain pending.

## Enrollment and authority

Use a separate `action-journals:{tenant}` Server recording resource and
`action-journals:{audience}` governed binding. Existing `action-records` permission
does not imply journal permission. Authenticate the actual service peer and verify
the currently valid signed principal and binding on every request, including reads
and immutable retries. Recording is restricted to the enrolled Gate owner; reader
admission is separately explicit. Scope always includes domain, tenant, deployment
and cell. Cross-scope IDs or identical unqualified IDs cannot select another journal.

The immutable enrollment binds the qualified journal identity, actual Gate service,
positive source generation, initial operational-state digest, pinned R1 audit
cutoff/digest and evidence of a separately governed empty journal and empty target.
Reader configuration can change without rewriting that enrollment. Changing the
owner, journal identity, generation or baseline is recovery governance, not an
ordinary update or automatic initialization. A new database cannot enroll itself.
Existing populated journals need R3 reconciliation before entering this profile;
they cannot declare their present contents an empty baseline.

The current execution enrollment must require the exact journal enrollment. A local
configuration switch, restored absent metadata or replacement service instance
cannot turn that requirement off. R2 does not retrospectively label the existing
experimental prepared/dynamic histories independently checkpointed.

## Closed intent and commit chain

The new candidate will define closed enrollment, intent, commit and receipt shapes,
separate canonical digest domains and bounded operation-specific request/response
shapes. Preserve all existing candidate bytes, digest domains and golden vectors.
Use the committed-source publisher and new consumer namespaces. These operational
records are evidence; none contains an execution permission or bearer credential.

Each journal has one append-only chain, with one pending intent at most. A mutation
sequence starts at one and advances only through its matching committed pair. An
intent binds the enrollment digest, exact preceding committed checkpoint digest,
mutation sequence, actual before-state digest, mutation kinds, qualified operation/
attempt identities where applicable, complete proposed canonical row delta and its
digest, expected after-state
digest, retained audit prefix and conservative exposure footprint. The first intent
uses the enrollment checkpoint and its initial state. Activation-only mutations
explicitly have no operation; they cannot invent a placeholder action identity.

The commit binds that exact intent and sequence, the actual after-state digest and
the canonical changed rows sufficient to replay the transaction against the verified
prior state. Each delta identifies an allowed table, its complete immutable row key,
and exact before/after row values; row absence is explicit. Refuse duplicate keys,
unknown tables, changed key identities, unchanged rows, wrong ordering and a delta
that disagrees with the intent. Bound canonical bytes, nesting, row count and integer
range in the candidate. An oversized transaction refuses before durable Gate commit;
it cannot silently omit rows or split one atomic consumption into smaller mutations.

Server verifies the closed records, admitted owner/scope/enrollment, chain linkage,
sequence, canonical delta digest and intent/commit agreement. It retains the actual
Gate producer's evidence; it cannot independently observe Gate's SQL transaction.
Receipt identity, ledger position and receipt time are immutable. Identical retry
recovers the original receipt only under current authorization; changed bytes,
another intent while one is pending, a skipped sequence or stale prior checkpoint
refuses. A head response exposes both the last committed checkpoint and any pending
intent. It must never project a pending intent as a committed mutation.

An intent is possible exposure even if Gate later reports that its transaction did
not commit. Time, missing rows, a newer UTC window or expiry cannot settle it.
Consumption and send intents retain every applicable bucket and its units, limit
and window, the target, grant and worker/send bindings needed for conservative
reconciliation. The profile must validate that these facts agree with the delta's
reservations and dispatch state. R3 supplies independent settlement; R2 has no
caller-controlled abort, refund, reset or reopen operation.

## Actual Gate state and transaction ordering

Compute the before and after digests from actual database rows under serialization,
not request fields. Canonical state includes every scoped row in activation cells,
transitions and delivery/outboxes; action enrollment, sources and claims;
cancellations and consumed-grant tombstones; reservations; action outboxes and exact
acknowledgements; dispatch, outcomes and reconciliations; and execution generation.
Include original sequence, registration and receipt bytes. Enumerate the owned
tables in the candidate profile so that a new operational table requires an explicit
coverage update and regression control. Ignore only checkpoint metadata itself to
avoid a self-referential digest; validate that metadata separately against the chain.
The decision-only SQLite cache supplies no effect authority under this profile.

The serialization guard covers every effect-relevant writer, including startup,
enrollment, activation delivery and read-side writes. A PostgreSQL transaction lock
alone expires too early: serialize across the SQL commit and independent commit
acknowledgement, across all instances using the same qualified journal. Owner reads
and Warden/Council callbacks finish before this guard is acquired. Do not hold a
current-authority fence across remote callbacks or allow a guard to deadlock them.

For each transaction:

1. Recheck actual state, independently retained chain head, required enrollment and
   complete pinned audit prefix. Refuse unknown, missing or conflicting evidence.
2. Stage SQL changes and compute the complete actual delta under the guard. Staging
   is uncommitted; it exposes no operational response or authority. A transaction
   with no state change needs no new intent, but still requires the admission check.
3. Obtain the durable Server intent receipt before committing any operational SQL
   change. Persist the matching local checkpoint metadata in the same transaction
   as consumption, worker ownership, every reservation and the outbox.
4. Commit PostgreSQL, then obtain Server's immutable commit receipt for the exact
   actual delta. Only afterward may the adapter return the operational response.

This is write-ahead relative to durable mutation, not relative to uncommitted SQL
staging. A failure before intent creates no independent exposure. Any interruption
after intent leaves the footprint unresolved and admission quarantined. Persist
quarantine separately from activation pause; ordinary activation resume cannot
clear it. If the exact independently committed receipt is already retained and
actual local state and metadata match, recover only that factual receipt. A pending
intent or missing local commit remains a reconciliation case.

## One-shot final send and short-lived authority

Successful consumption and send-intent responses require completed independent
custody. Only the original live final-send path can return its private one-shot
permission after the exact commit acknowledgement. Retry, lookup, process restart
or recovery cannot mint another completion token or return permission from a stored
receipt. If a reply was lost, the operation retains its spent send opportunity.

Preflight a verified, narrowly scoped Server recording assertion before entering
short-lived custody, following
[ADR 0017](0017-scoped-registry-assertions.md)'s identity verification and retention
principles for this separately admitted resource. Every owner fact stays live and
every Server request checks current authority. Recheck custody, clock bounds and
authority after independent acknowledgement, before permission. An expired ticket,
late acknowledgement or changed authority leaves unresolved exposure; do not extend
five-second custody or the two-second clock bound to accommodate the exchange.

## Independent Server retention

Server's append-only ledger can itself be restored. Pinning only its current head
inside that same restored database cannot detect backwards movement. The R2 Server
adapter therefore requires a separately retained per-journal high-water checkpoint
outside both Gate and Server snapshot restoration. It binds the enrollment and exact
latest retained chain record, including any unresolved intent. It contains evidence
references and digests, not credentials. Keep filesystem/configuration concerns in
the Server adapter; the core chain remains independent of filesystem and transport.

Advance this retention before acknowledging a record, with durable handling of the
interruption between retention and ledger persistence. Serialize writers and verify
the retained record against the ledger at startup and on each request. A missing,
older, conflicting or unreadable retention point refuses; it cannot be silently
recreated from the current database. Exact retry may complete an already provable
record, but cannot infer that an absent record was safely rolled back. Tests must
cover each persistence interruption and retained Server state moving backwards.

The deployment must preserve this retention independently; a joint rollback of
every evidence store is outside its demonstrated detection boundary. Document the
actual storage durability and administrator trust assumptions rather than claiming
hardware independence from a pathname.

## Implementation packets, evidence and alternatives

R2 proceeds in bounded packets: new hub candidate/vectors/export; Server admitted
chain and independent retention; Gate exhaustive transaction/admission coverage;
then actual Harness snapshot and interruption histories. Keep at most two packets
awaiting review, one owner for hub/Server edits and the eight-hour re-estimation
boundary. The founder is accountable owner/reviewer; independent human acceptance
remains pending. Record environment ownership, availability, expiry and cleanup
before live tests. No new runtime coverage is claimed by this decision.

Required negative controls include stale/absent enrollment, wrong peer/resource/
scope, conflicting retry, two-instance admission, omitted owned table, altered
receipt, partial audit export, failure at each intent/SQL/commit boundary, undeclared
Gate snapshot rollback and retained Server rollback. Adjacent positives prove exact
receipt recovery without renewed permission. Preserve existing native Linux,
Windows, activation, prepared, dynamic and agent-isolation tests. R3 still owns safe
reopening, old-worker exclusion, target floors and held debt after reconstruction.

Audit-only export was rejected because a committed consumption can be absent from
the audit tail. Post-commit-only checkpointing was rejected because an interrupted
exchange leaves no independent precommit footprint. Local digests without retained
prior heads were rejected because a self-consistent old snapshot passes them.
Distributed SQL transactions were rejected because the owners have independent
stores and require explicit failure custody. Silent adoption of existing populated
journals was rejected because it would erase the unobserved-history boundary.

The new candidate remains inactive and unreleased. No catalog/invariant promotion,
contract acceptance, qualification, deployment, production trust or paid resources
follows from this protocol. Stage 2 retains `qualification:false`.
