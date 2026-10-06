# Proposed action lifecycle and client semantics

**Proposed specification, 6 October 2026; no implemented API or published wire contract.**
The founder/maintainer owns acceptance. [ADR-0002](../decisions/0002-action-execution-protocol.md)
defines the transaction boundary; DEC-02, DEC-04 and DEC-05 in the
[contract backlog](contract-backlog.md) must settle exact encodings before component work.

## Identity, binding and retention

The application persists a stable operation identity with its business intent **before** submitting
it. Harness accepts that persisted identity; it must not invent a fresh one on each network retry.
Gate's deduplication key is tenant plus operation identity, bound to the authorized principal scope
and Gate-computed canonical request digest. Lookup/replay requires authorization for that tenant
and operation; possession of its identifier is not access authority.

The same key and canonical content returns the existing operation; changed content conflicts.
An intentional second effect has a new business intent and key. When a target has an independent
business uniqueness constraint, its manifest declares the corresponding effect key and conflict
behavior; a new arbitrary client key cannot bypass that constraint. Request identity alone cannot
detect all semantically duplicate intentions, and the boundary must say so.

The request binds action, target, verified artifact/evidence references, principal scope and typed
quantities. A decision additionally binds evaluator/policy/manifest digests, evidence snapshot,
consequence, obligations, target preconditions, mode and activation epoch. Approval binds that
exact request/decision context; the later grant additionally binds the durable claim. Renewing a
token cannot change the intent or extend an
approval's execution window. Re-evaluation appends a linked decision revision; it never overwrites
the earlier refusal, approval, grant or outcome.

For the first profile, compact identity/digest/outcome and consumed-grant tombstones have **no
automatic TTL**; claim/grant expiry is not deduplication expiry. Payload retention is separately
bounded and access controlled. Pruning a payload retains its digest, identity, authorization scope
and deletion evidence; lookup can report unavailable detail without permitting another send.
Archival must preserve lookup/tombstone enforcement. A future finite deduplication horizon requires
an explicit admission rule for expired namespaces and cannot silently recycle old identities.

## Execution states and allowed transitions

State names below are proposed wire candidates. Each transition has a durable version/sequence,
actor, time, authority and source-event references; clients use conditional versions for mutation.

| State | Meaning | Permitted transition and authority |
|---|---|---|
| `proposed` | Authenticated intent captured; no effect authority | Gate evaluates to `denied`, `approval-required` or `claimed`; authorized withdrawal may cancel |
| `denied` | A decision refused the request; no dispatch | Fresh evaluation may append a new decision under the same immutable intent; never auto-retry execution |
| `approval-required` | Obligations remain unsatisfied | Bound Council approval and fresh Gate checks allow `claimed`; refusal, expiry or withdrawal records denial/cancellation |
| `claimed` | Durable immutable claim exists; no grant consumed | Gate consumes the matching Warden grant, acquires ownership and reserves all capacity atomically to `dispatch-admitted`; expiry/cancel before consumption terminates this claim |
| `dispatch-admitted` | Grant consumed, one worker/fence and capacity assigned; send forbidden pending final checks | Acknowledged Server event plus Warden validation and final Gate CAS permits `dispatching`; safe pre-send cancellation/failure is terminal for this claim |
| `dispatching` | Irreversible send intent committed; a send may have happened | Connector records `completed`, `rejected-after-dispatch` or `unresolved`; lease expiry cannot authorize another send |
| `completed` | Connector contract establishes the known effect/result | Replay result; any reversal or correction is a linked new action/record |
| `failed-before-dispatch` | Journal proves final send admission never occurred | Release reserved capacity once; fresh action authorization is required for another attempt |
| `cancelled-before-dispatch` | Authorized cancellation won the conditional race before send admission | Release capacity; consumed grant remains consumed and the cancelled claim cannot reopen |
| `rejected-after-dispatch` | A send occurred but authoritative target evidence proves no effect | Record rejection and evidence; settle/release under its measurement rule; never label this unsent |
| `unresolved` | Some, all or none of the effect may have happened | Authorized read-only investigation may append evidence and resolve to a known outcome; no automatic resend or capacity refund |

An abandoned pre-consumption claim may be superseded by a fresh linked claim only after its issuance
is irrevocably closed and Gate atomically disables admission. A consumed claim is never recycled.
A new attempt after definitive failure uses a new operation linked by `retry-of` and repeats all
authority checks. Changed business intent is a new operation, not a changed digest under an old key.
An unresolved operation cannot be made retryable by cancellation, new approval or a new client key;
operators must establish its effect before authorizing a related replacement.

## API results, retries and cancellation

The proposed REST mapping keeps decision outcome, execution state and recording delivery separate.
Exact paths, bodies and codes require contract vectors; MCP maps the same semantics rather than
converting all successful tool transports into successful actions.

| Operation/result | Proposed HTTP interpretation | Safe client behavior |
|---|---|---|
| Accepted proposal awaiting work/approval | `202`, operation reference, current decision and state | Poll/read or supply authorized approval; no target authority implied |
| Valid request with policy denial | `200`, typed `denied` decision and durable reference | Display refusal; a successful HTTP exchange is not permission |
| Known completed/rejected/unresolved operation | `200` lookup, typed state and result/evidence | Display the exact state; unresolved lookup never executes |
| Existing identical submission | Existing reference/state (`200` or pending `202`) | Reuse identity; replay must not repeat the effect |
| Identity/content conflict or stale conditional mutation | `409` with conflict category | Resolve content/version mismatch; do not switch keys automatically |
| Malformed input / unauthenticated / unauthorized | `400` / `401` / `403`; non-disclosing lookup policy may use `404` | Correct input or authority; do not expose another tenant's operation |
| Required dependency unavailable before accepting a request | `503`, optional retry guidance without an execution promise | Retry same identity, first lookup if acceptance was ambiguous |
| Server outcome delivery pending | State/result plus `recording-pending` delivery field | Do not claim a complete accountability chain until acknowledged |

Cancellation by an authorized originator/delegate or operator uses a journal compare-and-set.
Before final admission it may establish `cancelled-before-dispatch`; after final admission it
returns a too-late conflict with the actual operation state. A transport disconnect, cancelled SDK
future or HTTP timeout is not action cancellation and does not release capacity. Withdrawal of an
approval blocks unstarted work but cannot undo admitted effects. A target-specific cancellation
after send is a separately authorized operation whose result may itself be uncertain.

An asynchronous worker reports progress and durable failures through lookup even if the original
HTTP call has ended. Client retry policy is per operation category: proposal replay, event delivery
and evidence lookup can be idempotent; target sends are never generically retried. Lost replies to
issuance, consumption and final send admission follow ADR-0002's distinct recovery rules.

## Evidence, reconciliation and compatibility

Effect status and Server delivery status are independent: a known effect with a pending outbox is
not a fully recorded success; a complete predispatch ledger is not proof of a target effect.
Records preserve journal sequence, mode/epoch, grant/claim/fence, target receipt digest, covered
source range, last confirmed watermark and any missing interval. Reconciliation is append-only,
names the actor and evidence, and retains the earlier unresolved observation and its duration.

Compensation and supersession are **relationships**, not mutations that erase `completed` or
`unresolved`. The new action links `compensates`/`supersedes`; the original remains queryable with
its actual outcome. Disputed target evidence remains disputed until the declared resolution
procedure determines what can be concluded.

The historical plan's `failed-before-effect` becomes two precise cases: proven unsent, and sent
with proven no effect. Harness/Console and Assure must distinguish both from uncertainty. Existing
scaffold associated types do not constitute an API to migrate, but future published enums and
clients must fail safely on unknown states and evolve by expand, migrate, remove. Acceptance
vectors include every table row, cancellation racing admission, non-disclosing cross-tenant lookup,
changed-content retries, payload pruning, stale approval/mode, and pending outcome delivery.
