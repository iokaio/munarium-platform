# Platform contract second pass

**7 October 2026; design review, human disposition pending.** Reviewed the pinned
[Stage 1 inputs](stage1-review-inputs.json), [HUB-03](../decisions/0010-stage2-authority-durability.md)
and the [full platform plan](../platform-plan.md), including Gateway, Sentinel,
Assure, Console, Matrix provenance, policy lifecycle and federation. This review
changes proposed semantics in [ADR 0011](../decisions/0011-platform-contract-evolution.md)
and clarifies ADR 0010. It does not replace existing candidate bytes or claim new
runtime behavior. Source observations below apply to the acceptance packet's pins.

## Recommendation

Review Stage 1 for its bounded decision-only use, preserving its existing recovery
behavior. Do not freeze that envelope as the final platform-wide contract. Before
the next action schema cut, settle durable identity/attempt binding, qualified
references and epochs, scoped activation and shared event semantics. Those choices
affect the next implementation directly. Preserve extension boundaries for later
components without bringing their runtime work forward in the parallel plan.

## Findings and disposition

“Next cut” means a requirement for new Stage 2 schemas/vectors, not a defect to
patch into Stage 1 or a claim that a reviewed schema already exists. “Later” still
requires a decision before its consumer implementation. Plan section references
below refer to the linked full platform plan.

| ID / priority | Observation and longer-term consequence | Proposed disposition / owner |
|---|---|---|
| CR-01 / next cut | Foundation `principal` includes validity times; `request` binds its digest. Durable operation identity must survive refreshed authentication and explicitly re-evaluated context (plan 17). Existing recovery already separates the current caller from original bytes. | Separate enrolled subject, proof, immutable intent and authorization attempt; preserve the original Stage 1 archive. Gate/Warden/Council jointly enforce no replacement of unresolved effects. |
| CR-02 / next cut | Unqualified IDs and a generic epoch cannot distinguish two cells, issuer generations, activation and target fencing (plan 16.3, 22). Registry v2 `operation_id` also names a capability rather than a request instance. | Typed qualified references and separately scoped epochs; explicit capability-operation mapping. Single home-cell admission; cross-domain execution refused. Hub/Gate/Warden/Registry. |
| CR-03 / next cut | A flat artifact set and hardcoded receipt list can become ambiguous when Gateway participates in activation (plan 10, 19). | Scope and participant-set digest, explicit partial/applied/active states, not-before/expiry and fresh rollback epoch. Council/Registry; Gate controls resume. |
| CR-04 / next cut | ADR 0010's initial envelope required action fields on every event; foundation event kinds are proposal/decision/refusal and Server rejects a second different non-proposal for one operation. These are not a model, activation or suspension ledger (plan 12–14). | Common envelope with closed payload families and separate conflict rules; producer-owned transactional outboxes, qualified source streams and historical recovery. Server/all producers. |
| CR-05 / next cut boundary; later runtime | Action and model budgets need shared root/child attribution, but two independent commit owners cannot promise one atomic shared cap (plan 12, 17–18). | Bind verified task/delegation lineage now; preserve separate balances and one owner per shared limit. Defer model pricing/settlement payload implementation to Gateway/S8. |
| CR-06 / next cut boundary; later kinds | Registry v2 currently permits only `distinct-approval` obligations. Freeform later obligations could silently lose monitoring, disclosure or quorum enforcement (plan 12–13, 18). | Versioned typed kinds, enforcing owner and evidence; unknown required kinds refuse. Add only first-profile kinds now, new reviewed versions later. Gate/Registry/Harness. |
| CR-07 / define now; later S5/S6 | Event integrity alone cannot tell Sentinel or Assure whether a range is missing, withheld, aggregated or complete relative to its sources (plan 13–14, 16.3). | Stable scope/cutoff/cursor and coverage vocabulary; independent trust context and explicit omissions. No claim of world-wide completeness. Server/Sentinel/Assure. |
| CR-08 / next cut retention boundary | No automatic tombstone expiry is necessary for non-reuse, but must not imply permanent retention of every sensitive payload (plan 14, 16.3). | Minimal durable identity/exposure facts separated from controlled payload refs; explicit removal and lost replay. Server/Gate/Assure. |
| CR-09 / define now; later UI/suspension | Approval, HTTP success and Warden suspension acknowledgement are not target completion or observed enforcement (plan 13, 15). | Orthogonal outcome/workflow/effect/recording states, revision-bound API commands, suspension propagation evidence. Council/Warden/Gate; Console/Sentinel later. |
| CR-10 / next cut profile | Binding protocol semantics to Linux/PostgreSQL/one IdP or OPA would constrain on-premises, air-gapped and future engine profiles (plan 19, 22). | Pin those as qualification-profile choices, not universal wire requirements; no automatic transfer of evidence to another profile. Hub/Harness/all services. |
| CR-11 / preserve boundary; later federation | A single allow or policy digest cannot prove parent constraints and both-domain permission (plan 19.3, 22). | Typed dependency set now; later explicit deny-overrides, trust, expiry and budget protocol. No speculative federation implementation. Council/Gate/Warden. |
| CR-12 / next cut context; later query/export | A source digest or ledger acknowledgement alone does not establish authoritative evidence, current access or reproducibility (plan 16–18). | Bind trust authority, source/derivation/field scope and freshness; retain corrections, actual mode and point-in-time pins. Matrix logical results and artifact bytes remain distinct. Gate/Server/Matrix. |

The foundation observations are inspectable in
[foundation.schema.json](../decisions/candidates/foundation.schema.json),
[Registry v2](../decisions/registry-v2/README.md) and the pinned-source
[Server assessment](stage2-foundation-assessment.md). The
[Stage 1 recovery ADR](../decisions/0009-stage1-recovery-profile.md) supplies the
existing immutable-request/current-caller distinction. Candidate schemas are
closed, so these additions require new versions rather than optional unvalidated
fields. None of these findings establishes a deployed vulnerability.

## Acceptance cases for the new candidates

These are required future vectors/integration oracles, **not executed tests**.
Use independent clients for wire interpretation and real stores for concurrency,
restore and outbox claims. Retain HUB-03's H03-01–13 failure histories as well.

| ID | Counterexample / required result | Delivery gate |
|---|---|---|
| EV-01 | Refresh a token for the same enrolled subject: original request/operation/effect identity remains unchanged; current access is rechecked. Another subject cannot recover it. | Next request/identity cut |
| EV-02 | Re-evaluate policy while a claimed send is unresolved: a fresh attempt/grant cannot bypass its effect key or reservation. Concurrent unclaimed-attempt supersession has one winner; missing issuance-closure/admission-disable receipts or prior consumption prevents claim replacement. | Action journal and approval |
| EV-03 | Reuse an object ID in another tenant/cell/domain or substitute activation epoch for target fence: refuse before admission. | Qualified references and target profile |
| EV-04 | Swap manifest capability-operation and request-instance identifiers: validation refuses; the adapter preserves their distinct meanings. | Manifest/request vectors |
| EV-05 | Add an unknown mandatory obligation or required activation participant: refuse, leaving admission paused when a transition has begun. No dropping fields or downgrade. | Profile and activation |
| EV-06 | A child omits its admitted parent or changes a session label to evade a root limit: refuse/recover verified lineage; never allocate a second root balance implicitly. | First task bindings; Gateway later |
| EV-07 | Deliver Council/Warden/Registry events after crash or out of order: immutable replay, per-stream continuity and original outcome; no new authorization from archive delivery. | Shared records; real-store producers |
| EV-08 | Deliver a model/suspension event to an action-only consumer: explicit unsupported interpretation; an opaque archive receipt cannot satisfy validated admission. | Envelope compatibility; later families |
| EV-09 | Export an interval with lag, withheld data or aggregation, then revoke the reader between pages: explicit coverage and current-access refusal; no silent complete/live view. | S5/S6 and Assure |
| EV-10 | Remove a retained payload under governance: effect tombstone remains non-reusable; replay reports missing content, not successful verification. | Retention before collection is enabled |
| EV-11 | Lose the suspension reply or pause a worker after acknowledgement: same request status, measured propagation and separate already-admitted effects; expiry cannot restore revoked authority. | Sentinel/Warden suspension |
| EV-12 | Resubmit a stale Console approval with a current login: expected revision/context conflict; no changed content behind the approval button. | Council API now; Console later |
| EV-13 | Install compatible bytes on an unqualified OS/store or omit a required schema version: no qualification inheritance or execution fallback. | Candidate/profile compatibility |
| EV-14 | Local allow conflicts with a mandatory parent deny or destination refusal: no cross-domain permission. | Federation; first profile refuses cross-domain |
| EV-15 | A stream is cancelled without final provider usage: retain bounded unknown exposure; unknown price never becomes zero. | Gateway/S8 |
| EV-16 | Supply hashed agent assertions as authoritative target evidence, substitute a shadow allow, or reuse cached lineage after its trust/access context changes: refuse admission; preserve the original historical decision. | Action context; later query cache |

## Impact on the parallel plan

Keep the current HUB-03 preparation lane and confirmed Server foundation lane.
The immediate deliverable is reviewable semantics, then a separately pinned
request/approval/activation/action-record candidate cut and its compatibility
vectors. Do not schedule Council/Gate/Warden against an unidentified schema or
implement the later Gateway, Sentinel, Assure and Console runtimes in this packet.

Stage 1 acceptance remains explicitly scoped to decision-only versions and the
tested Windows profile. Accepting that scope must not be recorded as acceptance
of permanent platform-wide identity, event or federation definitions. The
[preparation plan](../stage2-preparation.md) carries the revised next-cut gate;
human contract acceptance and runtime authorization remain pending.

## Verification of this review change

Local checks passed on 7 October: `python check_license.py`,
`python scripts/docs_linkcheck.py` (49 Markdown files),
`python scripts/private_material_scan.py` (131 files), all 60 existing tests via
`python -m unittest discover -s scripts -p "test_*.py"`, and `git diff --check`.
The `py` launcher was unavailable; the same checks ran with `python`. Gitleaks
was unavailable, so no local gitleaks success is claimed. Hash comparison with
the pre-review files confirmed no candidate schema, vector, lock or pinned review
input changed. No runtime qualification was rerun or new acceptance case claimed
as executed; EV-01–16 and H03-01–13 remain implementation/review obligations.
