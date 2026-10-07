# 0010: Stage 2 approval, activation and durable action boundary

**Proposed for maintainer review, 7 October 2026.** This HUB-03 design packet
extends [ADR 0002](0002-action-execution-protocol.md) and the implemented
[Stage 1 boundary](0008-stage1-service-boundary.md). It addresses DEC-04–08;
it is not an accepted wire contract, effect implementation or runtime authority.
The maintainer authorized preparing the packet and foundation assessment.
The [work plan](../stage2-preparation.md) records the subsequent gates.
The [platform-wide second pass](0011-platform-contract-evolution.md) supplies
the identity, namespace, epoch, profile and event rules for the next candidate
cut. Read the two proposals together; neither changes Stage 1's existing bytes.

## Scope and choices

One cell, one synthetic `release.publish_approved_artifact` target, distinct
requester/approver identities, and the existing REF-02–19 oracle. Council owns
approval and activation coordination; Registry owns admitted immutable artifacts;
Gate owns the action transaction; Warden owns issuance and credential admission;
Server owns durable accountability. None writes another service's tables.

| Question | Recommended choice | Alternative / consequence |
|---|---|---|
| Approval | Exact-request/context approval by a currently eligible distinct human | A ticket label or reusable broad approval cannot authorize this action |
| Activation | Single coherent artifact-set digest and one resumable cell barrier | Independent pointer changes can expose mixed authority; no distributed atomic commit is assumed |
| Consumption and limits | Gate owns one atomic journal transaction | Separate Warden consumption would require another consistency/recovery protocol |
| Records | Shared versioned envelope with a new action payload family alongside unchanged Stage 1 records | Adding kinds to the existing single-result conflict rule is insufficient; other families must not invent action bindings |
| Persistence profile | PostgreSQL for the proposed effect journal, with separate roles/stores | Stage 1 SQLite remains supported for decision-only use; it is not silently qualified for action execution |
| Effect boundary | Retain the proposed isolated Linux cell and target with atomic fencing | Existing Windows process tests prove authentication, not agent/credential isolation |

The Linux recommendation retains the reference profile's intent but exposes a
real prerequisite: Stage 1's bounded native OPA worker is Windows-only. Gate must
prepare and qualify a separate Linux worker/profile with pinned binary and bounds
before the Linux effect composition can run. Do not remove resource limits or
treat a host change as already covered. Native Windows isolation is an alternative
requiring its own concrete deny-edge and custody evidence; neither is accepted here.
Keycloak/OpenBao remain integration candidates from the reference profile; exact
versions, licenses and dependency reviews must be supplied at profile intake.

## DEC-04: approval binding and distinct authority

Council obtains the canonical proposal and authoritative decision context from
authenticated services. It must not sign an agent-provided summary or accept a
caller-supplied approval as its own verified result. A candidate approval binds:

- schema/profile version, approval ID, qualified tenant/cell/operation and attempt;
- canonical request, decision, durable principal/origin, manifest/artifact, policy and
  required-evidence digests, target/environment and exact target preconditions;
- actual mode, scoped activation epoch, qualified authority/context pins and change window;
- selected approver policy, obligations/quorum, authenticated approving principal
  references, issued time and expiry, plus immutable prior/correction references.

The first profile uses one distinct enrolled human approver; this is account-level
separation, not evidence of two independent human operators. The approver cannot
be the requester, an agent-derived ratifier or a member of the proposer's chain.
Human admission must use an operator-enrolled path: Stage 1 workload tokens may
not acquire human kind. Council verifies current eligibility, scope and freshness
when approving; Gate revalidates the exact bindings and approval status before
admission. A valid signature alone is insufficient after revocation or change.

Candidate lifecycle: proposed, awaiting approval, approved, withdrawal-pending,
vetoed, cancelled or expired; each disposition is append-only. An approval API
retry returns the same issuance for the same idempotency key and immutable bytes;
changed content conflicts. Responses separately expose current approval status
and revision, so retrieving an original approval cannot conceal its withdrawal.
Changed evidence, policy, target precondition, mode or epoch requires a fresh
decision/approval. Expiry never renews through retry.
ADR 0011 distinguishes immutable intent from authorization attempts: refreshing a
proof alone does not rewrite the original request. Changed intent conflicts under
the same operation, and a fresh attempt cannot bypass an unresolved claim/effect.

Withdrawal after issuance starts as pending. Council requests Gate's durable
conditional cancellation bound to operation/attempt, approval ID/revision and withdrawal
ID. Gate records a cancellation tombstone even if no claim exists yet, and
serializes it with final admission: before `dispatching` it prevents any later
admission for that approval; after final admission it returns too-late. Council
marks withdrawal effective only on the matching durable receipt. A lost reply
uses that same withdrawal ID; lookup cannot reinterpret pending as effective.
Already admitted work remains subject to the stated revocation/effect limits.

The minimal authenticated Council interface exposes request, decision and lookup
operations. Notifications and Console are presentation, not authority, and are
not dependencies of this first approval path.

## DEC-04/07: resumable activation barrier

Activation binds a transition ID, cell/tenant, expected prior head/epoch, complete
artifact-set digest, proposed successor epoch, human ratification and validity,
including not-before/expiry. It also binds the admission scope and exact required
participant/receipt-set digest. Each epoch is qualified by owner and scope under
ADR 0011; source, recovery, worker and target generations are not interchangeable.
All referenced artifacts are immutable, compatible and independently verified.
Submitted Registry candidates never promote themselves. Governing transitions
use the deployment's admitted authority, including Server's non-agent bootstrap
retirement constraints; no direct SQL or ordinary writer bypass is allowed.

1. Council durably records the approved transition and asks Gate to pause new
   action admission. Gate commits the pause and returns a bound receipt.
2. Registry stages the exact verified artifact set, then conditionally installs
   its active set/epoch against the expected prior head under that transition ID.
   Its activation receipt binds the prior and new heads, exact set and successor
   epoch. Server and Warden apply only their owned authority changes using expected
   prior state and the same transition. Their receipts bind the same selected set
   and epoch. A lost reply returns the original receipt, not another activation.
3. Gate commits the matching epoch while paused, serializing it with final-send
   admission. Council retains the complete required receipt set.
4. Gate resumes only on a valid, current completion command for that exact
   transition and the required Registry, Server and Warden receipts. Any failure
   or missing acknowledgement leaves admission paused; status lookup alone cannot
   resume it. Required participant membership comes from the bound profile, not
   from a caller's list with omitted owners.

Retries resume the same transition and return existing receipts, rejecting
changed content or stale expected heads. Partial updates are visible, never
reported as global atomic activation. Recovery completes that transition or
performs a separately governed transition to known compatible digests; rollback
does not reuse an old epoch or revive prior approvals. Already admitted work is
reported separately; the barrier cannot recall it. REF-18 exercises failure after
each acknowledgement and checks the target as well as the service responses.
Expose each participant's applied state separately from the composition's active
state. A Registry active pointer during partial transition does not prove resumed
admission. Future Gateway participation requires an explicitly admitted profile;
Console, Sentinel and Assure are not universal activation dependencies.

## DEC-05/06: one transaction owner and bounded exposure

Retain ADR 0002's seven protocol steps. Gate first durably binds the request and
creates the claim; Warden verifies it by authenticated lookup and persists one
issuance per qualified tenant/cell/recovery epoch/claim and exact authorization
attempt. Activation context is also bound and checked independently. Gate retains
one operation/effect identity across attempts. Identical retries retain grant ID
and expiry.
Changed bindings conflict and expiration does not silently mint a replacement.

Gate then atomically consumes the grant, acquires one worker/fence, reserves all
applicable action buckets and appends the predispatch outbox event. Its exact
Server acknowledgement is required before final admission. Warden rechecks
current authority and delivers credentials only to the bound isolated connector.
The connector's final conditional Gate call binds its live invocation, current
owner/fence, approval/grant/ticket/lease validity, epoch and acknowledged event.
Only a successful live reply permits one send attempt; lost replies cannot be
replaced by a lookup receipt. No lease takeover resends an uncertain operation.

For the first target, reserve one publication admission against the tenant/target
UTC-hour cap of two. Policy may add root/child bounds; all applicable buckets
share the same transaction and deterministic lock order. Pending and unresolved
exposure carries into successor windows and policy epochs until evidence settles
it. Grant/lease expiration, window rollover and snapshot restore never refund it.
Known no-send/no-effect releases once; verified effect settles once; compensation
requires its own approval/capacity. Gateway model-spend balances remain separate.
Shared task/delegation references are authoritative bindings, not freeform session
labels. They preserve root/child attribution for Gateway later without promising
one atomic transaction across model and action balances. The first synthetic
action has an explicitly admitted standalone root when no parent task exists.

The target atomically validates expected target epoch, stable effect key and
installed recovery/fence floor with its mutation. A worker paused after final
admission can still send later unless the target has installed a newer floor.
No claim of exactly-once effects or instantaneous distributed revocation follows
from grant consumption alone. Preserve ADR 0002's bounded-ticket race explicitly.

## DEC-08: action records and acknowledgements

Prepare a common event envelope with a new `action-record-v1` payload family
through the exporter/re-vendoring process after this semantic review; the name
here is proposed, not a published schema version. Other families receive their
own closed schemas as their owners implement them. Keep Stage 1 schemas, locks,
golden vectors and consumers intact.
The [foundation assessment](../architecture/stage2-foundation-assessment.md)
identifies the current single-result validator that the new path must coexist with.

Each envelope binds version/kind, event ID, qualified authenticated source/stream,
source generation and sequence, predecessor, tenant/cell, payload digest, causal
references and occurrence-time provenance; Server records its separate receipt
time/position. Action payloads require operation/attempt, request digest, actual
mode and scoped activation/recovery epochs. Closed kind-specific payloads bind
the applicable approval, claim, grant, worker/fence, reservation, invocation,
target and acknowledgement identifiers and digests. Unrelated future model,
activation or suspension facts do not require invented action identifiers.
Missing bindings refuse; an opaque freeform payload is not sufficient validation.

The candidate distinguishes approval, claim-created, grant-issued,
consumption-reserved, predispatch, send-intent, outcome and reconciliation facts.
Different legitimate lifecycle facts may share an operation; reusing an event ID
with different bytes or changing immutable operation bindings conflicts. Per-source
sequence gaps refuse acknowledgement until the predecessor is durably present;
the outbox delivers missing predecessors before retrying. Pending delivery is
never an acceptance acknowledgement. Cross-source causality does not imply a
universal event order. Acknowledgements
bind event ID, exact payload/event digests and durable ledger position.

Every authoritative producer writes each operational change and its outbox event
in one local transaction or a qualified equivalent. This includes Council,
Registry and Warden as well as Gate; Server validates each producer/kind binding.
Required pre-send records must be acknowledged before the connector can send.
Post-send Server outage leaves a durable local outcome and recording-pending
delivery; replaying the outbox appends the same event, not a second action. Outcome
and recording status remain separate. Corrections link prior facts; they never
overwrite an uncertain send or manufacture proven-no-effect evidence.

The action-record recovery path must authenticate a currently authorized recovery
recorder separately from the original event's historical source/epoch. It verifies
the retained committed claim, original producer/epoch registration, permitted
event kind and recovery cutoff before accepting a delayed old-epoch audit sequence.
The closed recovery kind set includes proven committed prerequisite facts such
as send-intent as well as outcome/reconciliation; an outcome-only allowlist could
not drain its missing predecessor. Deliver that original sequence in order.
Original event bytes, causal references and sequence remain unchanged. Missing
historical evidence refuses; a fresh principal alone cannot invent an old claim.
Recovery admission cannot create a new grant, final-send permission or current
authority. This is a new compatible path: Stage 1's current-epoch append checks
remain intact. Activation or restore must preserve the evidence needed to drain
old outboxes without granting them new execution rights.

The first action profile has no automatic TTL for minimal operation identity,
outcome or consumed-grant tombstones. Retain original request digest bindings,
unresolved reservations and target/Server references. Sensitive payload retention
is governed separately under ADR 0011; this is not indefinite raw-content custody.
Legacy command idempotency TTL cannot replace this rule. Any later collection
requires a reviewed checkpoint/cutoff
and retention policy; expiry alone cannot make an action reusable.

## Failure histories to turn into real-store tests

These are required oracles, not executed tests. Every case observes target send
and effect counts independently. Inject failure on both sides of each listed
commit or network acknowledgement, retaining every failed attempt.

| ID / boundary | Required recovery / refusal | Reference |
|---|---|---|
| H03-01 approval persisted, reply lost / withdrawal races admission | Same approval/expiry with current status; Gate cancellation wins before send admission or reports too-late after it | REF-03–06/19 |
| H03-02 activation pause or component receipt lost | Same transition lookup/retry; missing receipt leaves Gate paused | REF-18 |
| H03-03 claim or issuance committed, reply lost | Same claim/grant; no new expiry and no send authority | REF-10 |
| H03-04 concurrent consumption / reservation | One atomic winner; all losing writes roll back; cap cannot overbook | REF-08/16 |
| H03-05 predispatch acknowledgement missing/wrong | No connector send; exact event recovery only | REF-12 |
| H03-06 final admission committed, reply lost | Unresolved, no replacement send, capacity held | REF-10/11 |
| H03-07 target commits, receipt lost | Independent lookup determines effect; no resend | REF-11 |
| H03-08 outcome committed, Server unavailable | Durable outbox retries event only; outcome and delivery lag distinct | REF-13 |
| H03-09 owner/revocation/epoch/time changes | Refuse invalid new admission; separately measure prior admitted work | REF-09/14/18/19 |
| H03-10 old snapshot restored after effect | Issuance/dispatch quarantined; no reused consumption or refunded exposure | REF-15 |
| H03-11 unresolved action crosses window | Debt remains charged until evidence-based settlement | REF-17 |
| H03-12 agent probes broker/target/store/mount | Denied by actual network/custody controls, not a cooperative test adapter | REF-07 |
| H03-13 activation/restore changes epoch while send-intent/outcome outbox is pending | Current recovery recorder proves historical claim/source/cutoff; complete old audit sequence delivered once in order, no new dispatch authority | REF-13/15/18 |

Restore reopening requires old-dispatcher exclusion, reconciliation through a
known cutoff, an externally established fresh recovery epoch, retained consumption
and reservation facts and target floor acknowledgement. Incomplete evidence keeps
the cell quarantined. Testing only restored Server authority is not REF-15.

## Consumer changes and review gate

Council needs authenticated human approval and the activation coordinator;
Registry needs staged/active/retired compatibility and exact transition receipts;
Gate needs its action journal, reservations, Linux evaluator profile and isolated
connector; Warden needs claim-bound issuance, online validation and credential
custody; Server needs the compatible action-record path; Harness needs independent
effect observation and the crash/restore runner. Matrix remains read-only and is
not required by this synthetic action. Existing Warden broker experiments are
inputs for review, not already qualified Stage 2 service behavior.

Acceptance must identify the reviewed ADR 0010/0011 revisions, resolve the human identity
and Linux dependency profile, pin schemas/vectors through a subsequent candidate
cut and record the selected persistence/topology. Implementation packets then
name exact inputs, owner, acceptance reviewer, tests and environment limits.
The [preparation plan](../stage2-preparation.md) preserves these gates. No runtime
implementation, contract release, target credential or dispatch is created here.
