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
