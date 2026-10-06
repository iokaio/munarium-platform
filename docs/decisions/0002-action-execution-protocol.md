# 0002: single-cell action execution and cumulative reservations

**State:** Proposed for maintainer review; not an accepted contract or implemented guarantee.
**Date:** 6 October 2026. **Accountable owner:** founder/maintainer under
[GOVERNANCE](../../GOVERNANCE.md). **Decision register:** DEC-05 and DEC-06 in the
[contract backlog](../architecture/contract-backlog.md).

## Problem and scope

Plan revision 4 requires durable claims, single-use grants, required recording and no blind
repetition of uncertain effects. It does not assign a transaction owner for acquisition and
consumption, or for aggregate action limits. Separate databases cannot establish those properties
merely by exchanging signed tokens. This proposal makes those boundaries explicit for one cell.
It covers Gate, Warden, Server, connectors and their clients; Gateway model-budget accounting
remains a separate responsibility. The [action lifecycle](../architecture/action-lifecycle.md)
defines the proposed states and API interpretation.

This is a design to test. It neither changes Server/Matrix nor activates scaffold interfaces.
Implementation waits for accepted decisions, versioned contracts and the foundation extensions.
Decision-only evaluation has no target grant, broker access or effect-producing transition.

## Proposed transaction and authority owners

| Owner | Authoritative state | Constraint |
|---|---|---|
| Gate operational journal | Claims, worker fences, grant consumption, action reservations, send admission, outcome outbox | One supported transactional database; one active writable cell epoch |
| Warden | Verified identity, immutable issuance bindings, revocation/suspension, credential admission | May issue and validate grants; cannot mark an action unconsumed or dispatch it |
| Server | Append-only accountability events, provenance and linked corrections | Required predispatch acknowledgement; later outcome delivery is idempotent and recoverable |
| Connector/target | One send attempt and target receipt or lookup evidence | Neither a lease nor a signature proves exactly one external effect |

Gate is the **only commit owner** for consuming a grant, acquiring its claim and reserving all
action capacity. These writes share one transaction with uniqueness on tenant/operation identity,
claim ID and grant ID, and conditional updates on state, owner fence and recovery epoch. Warden's
issuance state is not a second consumption database. Other cells must reject the grant audience;
multi-cell execution would require a separate decision and evidence.

Server does not host Gate's worker lease. Each operational transition appends an outbox event in
the same journal transaction, with immutable event ID, operation ID, sequence, prior-event link,
payload digest and source epoch. Server acknowledgement must identify that event and digest.
Retrying an append with the same ID is idempotent; different content is a conflict. These are
required foundation semantics, not claims that the existing Server API supplies them.

## Protocol and linearization points

1. Gate authenticates and pins the proposal, decision, approval when required, manifest, target
   preconditions, mode and activation epoch. Required proposal/decision/approval records receive
   durable Server acknowledgements. A journal transaction creates a stable unowned claim and its
   immutable grant-request binding; no target permission follows from this write.
2. Warden validates authority and authenticates Gate's durable claim lookup, comparing the
   immutable tenant/request/target/epoch binding rather than trusting a caller-supplied claim ID.
   A missing, mismatched or unavailable claim refuses issuance. It atomically persists issuance
   keyed by tenant, cell epoch and claim ID before replying. Identical retries return the **same grant ID and original expiry**;
   changed bindings conflict, and an expired or revoked issuance is not silently replaced. A lost
   reply permits authenticated lookup. One claim has one issuance and one consumption.
3. Gate atomically checks the claim, grant binding, expiry and available cumulative capacity;
   consumes that grant; assigns one worker/fence; reserves every affected action bucket; and
   records `dispatch-admitted` plus its outbox event. Any failed check rolls back all those writes.
   This is single consumption, not target dispatch. Warden/connector learn consumption through
   authenticated journal introspection, never from an agent's assertion.
4. Gate obtains Server's durable acknowledgement of that exact predispatch event. Unavailability
   prevents a send. A timed-out acknowledgement is queried or retried by event ID, not assumed.
5. Warden rechecks revocation, suspension, identity and grant validity online and returns a short
   validation ticket bound to grant, claim, worker/fence, cell epoch, mode/activation epoch,
   audience and deadline. Only the isolated connector receives the target credential. Ticket
   renewal changes neither the original grant expiry nor the consumed-grant state.
6. Immediately before one send, the isolated connector calls Gate's final-admission API for its
   exact live invocation. Gate's conditional journal transaction verifies the acknowledged
   event, owner/fence, ticket, current mode/epoch, required freshness and target preconditions.
   Admission must fit the intersection of approval, grant, ticket, owner lease and change-window
   validity using conservative time bounds. It changes `dispatch-admitted` to `dispatching` and records the
   intent. **This commit is dispatch authorization's linearization point.** It is neither a
   cross-service transaction nor the external effect's commit. Only the successful live connector
   invocation may proceed; losing or uncertain replies never permit a send based on lookup alone.
   A repeated connector command must repeat this conditional admission, which then refuses; a
   previously returned admission acknowledgement is not a reusable dispatch credential.
7. The connector performs at most one send attempt; transport libraries must disable automatic
   effect-producing retries. Gate records receipt, known-no-effect evidence or uncertainty
   durably with an outcome outbox event, then delivers it to Server. Journal loss or send/receipt
   ambiguity is `unresolved`, even if the target might have succeeded.

The journal and trusted connector are in the enforcement boundary. A stale worker cannot pass
the conditional transition. A worker paused **after** that transition may still send later:
no lease takeover may redispatch its operation. The reference target additionally checks the
fence/recovery epoch and stable effect key atomically with its effect. A legacy target that does
not support those checks cannot promise rejection of an already admitted stale request; document
that limitation, remove parallel dispatch paths and qualify only the weaker boundary.

## Revocation, time and mode

The proposed [reference profile](../architecture/reference-profile.md) uses a 30-second grant,
5-second validation ticket, 10-second owner lease, 2-second maximum pairwise clock skew and
conservative expiry checks. These are experimental requirements to measure, not current service
guarantees. Ticket creation after Warden accepts revocation is refused. A previously issued ticket
can admit within its remaining validity; the proposed no-new-admission bound is at most 7 seconds,
subject to measured clock assumptions. Final admission checks fresh revocation and activation
watermarks; missing dependency, uncertain clock or expired freshness blocks it.

Revocation after admission cannot recall a request already admitted or undo an effect. Record the
revocation's acceptance, affected scope, last possible admission and observed acknowledgement;
publish dispatch-admission and target-effect limits separately. Target preconditions need atomic
target enforcement where the claim depends on them, not only a read before send.

Every decision, approval, claim, ticket and event binds the actual enforcement mode and activation
epoch. Observe/advise never dispatch through this protocol. A relevant activation, stronger
obligation or mode change invalidates unstarted authorization and requires a fresh bound decision;
a weaker mode still requires a governed transition and cannot revive an old approval.

For this cell, Council coordinates an explicit admission barrier using the approved activation
attestation and authenticated control APIs: Gate durably pauses new admission, the governed
Registry/Warden transition installs the new epoch, then Gate applies that epoch and resumes only
after the required acknowledgements. Failure leaves admission paused; Council recovers the same
transition ID and expected prior epoch rather than starting a second activation.
The activation receipt records the affected cell and barrier acknowledgements; reading a Registry
pointer alone is not proof that every consumer has adopted it. Gate's epoch update serializes with
final send admission in the same journal, and Warden tickets must match it. Already admitted work
remains subject to the effect limits above. DEC-04 must accept this barrier before implementation;
the proposal makes no instantaneous global-activation promise.

## Cumulative action reservations

Gate owns aggregate **action** limits, independently of Gateway's model-price/token reservations.
Policy supplies typed units, exact integer quantities, cap, aggregation key, window and epoch;
the first slice rejects unsupported units rather than estimating silently. Keys include tenant,
root task, target/action class and any policy-defined subject; child actions charge the same root
pool plus applicable child caps without double-counting the root total.

All affected buckets are locked/conditionally updated in a deterministic order inside step 3.
For each cap: settled usage plus live reservations plus this proposed quantity must fit. Per-action
allowance is insufficient. Reservations retain the admitted policy epoch: changing limits or a
window cannot make pending exposure disappear. New admissions count unresolved carry-over against
the successor window/cap until evidence settles it; no window reset or grant expiry refunds it.
The first profile attributes settled usage to its admission window and carries pending exposure
forward; this is an admission allowance, not a promise about effect-completion rate at the target.

Proven no-dispatch/no-effect releases the reservation once; verified effect settles actual usage
under the declared measurement rule, retaining the reserved bound if actual usage is unknown.
Excess usage creates an explicit violation and blocks further affected admissions; it cannot be
made safe retrospectively by rewriting the reservation. Compensation is another authorized action,
with its own capacity; it does not erase the original consumption.

## Crash and restore rules

| Failure point | Required recovery |
|---|---|
| Before issuance commit / reply lost | Retry the identical issuance key; lookup returns persisted result, never a new grant |
| Before consumption commit / acknowledgement lost | Inspect journal; no connector send is allowed by this phase |
| After consumption, before final admission | Resume only under the same live owner/fence, or terminally cancel; an expired owner cannot obtain a send transition |
| Server predispatch acknowledgement missing | Keep blocked or safely cancel before send; do not manufacture an acknowledgement |
| Final admission acknowledgement lost, or worker dies after it | Unresolved until independent receipt/no-effect evidence; no replacement send |
| Target replied, Server unavailable | Persist outcome/outbox locally; expose ledger delivery as pending and recover by event ID |
| Outcome durability uncertain | Preserve unresolved state and capacity; reconcile against target/Server evidence |
| Restore, rollback or possible split brain | Quarantine dispatch and issuance; do not infer safety from restored database contents |

Recovery requires fencing off every old dispatcher/credential route, reconciling journal, Warden,
Server and target records through a known cutoff, and establishing a **new authority/recovery
epoch outside the restored snapshot**. Epoch custody belongs to the operator's protected recovery
procedure, with Warden and target-side enforcement or credential revocation as applicable. Reusing
the old snapshot's epoch is forbidden. If old workers or effects cannot be excluded, the cell stays
quarantined. Carried-forward tombstones, consumed grants and unresolved reservations remain linked
to their original epochs; fresh authority never resets their meaning. Minimum restore tests gate
the first effect path; broader disaster recovery remains later work.

## Alternatives, consequences and acceptance

| Alternative | Tradeoff and disposition |
|---|---|
| Atomic transaction spanning Gate, Warden, Server and target | Not assumed; no such supported common transaction exists in this design |
| Warden owns consumption and Gate independently leases work | Requires another recovery/consistency protocol; defer to keep one commit owner |
| Server is the live worker journal | Would add operational lease/transaction duties to the foundation; requires a separate decision |
| Signed short-lived grants alone | Cannot reject concurrent redemption or restore resurrection; insufficient |
| Retry through target idempotency automatically | Useful for some targets, but absent a qualified contract can duplicate effects; first slice uses lookup only |

Gate gains durable admission/storage and reservation work; Warden needs issuance idempotency,
online validation and recovery-epoch handling; Server needs typed links, deduplication and durable
acknowledgements. Harness/Console expose uncertainty and recording lag; Sentinel/Assure preserve
those distinctions. Matrix remains read-only evidence and acquires no execution responsibility.
No new cross-repository implementation is authorized by this proposal.

Acceptance requires real-store concurrency and fault injection at every numbered step, duplicate
issuance/consumption conflicts, stale-worker rejection, two actions exceeding one aggregate cap,
window rollover with unresolved exposure, expired/changed-mode admission, Server outage, outcome
recovery and old-snapshot quarantine. Inspect the disposable target independently to verify effect
counts. The [reference scenario](../architecture/reference-scenario.md) supplies the test cases.
No evidence has been produced for this protocol yet. Accepting it also requires resolving DEC-01,
DEC-02 and DEC-04 bindings and DEC-07 deployment assumptions. Published contracts subsequently use
expand, migrate, remove; no provisional enum or document here is a wire version.
