# Stage 1 acceptance review packet

**Prepared 7 October 2026; human disposition pending.** The maintainer approved
preparing Stage 1 closeout, reconciling the plans and investigating HUB-03 and
Server S7/S9. That direction authorizes this preparation; it is not acceptance of
an unidentified contract revision. This packet makes the review inputs explicit.
It does not activate candidates, publish a release or advance catalog labels.

## Immutable inputs

[Machine-readable review inputs](stage1-review-inputs.json) pin full source and
Git tree IDs, candidate bundle/file digests and the evaluator. They describe
review inputs, not a tested binary distribution or released composition.

| Repository | Source revision |
|---|---|
| Hub | `f122011b713c892249738c9835c90a2d81a9505a` |
| Server and SDKs | `7cc0c97fe124d446064bb8cf0dfcb6d868d04987` |
| Warden | `7aabbf4a5336cbf29ee7ef26f3baf8a7078770fb` |
| Registry | `4ab7f4b3a9f77d16e74e44611de4a526e8c75eb9` |
| Gate | `5f8957e25cff0398f8cda7359e6397e840232835` |
| Harness | `926624e0cb4e1d5af1996308cfaed108204a3854` |

Server's final 6 October branch commit `b046ff0` and its 7 October squash
`7cc0c97` have identical trees. Pin the latter for review. The hub revision above
is the implemented Stage 1 baseline; this closeout packet is a subsequent change.

The foundation, Warden admission and Registry v2 candidate lock hashes were
checked against their committed files. Server, Gate and Harness Stage 1 vendor
files match the hub sources, and Registry v2 matches its hub candidate, after LF
normalization. Those checks establish byte agreement, not contract acceptance.
Runtime worker hashing uses actual file bytes; checkout line-ending conversion
must be reflected in a run's worker digest, not confused with the review hash.

## Decisions requiring a human disposition

Review the following at the pinned hub revision, with the existing schemas and
negative vectors. Record accept, revise or defer, reviewer, date and exact
revision; do not mark a row accepted because implementation or merging succeeded.

| Decision group | Concrete choice under review | Evidence and limitation |
|---|---|---|
| DEC-01; ADR 0003/0005/0008 | Non-agent bootstrap, irreversible retirement, recipient-bound identity and registered attenuation | Authority/identity tests; one Server replica and external checkpoint custody |
| DEC-02; ADR 0004/0006 | Restricted canonical JSON, exact signed manifest identity, inert candidates | Independent client vectors and Registry admission; no activation protocol yet |
| DEC-03; ADR 0007 | OPA 1.21.1 Windows amd64, pinned worker/capabilities, 100 ms/64 MiB boundary | Native controls and replay; no Linux or production sandbox claim |
| Minimum DEC-07; ADR 0008 | Direct mTLS, enrolled peer fingerprints and provider mappings, current per-recipient authority | Actual service tests; not network/credential isolation qualification |
| Minimum DEC-08; ADR 0004/0007/0009 | Proposal/decision/refusal records, exact acknowledgements, immutable archives and authenticated recovery | Memory/PostgreSQL checks; no Stage 2 action-event protocol |

Use the [decision index](../decisions/README.md) for those records and the
[implementation record](stage1-implementation.md) for the historical test results.
The candidate manifests remain inactive and every service outcome remains
decision-only under this review scope.

The [platform-wide second pass](platform-contract-review.md) recommends retaining
this bounded scope. A Stage 1 disposition does not freeze its principal/request,
epoch or three-kind event model as the final platform-wide contract. New action
contracts need the typed identities/context, event families and compatibility
boundaries proposed in [ADR 0011](../decisions/0011-platform-contract-evolution.md).
These are new-version requirements; the pinned review inputs above stay unchanged.

## Completion requirements and evidence map

| Required outcome | Evidence owner / executable source | Current disposition |
|---|---|---|
| Canonical bytes, digest and typed outcome agreement | Harness Rust/Python decision tests and unchanged hub vectors | Local results recorded on 6 October; component CI successful |
| Candidate validation, current identity, tenant/manifest refusal | Registry `tests/reg_01.rs`, `tests/identity.rs`; Warden admission/principal tests | Local results recorded; component CI successful |
| REF-01 replay and Stage 1 lineage/refusal cases | Harness `tests/composition/scenario.rs`, `tests/network/test_services.py` | 13 library case groups and memory/PostgreSQL services recorded locally; not REF-02–20 |
| S1 authority and REST/gRPC parity | Server `platform_api_tests.rs`, store authority tests and Python live authority tests | Local record plus successful exact-revision `platform-authority` CI job |
| Lost acknowledgement and restart recovery | Harness network test drops an archive acknowledgement, restarts Gate without evaluator | Memory profile rerun passed on 7 October from clean source snapshots; full service CI run not found for pinned Harness SHA |
| Reproducible installation and retained run | Harness service/library runners and component service guides | Clean-snapshot memory run recorded below; independent clean build/released binary provenance still open |
| Human contract disposition / independent review | This packet and exact candidate revisions | Pending; neither supplied by component CI |

Source paths above are in the repositories pinned in the input file. The
[Harness service guide](https://github.com/iokaio/munarium-harness/blob/926624e0cb4e1d5af1996308cfaed108204a3854/docs/service-profile.md)
documents both actual service profiles and the separate 13-group library suite.

## GitHub observations on 7 October

Read-only workflow-run queries filtered by each exact SHA returned the following
completed successful push runs. These observations apply to those commits only.

| Repository | Exact-revision successful runs |
|---|---|
| Server | [server-ci](https://github.com/iokaio/munarium/actions/runs/37579141853), [clients-ci](https://github.com/iokaio/munarium/actions/runs/37579141733), [hygiene](https://github.com/iokaio/munarium/actions/runs/37579141655) |
| Hub | [hygiene](https://github.com/iokaio/munarium-platform/actions/runs/37575898644) |
| Warden | [Rust](https://github.com/iokaio/munarium-warden/actions/runs/37576122303), [hygiene](https://github.com/iokaio/munarium-warden/actions/runs/37576122201) |
| Registry | [Rust](https://github.com/iokaio/munarium-registry/actions/runs/37576266523), [hygiene](https://github.com/iokaio/munarium-registry/actions/runs/37576266520) |
| Gate | [Rust/evaluator](https://github.com/iokaio/munarium-gate/actions/runs/37576436621), [hygiene](https://github.com/iokaio/munarium-gate/actions/runs/37576436589) |
| Harness | [Rust](https://github.com/iokaio/munarium-harness/actions/runs/37576602496), [hygiene](https://github.com/iokaio/munarium-harness/actions/runs/37576602550) |

Job-level inspection confirmed Server's `platform-authority` job and Gate's
`Bounded Windows evaluator controls` job completed successfully. No Stage 1
service-composition run appeared for the pinned Harness SHA. Its workflow is
manually dispatched and covers the memory service profile; its existence is not
a run result. No workflow was dispatched for this observation. Initial check-run
API requests failed; the workflow-run and selected job queries above succeeded.

## Additional local verification on 7 October

All four service binaries were rebuilt from the pinned local sources with
`cargo build --offline --locked`, using Cargo/rustc 1.98.1. Each command exited 0.
Six disposable local clones were then detached at the pinned commits; their
tracked/untracked status was clean before the service runner. Rebuilt executables
and the pinned public OPA executable were copied into their ignored build
directories. This tests clean source snapshots with locally rebuilt binaries;
it is not an independent clean-room build or a released artifact provenance claim.

From the disposable Harness checkout, with `PYTHONPATH` pointing at the pinned
Server SDK source and the existing SDK test interpreter meeting its dependency
requirements:

```console
python scripts/run_services.py --workspace CLEAN_SNAPSHOT_PARENT --opa PINNED_OPA --database memory --output NEW_LOCAL_RECEIPT
```

| Attempt | Observed outcome |
|---|---|
| 1 | Setup failed before service startup: local-clone origin metadata did not match the runner's public-origin preflight. Corrected only the disposable clones' origin metadata. |
| 2 | Exit 1; one failed, one deselected. The ambient Python protobuf runtime was older than the committed generated-code floor. No assertion or SDK requirement was changed. |
| 3 | Exit 0; one memory integration case passed, one PostgreSQL case deselected, in 58.84 seconds. Used the existing SDK test environment. The case includes multiple service/refusal/recovery assertions; this is not 13 independently executed cases. |

Separate receipts are retained locally under Harness's ignored
`target/stage1-runs/2026-10-07-closeout-memory-attempt{1,2,3}.json`; attempt 1 is
an explicit setup receipt because the runner failed before creating its own.
Those paths are local retention references, not public downloadable evidence.
The failed attempts remain failed. PostgreSQL was not rerun; its 6 October
observation and exact-commit component CI remain separate evidence.

The fixture stopped its owned services and removed temporary test keys/configs.
After process inspection confirmed no task-owned service/evaluator remained,
only the verified disposable snapshot directory was removed. Run receipts and
reusable build caches remain local. No target credentials, effects or paid
resources were used. The separate [foundation assessment](stage2-foundation-assessment.md)
also records four passing memory-store tests.

## Remaining gates and retained limitations

- **AC-01 / maintainer:** supply the exact-revision contract dispositions above.
- **AC-02 / Harness:** the clean-snapshot memory receipt above is available
  locally. Complete the reviewable immutable composition inputs and artifact
  provenance, selected installation profiles, per-case evidence/omissions and
  retention boundary before qualification. Preserve all prior attempts.
- **AC-03 / review owner:** identify independent review scope and availability;
  no independent reviewer or production qualification is claimed here.
- **AC-04 / foundation owners:** retain the failed/unavailable FOUNDATION-01
  checks and original Matrix provenance gap. New successful component CI does
  not rewrite those historical receipts or qualify omitted profiles.

The [6 October record](stage1-implementation.md) retains 55 pre-existing hub
filesystem scanner findings in unrelated nested worktrees. A clean preparation
worktree can pass its own scan without resolving those findings. Preserve both
observations. Single-process SQLite custody, Windows evaluator support and the
external checkpoint's restore limits remain part of the experimental boundary.

The next design packet is [Stage 2 preparation](../stage2-preparation.md).
Closing Stage 1 does not authorize target effects; Stage 2 requires its own
accepted action contracts, bounded implementation authorization and evidence.
