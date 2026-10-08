# Stage 2 next steps

Maintainer-directed implementation, 7 October 2026. This preserves the reviewed plan; actual results are recorded separately.

**The next stage is to finish Stage 2’s first controlled action path, starting with Council and Registry.** Stage 2 has already begun: its contract candidate and Server action-record foundation are merged. The parallel build plan’s “next pair” still points to preparation that has largely happened.

I reviewed the planning and acceptance documents, component source, local branches/worktrees, and current GitHub PR/CI state. No files were changed or tests rerun for this review.

**Current position, verified on 7 October 2026**

| Area | Observed state | What remains |
|---|---|---|
| Stage 1 | Experimental decision-only services and recorded integration evidence | Exact contract dispositions, composition/provenance evidence and independent review remain open |
| Hub / HUB-03 | Candidate merged through [PR #14](https://github.com/iokaio/munarium-platform/pull/14), main `d51aa16`; hygiene passed | Runtime integration details and qualification evidence |
| Server / S2-A | Action records merged through [PR #76](https://github.com/iokaio/munarium/pull/76), main `61a350a`; exact-commit Server, client and hygiene workflows passed | Activation participation and integrated action/recovery evidence |
| Council | Rust interfaces only | Authenticated human approval, durable storage, activation coordination |
| Registry | Authenticated candidate inventory; candidates remain inactive | Activation, compatibility, retirement and durable transition receipts |
| Gate | Working decision service; action journal and connector remain interfaces | PostgreSQL action transactions, reservations, fencing and controlled dispatch |
| Warden | Working identity service plus experimental grant/broker libraries | Authenticated Stage 2 endpoints, Gate integration and qualified credential isolation |
| Harness | Stage 1 composition tests | Actual effect observation, isolation checks and Stage 2 failure histories |

There are no open PRs in the seven Stage 2 repositories checked. Existing worktrees remain in place; the open Stage 1 closeout worktree is an older snapshot.

The [implementation packet](stage2-implementation.md) is more current than the [parallel plan](parallel-build-plan.md). It identifies the remaining work as C2-A, G2-A and H2-A. Its Server evidence also predates the final merge and successful main-branch CI.

**The milestone I would work toward:** one precisely approved synthetic `release.publish_approved_artifact` operation, executed through isolated services, with durable evidence and safe handling of crashes, lost replies and restoration.

Here is the detailed sequence.

1. **Reconcile the baseline and create bounded implementation packets.**

   I will update the planning cross-references to show HUB-03 candidate preparation and S2-A as implemented, preserving their qualification limits. I will pin the merged hub and Server revisions alongside the unchanged component revisions, verify candidate/export digest agreement, and retain the original Stage 1 acceptance pins.

   Each packet will name its repository, permitted files, contract inputs, tests, environment, evidence destination, owner, reviewer and effort ceiling. Formal acceptance fields will remain pending unless an actual disposition is supplied.

   **Exit:** one consistent implementation baseline and an accurate dependency map; no repeated foundation assessment or Matrix extraction.

2. **Complete the runtime interface and environment intake.**

   I will resolve the remaining concrete service interfaces for approval lookup/withdrawal, activation receipts, claim lookup, grant issuance, credential delivery and final-send admission. Shared semantic choices will be recorded in the hub before consumers implement them. Existing candidate bytes will remain immutable; necessary wire changes will use a new version.

   I will also establish the Linux execution profile: pinned evaluator and resource limits, PostgreSQL journal, human identity admission, broker, service identities and permitted network paths. Environment availability, ownership, resource limits, expiry and cleanup must be observed and recorded before scheduling qualification.

   **Exit:** consumers have explicit interfaces and a reproducible test profile. The existing Windows evaluator evidence will not be counted as Linux qualification.

3. **Implement Council’s durable approval service.**

   I will build the minimal authenticated service and command-line approval path. Council will obtain authoritative request/decision inputs, verify a currently eligible enrolled human, and bind approval to the exact operation, attempt, request, context, decision and expiry.

   Storage will preserve approval history, immutable retries and current status. Approval changes and their outbox records will commit together. Withdrawal will remain pending until Gate supplies the matching durable cancellation receipt; a lost response will not imply successful cancellation.

   **Exit:** component tests demonstrate request binding, unchanged retry expiry, self-approval refusal, tenant isolation, restart recovery and durable recording. Withdrawal integration completes once Gate’s cancellation path exists.

4. **Implement Registry activation and the complete activation barrier.**

   I will add verified artifact-set staging, compatibility checks, expected-prior-state updates, retirement handling and idempotent transition receipts to Registry. Council will coordinate the transition and persist its progress.

   This step also needs bounded participant work in **Gate, Warden and Server**: durable pause, participant application receipts, matching epoch installation and conditional resume. This dependency is insufficiently explicit in the current two-machine table.

   I will inject failures after each participant commit and acknowledgement. A Registry pointer change must never be reported as complete cell activation while another participant is missing.

   **Exit:** the same transition resumes safely after interruption; incomplete receipt sets keep action admission paused; rollback requires a new governed transition.

5. **Implement Gate’s PostgreSQL action journal and capacity accounting.**

   I will implement durable operation/attempt bindings, claims, cancellation tombstones and worker ownership. Gate will own the transaction that consumes a grant, acquires the worker fence, reserves every applicable action limit and writes the required outbox event.

   The initial profile permits two publication admissions per tenant/target UTC hour. Pending and uncertain exposure will remain charged across window changes and restarts until evidence settles it. Retries will recover existing work without silently creating another send opportunity.

   **Exit:** real PostgreSQL race and restart tests establish one winner, no overbooking, exact acknowledgements and no automatic release of unresolved exposure.

6. **Integrate Warden, the isolated connector and the synthetic target.**

   I will adapt Warden’s existing experiments to the selected Stage 2 protocol: authenticated claim lookup, stable grant issuance, current authority checks, revocation and connector-bound credential delivery.

   Gate will require the exact predispatch acknowledgement before final-send admission. The connector will require a successful live admission response. Lost admission responses and uncertain target outcomes will remain unresolved.

   The synthetic target will atomically enforce its precondition, stable effect identity and installed recovery/fence floor with the mutation. Harness will independently observe sends and effects and probe denied agent access to the broker, target, database and secret mounts.

   **Exit:** one approved action succeeds, invalid actions refuse, and isolation is demonstrated from the actual agent boundary.

7. **Complete Harness crash, recovery and restore testing.**

   I will implement the [H03 failure histories](decisions/0010-stage2-authority-durability.md) and [REF-02–19 scenarios](architecture/reference-scenario.md) against actual services and persistence.

   Coverage will include concurrent redemption, approval withdrawal races, partial activation, wrong/missing acknowledgements, process death, target commit with lost response, Server outage, stale workers, revocation, clock bounds and unresolved capacity across windows.

   Restore testing will start from a snapshot predating a real synthetic effect. Dispatch must remain quarantined until cutoff reconciliation, retained consumption/reservations, external recovery epoch and target-floor acknowledgement establish safe reopening. Historical outboxes must drain without gaining execution authority.

   **Exit:** a per-case evidence matrix records actual results, failed attempts and omissions, with independent target observations. An uncertain operation is never automatically resent.

8. **Produce installation, investigation and acceptance evidence.**

   I will package a reproducible disposable installation and teardown procedure, plus instructions for investigating pending approval, partial activation, unresolved dispatch, recording lag and restore quarantine.

   The final evidence packet will pin source revisions, candidate digests, binaries/images, environment and test receipts. Validation will follow each repository’s actual workflows; any Server changes will include its complete gate-catalog formatting/regression entry point and relevant store/transport checks.

   **Exit:** a reviewable Stage 2 experimental composition with explicit support limits. Qualification, contract acceptance and release status will reflect supplied evidence and human disposition.

**Proposed two-machine allocation**

| Sequence | Machine A | Machine B | Review gate |
|---|---|---|---|
| Baseline | Hub reconciliation and interface decisions | Runtime/environment assessment | Exact shared inputs |
| Approval | Council approval service | Registry activation storage | Durable component behavior |
| Activation | Council coordinator | Gate/Server/Warden participant adapters, sequentially owned | Complete barrier recovery |
| Execution | Gate journal and reservations | Warden grants and credential custody | Atomic admission and custody |
| Integration | Harness and independent target oracle | Linux isolation, fault injection and bounded fixes | REF-02–19 evidence |
| Closeout | Evidence and operator documentation | Reproduction and remaining fixes | Stage 2 acceptance packet |

I would keep the existing limit of two bounded implementation tasks awaiting review, with one owner for hub edits and one for Server edits. Harness test design should begin alongside implementation so fault-injection points are built into the services.

**The first concrete implementation pair is Council approval plus Registry activation storage.** Calendar estimates should follow the runtime-profile intake and initial PostgreSQL protocol work; the older roadmap month ranges are not reliable estimates for the remaining implementation.
## Progress on 8 October 2026

The [live execution review packet](stage2-implementation.md#live-execution-review-packet-8-october-2026)
connects the merged journal to live Warden grant/OpenBao custody, Council approval
custody, Gate's final-send transaction and an independently persisted synthetic target.
Real tests cover effects, lost replies, withdrawal, target recovery-floor refusal and
restoration of a pre-effect PostgreSQL snapshot into quarantine. Five owner PRs are
prepared for review; their exact source pins and evidence limits are in that packet.

Steps 6 and 7 now have experimental prepared-release implementation and real fault
histories. They are not complete qualification: dynamic Linux evaluation, OS isolation,
automatic rollback detection, retained-fact/cutoff reconciliation and safe reopening
remain required before general execution. The current profile accepts only signed
operator-prepared disposable requests and cannot reopen a restored store by boolean.
