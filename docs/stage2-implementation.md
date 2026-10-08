# Stage 2 implementation direction and bounded packets

## Participant delivery and journal review, 7 October 2026

After the maintainer confirmed the preceding three merges, Server, hub, Harness,
Council, Registry, Gate and Warden were refreshed from `origin/main`. Verified
new merge heads are Server `7d4a4d8`, hub `748dc42` and Harness `887d38b`.
The two current bounded tasks are participant outbox delivery across its owners
and Gate journal persistence, following the intake in
[ADR 0014](decisions/0014-stage2-service-integration.md#participant-delivery-and-action-journal-intake).

| Component review | Exact implementation input | Behavior |
|---|---|---|
| [Gate PR 4](https://github.com/iokaio/munarium-gate/pull/4) | `f8df9736045214c204921f358b296c27d58fc868` | PostgreSQL immutable claims, cancellation tombstones, atomic grant/worker/capacity admission, ordered action custody and participant delivery |
| [Warden PR 5](https://github.com/iokaio/munarium-warden/pull/5) | `f0bfdda6d11060dccdbc4cefc2a5b805c44c0d87` | Current owner identity, immutable activation events and exact Server acknowledgement persistence |
| [Registry PR 5](https://github.com/iokaio/munarium-registry/pull/5) | `91d4305a3241c9f3bf4e5cf011400d4a6e5b2353` | The same delivery boundary with Registry-owned SQLite transactions and retained receipt intent |

Local Rust 1.98.1 formatting, locked offline build, warnings-denied Clippy, default
tests and documentation checks passed in all three components. Gate's five explicitly
selected real PostgreSQL tests passed, covering concurrent writers, competing
workers and capacity, exact retry, cancellation, pause, multi-bucket rollback,
ordered acknowledgements, tenant isolation and unresolved capacity after restart
and UTC-hour rollover. Warden/Registry delivery tests passed across SQLite reopen.
Native Gate and Warden authenticated activation tests passed. Registry's library
also passed without default features. Local gitleaks was unavailable; hosted
secret scanning remains enabled. Warden's optional live OpenBao test was not rerun.

Harness's extended five-service test passed locally against separate disposable
Server/Gate databases, real Warden assertions and Server audit custody. For each
participant it rejected a reader flush and a substituted acknowledgement, lost
the real committed reply, restarted the owner and recovered the original Server
acknowledgement. The preceding six activation interruption cases remain enabled.
The first attempt failed because the fixture supplied duplicate provider bindings
for one workload subject; the corrected unique enrollment passed. Failed and
successful attempts remain retained locally rather than relabelled.

The second pass added explicit installed-artifact-set checks to the journal,
ordered custody checks, direct rollback assertions and Registry feature gating.
This is an advisory implementation review, not supplied human acceptance.
Component hygiene passed. The hub root filesystem scan found scanner fixtures
inside existing nested worktrees; those files were preserved. The unchanged
checks passed on the proposed hub content in an isolated review worktree.

**Execution remains closed.** The journal is a trusted owner-local storage API;
action-source/claim/cancellation service adapters, live Warden grant/custody,
final-send admission, evidence-based settlement, attempt closure, restore quarantine
and target-floor/isolation qualification remain subsequent integration work.
Participant delivery and completed activation do not satisfy those controls.
No candidate bytes, Stage 1 acceptance pins or release labels changed.

### Exact-head hosted checks

All checks passed on the component heads above and Harness
`07f3aa5363d23e11a3c90a3cc08721092a9faa9a`
([PR 4](https://github.com/iokaio/munarium-harness/pull/4)). Runs:

- [Gate Rust/PostgreSQL/native/evaluator](https://github.com/iokaio/munarium-gate/actions/runs/37730652030),
  [hygiene](https://github.com/iokaio/munarium-gate/actions/runs/37730652108) and
  [DCO](https://github.com/iokaio/munarium-gate/actions/runs/37730652006).
- [Warden Rust/native/identity-core](https://github.com/iokaio/munarium-warden/actions/runs/37730655916),
  [hygiene](https://github.com/iokaio/munarium-warden/actions/runs/37730655905) and
  [DCO](https://github.com/iokaio/munarium-warden/actions/runs/37730655929).
- [Registry Rust](https://github.com/iokaio/munarium-registry/actions/runs/37730657900),
  [hygiene](https://github.com/iokaio/munarium-registry/actions/runs/37730657885) and
  [DCO](https://github.com/iokaio/munarium-registry/actions/runs/37730657993).
- [Harness Linux composition](https://github.com/iokaio/munarium-harness/actions/runs/37730811209),
  [Rust/Python](https://github.com/iokaio/munarium-harness/actions/runs/37730811175),
  [hygiene](https://github.com/iokaio/munarium-harness/actions/runs/37730811176) and
  [DCO](https://github.com/iokaio/munarium-harness/actions/runs/37730811172).

The hosted composition artifact records clean source trees, Server `7d4a4d8`,
Council `6ea0822`, the exact Gate/Warden/Registry heads above, and GitHub's Harness
test merge checkout `295b0f4666e96c36a8a831af310983f31f6b75c6`. Its scenario passed
in 38.33 seconds, with participant delivery included and execution excluded.
The retained log digest is
`sha256:092759e4402f3ed5d6978c7a5e8f03a0e5a7da5eba07e7c6f54c919165e103fb`.
These checks establish experimental storage and composition behavior, not human
review or effect qualification. The disposable local PostgreSQL container and its
volume were removed after verification; hosted job cleanup also passed.

**Maintainer directed, 7 October 2026.** Following candidate PR 14, the maintainer
instructed “Proceed with implementation.” Use hub candidate source
`2fb118909633264fad23ede2e7c9942aba374312` and bundle
`8aca66588c87107a0c7a7720c68f921dfd2bdcaecf6433728afa4b1c51420aa6` as the exact
experimental inputs. PR 14 was open when implementation started. This direction
authorizes implementation against that recorded candidate; it does not claim the
PR was merged, the wire was released, or independent qualification occurred.

Source, tests, additive migrations, exported candidate copies, supporting
documentation and build/test workflow changes necessary for the bounded packets
below are included. Existing Stage 1 APIs, candidate bytes and evidence remain
unchanged. Use separate branches and component PRs; record dependency on the exact
hub input. No release, merge, deployment, production trust or paid resources are
authorized. Disposable local/CI resources may use synthetic identities, test-only
keys and loopback listeners with no production trust. No external model calls.

| Packet / owner | Initial source | Deliverable and required evidence |
|---|---|---|
| S2-A / Server | `7cc0c97fe124d446064bb8cf0dfcb6d868d04987` | Separate action artifacts/events, exact acknowledgements, authenticated admission and historical recovery; independent Rust vector consumption, memory/PostgreSQL race/reconnect tests and REST/gRPC parity |
| C2-A / Council and Registry | Council `3d24d637cd5668c10e6ec514554beb6ed3e1d3f5`; Registry `4ab7f4b3a9f77d16e74e44611de4a526e8c75eb9` | Distinct human approval and bounded activation coordinator/receipts, durable outboxes and partial-transition recovery; no implicit execution |
| G2-A / Gate and Warden | Gate `5f8957e25cff0398f8cda7359e6397e840232835`; Warden `7aabbf4a5336cbf29ee7ef26f3baf8a7078770fb` | Gate-owned claims/consumption/reservations, online grant/custody checks and final-send fencing; preserve immutable retries and unresolved exposure |
| H2-A / Harness | `926624e0cb4e1d5af1996308cfaed108204a3854` | Independently observed synthetic effects, deny edges, H03 crash histories and REF-02–19 with retained failures and omissions |

The founder remains accountable owner/reviewer. Implement prerequisite packets
first and retain the two-packet review limit. Server owns its code and admission
binding; the hub records shared semantics before dependent consumers implement
them. [ADR 0013](decisions/0013-action-record-admission.md) specifies S2-A's first
service adapter. Later packet intake must add concrete runtime/profile pins and
test-environment observations before scheduling its live qualification. An offline
or memory-store success cannot substitute for a required real-store/effect test.

## S2-A implementation evidence, 7 October 2026

Subsequent read-only verification found hub PR 14 merged at
`d51aa1681a18ab57687f88f92cf07565b0f77df2` and Server PR 76 merged at
`61a350a98953837e2b1b6564608c5b6957873ae9`. Server's exact-merge
[server-ci](https://github.com/iokaio/munarium/actions/runs/37707715091),
[clients-ci](https://github.com/iokaio/munarium/actions/runs/37707715121) and
[hygiene](https://github.com/iokaio/munarium/actions/runs/37707715194) runs completed
successfully. Hub's exact-merge
[hygiene](https://github.com/iokaio/munarium-platform/actions/runs/37707211035)
also completed successfully. These results supplement, rather than rewrite, the
earlier local evidence below. The maintainer then directed implementation of the
[next-step plan](next-steps.md), including tests, a second pass and review PRs;
[ADR 0014](decisions/0014-stage2-service-integration.md) records that boundary.

Server source [489e9f2bf276195f2028fd549cce69018ae075d0](https://github.com/iokaio/munarium/commit/489e9f2bf276195f2028fd549cce69018ae075d0)
implements [ADR 0013](decisions/0013-action-record-admission.md). It exports the
exact candidate into a new namespace, adds action artifacts/events to protected
ledger custody and exposes archive, append, operation/transition lookup and
source-head through the shared authenticated REST/gRPC handler. No new dependency,
applied migration change or execution path is included.

Observed local checks:

- Rust 1.98.1 on Windows: package formatting; warnings-denied Clippy for core,
  memory store, PostgreSQL store and Server, including all targets; Server build.
- Core and memory suites: 115 tests passed, including both Stage 1 regression
  tests and the new action lifecycle, denial, race and recovery checks. All 19
  candidate canonical records/digests and the aggregate export hash were independently
  consumed by Rust; this is not all of the hub oracle's contextual cases.
- Six Server authority tests and six documentation-coverage tests passed.
- Both explicitly selected PostgreSQL event tests passed: Stage 1 regression and
  Stage 2 lifecycle, duplicate writers, reconnect, tenant isolation and bounded
  recovery. The disposable loopback database used cached pgvector image
  `sha256:9b05db12a35460fff0587e009f9326e414a53e9484555547f96d214a2ba98ef7`;
  its container and volume were removed after verification.
- Four existing authority/records transport cases and two new Stage 2 transport
  cases passed against actual memory/PostgreSQL Server processes. An initial new
  fixture exceeded the existing 60-second identity lifetime and was correctly
  refused; corrected valid input and explicit over-lifetime refusal both passed.
- Python test lint/format, client source type checking, license, compatibility,
  private-material scan, documentation links, crate/retrieval/datastore boundaries,
  additive-migration checks and diff whitespace passed.

CI remains enabled with explicit PostgreSQL and mTLS Stage 2 selections. Local
checks do not claim remote CI success. The full Server release/enterprise/cluster
ladder was not rerun; local gitleaks was unavailable. No target effects, remote
Gate journal verification, human eligibility, credential isolation or Linux
reference qualification are claimed. C2-A, G2-A and H2-A remain unimplemented by
this packet. Review S2-A's evidence before starting the next major capability
slice, following the [parallel-build integration gate](parallel-build-plan.md).

## C2-A first component pair awaiting review, 7 October 2026

The first two implementation tasks are committed and published for substantive
review. Both consumed the unchanged candidate exported from hub `d51aa16`.

| Component | Review input | Observed CI on that exact head |
|---|---|---|
| Council | [PR 2](https://github.com/iokaio/munarium-council/pull/2), `c8103eddadbd5bbd0efd856b85c3d7b2a7e58731` | [Rust and real mTLS process tests](https://github.com/iokaio/munarium-council/actions/runs/37714558962), [hygiene](https://github.com/iokaio/munarium-council/actions/runs/37714558889) and [DCO](https://github.com/iokaio/munarium-council/actions/runs/37714558851) succeeded |
| Registry | [PR 4](https://github.com/iokaio/munarium-registry/pull/4), `1ab730c8b658f957a722826da411a5982d31c34e` | [Rust](https://github.com/iokaio/munarium-registry/actions/runs/37714561999), [hygiene](https://github.com/iokaio/munarium-registry/actions/runs/37714562070) and [DCO](https://github.com/iokaio/munarium-registry/actions/runs/37714561990) succeeded |

Council implements durable request-bound human approval, immutable retries,
pending withdrawal, approval issuance outbox and resumable activation coordination.
Its nine Rust integration tests and native mTLS process scenario passed locally.
The process scenario uses synthetic authenticated dependency servers; it does not
establish integration with Gate's future source/cancellation routes. The first TLS
fixture failed for a missing CA key-usage extension; the corrected fixture passed
with certificate verification retained.

Registry implements separately authorized activation, expected-head concurrency,
exact receipt recovery and retained explicit retirement. All 29 Rust tests and one
documentation test passed locally. The second implementation pass corrected
Council withdrawal receipt revision binding and Registry's distinction between
supersession and explicit retirement. Formatting, warnings-denied lint/docs and
component hygiene checks passed. Local gitleaks was unavailable; CI hygiene passed.

These two tasks fill the plan's limit on implementation tasks awaiting substantive
review. Neither PR is merged. C2-A is still incomplete: Gate/Server/Warden activation
participants, full barrier recovery and remaining activation/withdrawal audit
delivery need implementation and real composition tests. Runtime environment
qualification, G2-A execution, H2-A crash/restore/isolation evidence and the final
installation/acceptance packet also remain outstanding. No target effect or Stage 2
qualification is claimed. Review this pair before opening the next dependent
implementation packet; the next work is the activation barrier and its failure
tests, followed by the execution and Harness sequence in the next-step plan.

## Participant review pair, 7 October 2026

The maintainer reported all three preceding PRs merged and directed continuation.
GitHub confirmed hub PR 16 at `27c3e6c71a3030b209725778bacd88c00f6ff165`,
Council PR 2 at `6ea0822b6ad2da29ca051410289422d9ccaa4c54`, and Registry PR 4
at `eb08f75deaae664afd067194241ae4646c3d53ce`. These merge observations supplement
the historical review snapshot above; they do not close formal acceptance gates.

The next two bounded implementation tasks are:

| Component | Review input | Implemented boundary |
|---|---|---|
| Gate | [PR 3](https://github.com/iokaio/munarium-gate/pull/3), `663c513317e03ec94380257e3800a650b6162de7` | PostgreSQL pause/apply/resume barrier, scope-row concurrency, exact receipt recovery and independently authenticated participant evidence |
| Warden | [PR 4](https://github.com/iokaio/munarium-warden/pull/4), `98fa5d6a86d66d85277090d3d3ee90bdd128c3bb` | Current Council/Gate/Registry admission, SQLite expected-head application and durable receipt/outbox |

Both preserve the candidate bundle. Gate's earlier export retains hub `d51aa16`
as its source; Warden's exporter records `27c3e6c`. Their bundle hashes agree.
The participant intake amendment to ADR 0014 was recorded before implementation.
Server remains unchanged at `61a350a` and its participant adapter is the next
review task, alongside the remaining activation audit/composition work.

Local Rust 1.98.1 formatting/build and warnings-denied Clippy/docs passed.
Gate's ten ordinary tests and both explicitly selected real PostgreSQL tests passed.
Warden's 27 ordinary tests and identity-core commands passed; the unrelated live
OpenBao test was not run. Native mTLS tests passed against each actual binary,
including process kill/restart, coordinator/reader separation, unknown/agent/
foreign-tenant refusal, missing or stale dependencies and governing-revision changes.
Dependency services were synthetic authenticated fixtures, not the complete
composition. License, private-material, documentation and whitespace checks passed.

The second implementation pass tightened expected-refusal assertions so timeouts
cannot count as authorization refusals, added current-authority churn and specifically
missing Server coverage, and reviewed current-head versus historical receipt checks.
An initial SQLx umbrella dependency conflict was resolved with exactly pinned core
and PostgreSQL crates; an initial test compilation error was corrected before the
passing runs. Gate's unchanged Windows evaluator gate failed locally on positive
allow/deny controls both inside and outside the sandbox. No evaluator limits or
checks were weakened. Its exact-head hosted
[Windows evaluator job](https://github.com/iokaio/munarium-gate/actions/runs/37718889131/job/113121700541)
subsequently passed. Local gitleaks was unavailable. Gate's exact-head
[Rust/PostgreSQL/native-service workflow](https://github.com/iokaio/munarium-gate/actions/runs/37718889131),
[hygiene](https://github.com/iokaio/munarium-gate/actions/runs/37718888960) and
[DCO](https://github.com/iokaio/munarium-gate/actions/runs/37718888995) passed.
Warden's exact-head
[Rust/native-service workflow](https://github.com/iokaio/munarium-warden/actions/runs/37718895132),
[hygiene](https://github.com/iokaio/munarium-warden/actions/runs/37718895142) and
[DCO](https://github.com/iokaio/munarium-warden/actions/runs/37718895084) also passed.

Environment intake observed the cached PostgreSQL image
`postgres@sha256:65b16a8b326e0cfbdf33fa7e783f2a0cb352a61448616ccccfd616ef42aa0f65`,
a task-owned loopback-only container limited to 384 MiB/one CPU, synthetic credentials
and a disposable database. The maintainer's local test session owns these resources;
availability was checked before launch, no paid resources were used, and expiry is
task teardown. The verified task container was stopped and automatically removed
with its anonymous test volume after local verification. Temporary native-service
keys/databases were cleaned by each test.

These two tasks await review. Complete activation is still unavailable without
Server's independent participant implementation; Gate refuses missing receipts.
Neither service enables action execution. Local phase outboxes still require
acknowledged Server delivery. Actual REF-18 effects, snapshot quarantine,
PostgreSQL action reservations, grants/custody, final-send admission, Linux isolation
and the remaining Harness/reference evidence are outstanding.

## Server and composition review pair, 7 October 2026

The maintainer reported the participant pair and hub update merged and directed
continuation. Verified merge inputs are hub PR 17 at
`8a4afbf2a2f8b6ae87f35179771143844ece823f`, Gate PR 3 at
`bc429ebcce47579419d88daa6a6aee644fd34221`, and Warden PR 4 at
`ef08b587b259600864e3b4f48935e44fa00b7134`. Council and Registry remain at the
merged revisions recorded above. The previous paragraphs retain their historical
review-time limitations; this section records the next bounded pair.

| Component | Review input | Implemented boundary |
|---|---|---|
| Server | [PR 77](https://github.com/iokaio/munarium/pull/77), `059ee3f3305e17d96581822827f182ce927db615` | Governed REST/gRPC participant, immutable initial enrollment, atomic receipt/epoch/archive/audit event in the protected ledger |
| Harness | [PR 3](https://github.com/iokaio/munarium-harness/pull/3), `11140d9fb6dc6f264331feaedc0deb8544a1b742` | Actual five-service activation, six post-commit response losses and participant/coordinator restarts, pinned Linux CI and source/binary evidence runner |

Server's current signed coordinator binding, independently fetched Council
ratification, Gate pause/head and Registry receipt/head precede application.
Its external root authority fence is reacquired after callbacks and held through
the atomic expected-head ledger batch. An ordinary audit append cannot install
an epoch. Its internal archive provenance identifies the actual coordinator and
root revision; no Council principal is fabricated. Candidate bytes and golden
vectors remain unchanged. The amendment to ADR 0014 preceded implementation.

Local Server evidence: required runner/catalog/equivalence/format entry point
passed (23 runner and 14 catalog regressions); affected-package warnings-denied
Clippy passed; core/memory action tests passed (6), explicit PostgreSQL tests
passed (2), platform API and documentation tests passed (6 each). The exact CI
live authority/actions command passed (8), including REST/gRPC, changed root
authority during callbacks, denied dependency evidence and process restart.
Python API tests passed (6), as did Ruff, formatting, mypy, API generation drift,
licence, compatibility, private-material, documentation and whitespace checks.
Local full Server gate ladder and .NET/Java suites were not claimed; hosted CI
remains required. Local gitleaks was unavailable.

Harness's local five-service scenario passed with separate disposable Server and
Gate PostgreSQL databases. Warden issued the candidate admission assertion,
Registry verified a signed candidate, and a separately enrolled human ratified
Council's transition. The test discarded one successful response after each
owner's durable pause/apply/resume phase and restarted that owner and Council.
Incomplete progress stayed paused; retry recovered matching receipts and heads
for all four participants. Gate still reported execution unavailable after resume.
The runner retained local attempts with source inventory, binary/image and log
hashes. Existing Harness Python tests passed (7); hygiene/link checks passed.

The advisory second pass reviewed authority, callback lock order, transaction
races, retry immutability, actual fault placement, cleanup and evidence limits.
It added competing-transition tests on memory/PostgreSQL. Initial test expectation
errors were corrected. Actual composition exposed HTTP/2 negotiation against
HTTP/1.1 participant adapters; Server now explicitly uses HTTP/1.1 for those
calls, preserving native gRPC. The final pass regenerated the gRPC reference
through its owning tool to correct operation ordering. No assertion, evaluator limit or CI requirement
was weakened. This review is not an independent human acceptance disposition.

Environment availability was observed before the run: the existing host, cached
pgvector image `sha256:9b05db12a35460fff0587e009f9326e414a53e9484555547f96d214a2ba98ef7`,
loopback-only owned container, 2 CPU/768 MiB ceiling, synthetic credentials and
expiry at task teardown. The maintainer's local test session owns it; no paid
resources were used. Temporary keys, configuration and service processes were
removed/stopped by the test. The verified owned container and anonymous volume
were removed after local verification. Hosted CI uses its pinned public pgvector image and
independent disposable databases. Local Windows results do not establish Linux
qualification. Exact-head hosted results are recorded below when observed.

These two implementation tasks await review; merge Server before the Harness
dependency. This closes the missing-participant implementation and provides real
barrier recovery evidence, not the complete C2-A or Stage 2 acceptance packet.
Registry/Gate/Warden outbox delivery, withdrawal integration, Gate action
reservations, Warden grants/custody, controlled target effects, snapshot recovery,
agent isolation and final installation/investigation evidence remain open.
The next bounded work after this review is acknowledged owner outbox delivery
and Gate's durable action journal, before enabling any controlled execution.

Harness's final reviewed head `11140d9` passed the hosted Linux
[five-service activation job](https://github.com/iokaio/munarium-harness/actions/runs/37723974798),
[Rust/Python suite](https://github.com/iokaio/munarium-harness/actions/runs/37723974773),
[hygiene](https://github.com/iokaio/munarium-harness/actions/runs/37723974770) and
[DCO](https://github.com/iokaio/munarium-harness/actions/runs/37723974710).
The composition artifact confirms the final Server pin `059ee3f` and retains the
actual checkout/source/binary/image identities and sanitized test log. Its earlier
run also passed before the documentation-only Server pin update; final evidence
uses the links above. This supplies Linux activation evidence, with the stated
execution, outbox, restore and isolation limits intact.

Server's final reviewed head `059ee3f` passed the complete
[Server workflow](https://github.com/iokaio/munarium/actions/runs/37723823625),
including platform authority, PostgreSQL/workspace tests, DiskANN, black-box
conformance and generated-document drift. Its
[four-language clients and conformance](https://github.com/iokaio/munarium/actions/runs/37723823505),
[hygiene](https://github.com/iokaio/munarium/actions/runs/37723823508) and
[DCO](https://github.com/iokaio/munarium/actions/runs/37723823609) also passed.
All reported checks were successful on this final head. The superseded Server
run was cancelled after the generated-reference correction; no passing result
is inferred from that incomplete run.
