# Stage 2 implementation direction and bounded packets

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
