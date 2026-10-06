# Proposed reference action and evidence specification

**Proposed integration specification; no executed acceptance evidence.** The first action
is `release.publish_approved_artifact` against the [local profile](reference-profile.md).
Harness should own the executable integration runner and installation recipe; Gate should
own the disposable target/connector fixture and its conformance tests. The hub owns this
cross-component oracle and the accepted protocol definitions, beginning with the
[execution proposal](../decisions/0002-action-execution-protocol.md). No code or contract is
published by this specification, and no real release registry is contacted.

## Exact fixture and independent oracle

Use two fictional tenants, `tenant-a` and `tenant-b`, and a unique run namespace. Each has
a requester and an approver account authenticated by the profile's IdP. The proposer is
an agent delegated by the requester. The approver cannot be that agent or a principal it
controls. Separate accounts test enforcement; two accounts operated by the same human do
not supply independent human-review evidence. Record that limitation explicitly.

| Fixture | Required value or generation rule |
|---|---|
| Artifact A | UTF-8 bytes `munarium reference artifact A\n`, where `\n` is one LF; no BOM |
| Artifact B | Same rule with `B` replacing `A`; digest must differ |
| Source | Commit SHA of the reviewed fixture generator; no invented source revision |
| Build evidence | Fixture-generator test receipt containing command, revision, exit code and artifact digest; no fabricated CI success |
| Manifest | Exact accepted contract bytes for the named action; one disposable target, allowed tenant and artifact digest |
| Policy | Synthetic rule requiring matching evidence, approver, target prior epoch and enforce mode; pin its evaluator/version |
| Target | `sandbox-release` in this run; tenant-specific channel initially at epoch 0 with no artifact |
| Operation | Harness runner persists one stable operation ID with its test intent before first submission; retain it across response loss/restart |
| Approval | Bind all canonical request/context fields, target epoch 0, approver and 300-second expiry |
| Change window | Case setup plus 300 seconds; canonical request binds exact UTC bounds; expiry cases deliberately run outside them |
| Proposed effect | Set that tenant's channel to artifact A and advance epoch 0 to 1 exactly once |

The fixture implementation must expose a mutation endpoint accessible only to the connector
and a read-only observation endpoint with a separate test-observer credential. Persist
operation ID, tenant, canonical digest, target prior/new epoch, accepted recovery epoch/fence
and effect receipt in one target transaction. Atomically compare the requested prior epoch
before mutation; a pre-send read cannot close that race. Reject identity reuse with changed
content and stale fences against the target's installed floor; an exact duplicate returns
the prior receipt without a second effect. Compare source SHA,
artifact bytes/digest and expected epoch, not a human-readable artifact label.

The observer captures effect count and channel state independently of Gate responses and
Server logs. Fault injection can hold a request, crash a worker, fail a durable write or
drop a response **after** the target commit. It must never bypass target authentication,
alter Gate assertions or invent a successful receipt. Test concurrency against the actual
supported Gate/Warden/Server persistence engines with independent worker processes;
in-memory fakes test units only. Target fixtures bound the claim to this target, not to
external APIs with weaker idempotency or fencing.

## Acceptance matrix

Every case records expected and actual decision, durable transitions, Server references,
connector-send count and independently observed target effects. Start each independent
case in a new namespace; use an earlier snapshot only in the explicit restore case.

| ID | Stimulus | Required observable result |
|---|---|---|
| REF-01 | Decision-only allowed and refused proposals | Deterministic replay against pinned inputs; zero grants, sends and effects |
| REF-02 | Approved enforce-mode artifact A | One authorized send/effect; channel epoch 1; proposal-to-outcome chain retained |
| REF-03 | Replace A with B, change target, or reuse ID with new content | Binding/conflict refusal before connector send; approved request preserved |
| REF-04 | Missing evidence, unknown manifest, stale approval or changed target epoch | Pre-admission checks refuse; an epoch change racing admission is atomically rejected by the target with known-no-effect evidence; no effect |
| REF-05 | Agent approves itself or reopens retired bootstrap | Authority refusal recorded; no activation or target call |
| REF-06 | Tenant B reads/replays A's approval, operation or receipt | No disclosure or authority reuse; tenant B's target remains unchanged |
| REF-07 | Agent calls target/broker or mounts connector secrets | Network/credential boundary denies access; record tested denied edges |
| REF-08 | Two workers redeem the same grant simultaneously | One durable consumption/dispatch ownership; losing attempt recorded; one effect |
| REF-09 | Revoke before validation or fail required Warden/Registry/broker check; partition after successful validation separately | Failed checks prevent admission; already validated tickets obey the measured revocation bound; previously admitted effects remain separately accounted |
| REF-10 | Kill worker at every durable-write/network-ack boundary | Durable claims survive; pre-send recovery follows protocol; uncertain sends never repeat |
| REF-11 | Target commits, response is dropped, Gate restarts | Unresolved state and reservation survive; lookup never resends; observation resolves one effect |
| REF-12 | Fail mandatory pre-send record/ack or journal commit | No connector send; failure recorded when storage recovers |
| REF-13 | Fail Server after send while Gate remains durable | Outcome retained in journal/outbox; restored Server receives idempotent reconciliation |
| REF-14 | Resume old worker before final admission, then separately after admission with a new target recovery floor installed | Old ownership fails admission; target rejects a request below its installed floor; no takeover resend; do not claim uninstalled fences can stop admitted requests |
| REF-15 | Restore snapshot from before consumption after one real fixture effect | Dispatch stays disabled pending cutoff/consumption/reservation/target reconciliation, external recovery epoch and target-floor acknowledgement; absent evidence stays quarantined; no duplicate |
| REF-16 | One of two hourly admission slots used; concurrently propose two different publications bound to the current target epoch | Only one obtains the remaining reservation; losing action makes no target call; observe admission separately from effect-completion time |
| REF-17 | Unresolved publication across hour boundary | Reservation remains charged against available capacity until evidence settles it; no automatic release |
| REF-18 | Switch observe/advise/guard/enforce/assure context after approval; fail each activation-barrier acknowledgement | Epoch mismatch blocks admission; failed barrier stays paused; observe/advise creates no grant authority; record guard/enforce/assure scope and pre-barrier admitted work |
| REF-19 | Expired grant, oversized request/artifact or pairwise clock skew beyond profile bound | Refuse before send with stable reason; no retry that silently renews authority |
| REF-20 | Rotate verification keys, remove event interval or alter exported receipt | Valid historical evidence verifies only under declared historical trust; tampering/missing coverage is reported |

Expand REF-10 into a numbered crash-point list when the execution ADR is accepted, with
one test per actual commit/acknowledgement boundary. An unavailable prerequisite makes its
case **unavailable**, never passed. A failed target assertion fails the case even if all
APIs returned success. Stop authority/effect qualification on these failures; retain the
failure and diagnosis rather than silently rerunning it out of the report.

## Experimental run record from the first integrated slice

Begin this record at Stage 1, before running the decision-only scenario. It is an evidence
record, not a released composition manifest, activated policy or `platform-lock.yaml`.
The first implementation chooses its machine-readable serialization and validates every
required field; this table is the review template. Public exports contain fictional data
and sanitized diagnostics only. Do not copy a live environment into a fixture or archive.

| Record group | Required content |
|---|---|
| Identity and scope | Unique run ID; UTC start/end; owner/operator; scenario revision; attempted stage; claimed boundary and exclusions |
| Source pins | Full SHA and clean/dirty state for hub, foundations and each participating component; image/package digests; toolchain versions; qualification requires clean immutable source pins |
| Contract/configuration | Accepted ADR revisions; exact contract/vector/evaluator/policy/manifest digests; nonsecret profile parameters; mode and activation epochs |
| Environment | OS/runtime/database versions; topology and tested deny edges; resource ceiling and observed use; owner, availability, cost authority and expiry |
| Fixture provenance | Generator SHA, seed if any, input/output digests, synthetic identities and target initial state; secret values excluded |
| Commands and outcomes | Exact redacted command/working directory, UTC times, exit status, retained stdout/stderr digest; per-case expected/actual observations |
| Durability and coverage | Operation/claim/grant/reservation IDs, source event IDs and sequence/watermark ranges, ledger/checkpoint references, target receipts, missing intervals; restore cutoff evidence, snapshot digest and recovery-epoch/floor acknowledgements retained outside restored state |
| Results and gaps | Passed/failed/unavailable/skipped per case; reason and owner for each gap; retries linked to original attempts; no removal of failures |
| Retention and teardown | Artifact inventory/digests/access class, retention expiry, resource cleanup receipts, remaining resources and responsible operator |
| Review | Reviewer identity and scope when supplied; independence limitations; exact record revision reviewed; pending review stays pending |

Keep failed attempts immutable and append corrections with links to the original. Stable
event IDs enable duplicate detection; per-source sequence numbers and declared watermarks
detect gaps without assuming a universal event order. Store causal references across
services. Distinguish missing data, restricted data and a legitimately empty event range.
Sentinel/Assure consume these fields early; their later arrival cannot reconstruct events
that the first slice never recorded. Formatting, schema validity and documentation checks
prove none of the scenario's runtime authority or recovery claims.

Evidence retention and offline verification trust are separate lifecycles. Package exact
signing key identifiers, algorithms, signed ranges, checkpoints and available time evidence;
the verifier obtains trusted anchors and revocation/rotation policy independently of the
package under test. Preserve historical public verification material for the retention
window while retiring operational private keys. Report missing historical trust, compromised
keys, unverifiable time or expired retention as limitations; do not silently trust a key
because it arrived with the evidence. This packet does not authorize signing or key changes.
