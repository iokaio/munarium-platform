# FOUNDATION-01: source qualification observations

**Review record, 6 October 2026; incomplete platform qualification.** This records actual
local checks of unchanged public source. It is not a released qualification report,
accepted hub contract, tested composition or advancement of a catalog/invariant status.
The [baseline](foundation-baseline.md) and [requirements](foundation-requirements.md)
remain the requirements inputs. Matrix is already separate; no extraction was performed.

## Immutable inputs and environment

| Input | Revision / boundary |
|---|---|
| [Server](https://github.com/iokaio/munarium/tree/2c40480fdc2378e66dc23acdfaf82b529b9d22ee) | `2c40480fdc2378e66dc23acdfaf82b529b9d22ee`, fetched main, clean before/after; source version 1.3.0 |
| [Matrix](https://github.com/iokaio/munarium-matrix/tree/643863fcb4433c8236f3ab22ca812f17c354f34c) | `643863fcb4433c8236f3ab22ca812f17c354f34c`, fetched main, clean before/after; source version 1.2.0 |
| [Hub input](https://github.com/iokaio/munarium-platform/tree/44e2e2969f5c86fa964034af2d2729dd561c1e8e) | `44e2e2969f5c86fa964034af2d2729dd561c1e8e`; this report prepared in an isolated worktree; pre-existing planning edits preserved |
| Fixture | `pgvector/pgvector:pg16@sha256:ccc6e83d6e35e931dc7c5def2022729d5a6c370318d099181995567ff1fb4d6b`; disposable uniquely named PostgreSQL containers, loopback ports and test-only credentials |
| Host | Windows; PowerShell 7.6.6, Python 3.13.7, Docker 29.8.0; same host, two parallel analysis/test lanes, not independent machines or reviewers |
| Toolchains | Server rustc/cargo 1.98.0; Matrix rustc/cargo 1.98.1; Matrix SDK checks: .NET 10.0.204, Temurin Java 21.0.12.1, Gradle wrapper 9.7.1 |

Repository Cargo lockfiles, test sources and conformance fixtures are pinned by the source
revisions above. Rust and the Python launcher required process-local PATH additions.
No paid service, model provider or customer fixture was used. Containers created by these
runs were removed and their absence verified. Downloaded images and one uniquely named
Matrix test-image tag remain reusable local cache. No unrelated resources were removed.

`gh release list` found Server v1.3.0 (published 26 September 2026), but no Matrix GitHub
releases; no tag pointed to either inspected HEAD. Source package versions are not artifact
digests. No container/package signature or release authenticity was qualified here.

## Server commands and observed results

Commands below run from `server/` unless labelled root. Exit codes refer to the command,
not a later successful shell command. The source implementation was not edited.

| Command | Observed outcome |
|---|---|
| `./gates.ps1` | **Exit 1, failed.** Catalog-backed steps reported `powershell_exception`; PostgreSQL setup reported `missing_image`; dependent checks did not run. Build, OpenAPI, gRPC docs, notices and embedded formatting passed. This receipt is not a green gate. |
| `cargo fmt --all --check` | Exit 0 |
| `python tools/gate_catalog.py runner.regression catalog.regression catalog.equivalence contract.mmp contract.matrix boundaries.crates boundaries.datastore boundaries.retrieval migrations.additive` | Exit 0; 23 runner tests and 14 catalog tests; inventory equivalence, MMP publisher self-test, Matrix publisher/vendor check and boundaries passed |
| `cargo test -p munarium-core -p munarium-access -p munarium-api-types -- --nocapture` | Exit 0; 104 tests passed, zero failed/ignored (9 access, 81 core, 4 money, 2 API JSON, 5 Matrix contract, 3 wire compatibility) |
| `./test.ps1 -All` | **Exit 1, failed.** Still reported missing image and catalog exception; build and memory-backed black-box REST/gRPC conformance passed (9 each). PostgreSQL/platform/cluster dependencies did not run. |
| `cargo test -p munarium-server -- --nocapture` with isolated PostgreSQL | Exit 0; 272 tests discovered. Includes PostgreSQL governance, guarded-command recovery and authority tests; ignored child fixtures and environment-dependent skips are not qualified coverage. |
| `cargo run -p mmp-conformance -- --postgres <isolated-fixture-url>` | Exit 0; 8 passed, zero failed |
| `cargo run -p mmp-conformance -- --in-process` | Exit 0; 8 passed, zero failed |
| Root: `python check_license.py`, `python clients/check_compatibility.py`, `python scripts/docs_linkcheck.py`, `python scripts/private_material_scan.py`, `git diff --check` | Each exit 0; compatibility metadata for 4 clients, 28 indexed Markdown files; no scanner finding |

The immutable image pull succeeded, but the runners' repository-name image enumeration
missed a digest-only image without a tag. Server's direct PostgreSQL run used the exact
digest and bypassed only the image-discovery wrapper, not a test assertion. Matrix separately
added a new test-only tag for the same image and reran its documented runner successfully.
The original unsuccessful runs remain unsuccessful; neither workaround changes their result.

The Server catalog's PowerShell exception remains an unresolved runner finding. Its direct
Python invocation passed, but that does not cover every failed gate step. Full workspace,
feature matrices, embedded consumer/MSRV matrix, dependency audit, full platform/cluster
tiers, deployment checks and Server SDK runtime suites remain unqualified in this record.
No hosted CI run was dispatched or claimed passed. A subsequent runner repair needs its
own regression test and a fresh complete receipt.

## Matrix commands and observed results

Commands run from Matrix root except SDK commands, which run from their own directories.

| Command | Observed outcome |
|---|---|
| `pwsh -NoProfile -File ./test.ps1 -Gates -Postgres -ReceiptPath <new-local-receipt>` | Initial receipt exit **3**, incomplete: PostgreSQL image unavailable; all 12 offline/gate steps passed; source unchanged |
| `cargo fmt --all -- --check`; `cargo clippy --workspace --all-targets -- -D warnings` | Both passed in gate receipt |
| `cargo test --workspace -- --nocapture` | Harness: 372 passed, 49 ignored, zero failed; early-return limitation below |
| `python scripts/boundaries.py` | Passed: 250 shipping crates, pure core, no Server crate edge, rustls-only, additive migrations and four core adapters |
| `python contract/validate_examples.py`; `python contract/publish.py --self-test` | Passed: 8 examples; two identical cuts, 17 locked files |
| `python contract/publish.py --check ../munarium/server/contract/matrix`; `--verify ../munarium/server/contract/matrix` | Both exit 0; bytes agree; check ignores source-commit field |
| `python check_license.py`; `python scripts/third_party_notices.py --check --cargo-target x86_64-unknown-linux-musl`; `python scripts/doclint.py` | Passed: 154 headed source files, 279 notice components, 210 links with none dead |
| `python -m unittest discover -s tools -p test_validation.py` with Cargo on PATH | Exit 0, 4 passed; prior direct invocation without Cargo ran 3 and skipped 1 |
| `cargo run -q -p munarium-matrix-server --bin munarium-matrix -- openapi --check docs/api/openapi.json` | Passed |
| `python clients/check_compatibility.py`; `python clients/check_license.py`; `python scripts/private_material_scan.py`; `git diff --check` | Passed; three client metadata records; private scanner inspected 371 files |
| Python client: `python -m pytest tests -q -rs` with process-local SDK source path | Exit 0, 19 passed / 1 live test skipped |
| .NET client: `dotnet build -warnaserror`; `dotnet test tests/Ioka.Munarium.Matrix.Client.Tests --no-build -v normal` | Both exit 0, no build warnings/errors; 18 passed / 1 live test skipped |
| Java client: `./gradlew.bat build --no-daemon` | Exit 0, 23 passed / 1 live test skipped |
| `pwsh -NoProfile -File ./test.ps1 -Postgres -ReceiptPath <second-local-receipt>` after digest pull | Exit **3**, same missing-image discovery limitation |
| Same `-Postgres` command with a new receipt after adding a distinct test-only image tag | **Exit 0**, selected profile passed, source unchanged; PostgreSQL 9 passed and CDC/watermark 9 passed, zero ignored; owned container cleaned up |

The workspace count is a harness report, not a count of qualified integration behaviors.
In particular, 11 tests in
[live_server.rs](https://github.com/iokaio/munarium-matrix/blob/643863fcb4433c8236f3ab22ca812f17c354f34c/src/munarium-matrix-workers/tests/live_server.rs)
return early without a configured Server peer. They did not exercise live compatibility.
Do not subtract only those eleven and treat every other harness pass as independently
qualified. Complete Server/Matrix/SQL Server/gRPC/admin integration, live SDK round trips,
MySQL, browser, image-size/build and performance tiers were not run. `cargo deny` and
`gitleaks` were unavailable. The owning
[live contract workflow](https://github.com/iokaio/munarium-matrix/blob/643863fcb4433c8236f3ab22ca812f17c354f34c/.github/workflows/matrix-server-contract.yml)
remains independent coverage, not replaced by this record.

## Contract provenance

Both sources agree with vendored Matrix wire contract `0.1.0`, bundle digest
`2f35a515db4501a0320f51335e3d212796f757f06af6f309f8b3f639305ced96`.
The Server [lock](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/contract/matrix/contract.lock)
still says `source_commit: unknown`. Publisher self-test, lock verification and byte
agreement do not reconstruct original publisher provenance. This remains an unresolved
composition-input gap. No vendored file was hand-edited, re-cut or released.

## S1–S9 source, tests and remaining work

Status describes the **platform requirement**, separately from existing component tests.
All Server links below are pinned to the inspected source revision.

| ID / status | Existing source and test evidence | Remaining acceptance boundary |
|---|---|---|
| S1 / partial | [Governance metadata](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-core/src/governance.rs) binds revision and expected parent head; [memory/PostgreSQL policy tests](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-server/src/governance_policy_tests.rs) ran in the Server suite | Separate platform governance authority, non-agent bootstrap attestation and durable retirement are not established by those tests. DEC-01 acceptance and a transport/persistence refusal gate are required. |
| S2 / partial | [Ledger types](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-core/src/types.rs) and [command recovery](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-server/src/command_recovery.rs); memory/PostgreSQL conformance passed | No accepted platform proposal/decision/claim/grant/dispatch/outcome schemas or acknowledgement contract. Existing command receipts are not that contract. |
| S3 / partial | [Capability verification](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-access/src/lib.rs), 9 access tests; [REST/gRPC authority tests](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-server/src/authority_tests.rs) in Server suite | Platform issuer/audience, service-origin and attenuated delegation verification absent from the existing principal model; do not reinterpret static UID assertions as verified chains. |
| S4 / partial | [ClaimOrigin](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-core/src/types.rs), [evidence](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-core/src/evidence.rs) and source hashes; origin round-trip conformance passed | Origin explicitly remains provenance, not an acceptance input. Accepted trust/field/derivation bindings and unknown-lineage refusal still required. |
| S5 / absent in inspected paths; not run | [Ledger/storage interfaces](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-core/src/storage.rs) supply sequence/pin semantics | Runbook checkpoints are not signed ledger ranges. No signed-checkpoint/witness qualification or signer custody evidence. |
| S6 / partial | [Main tracing setup](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-server/src/main.rs) and existing ledger events | No accepted platform event convention, gap/export protocol or telemetry-loss test; Stage 1 event shape is prerequisite. |
| S7 / not run | [Listener configuration](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-server/src/main.rs); memory black-box transport checks passed | These checks do not prove authenticated service topology, proxy identity or denied network/credential edges. |
| S8 / partial, extraction not attempted | [Provider accounting](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-core/src/provider.rs), money tests and `munarium-providers` owner | Preserve the existing lineage before any Gateway extraction; no live provider/model accounting qualification in this run. |
| S9 / partial | [Guarded recovery tests](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-server/src/command_recovery_tests.rs) ran against PostgreSQL; source has durable claim/conflict/unresolved/replay behavior | No accepted Gate/Warden consumption/fencing/revocation or restore-quarantine contract/library; current command semantics do not prove exactly-once external effects. |

Matrix's [caller model](https://github.com/iokaio/munarium-matrix/blob/643863fcb4433c8236f3ab22ca812f17c354f34c/src/munarium-matrix-server/src/state.rs)
has tenant/role/static authentication, not platform principal chains. Its
[manifest](https://github.com/iokaio/munarium-matrix/blob/643863fcb4433c8236f3ab22ca812f17c354f34c/src/munarium-matrix-types/src/contract.rs)
already records both hashes, identity/completeness, redaction, snapshots and authorization;
optional textual `effective_principal` is not verified origin. Preserve the public
[adapter SPI](https://github.com/iokaio/munarium-matrix/blob/643863fcb4433c8236f3ab22ca812f17c354f34c/src/munarium-matrix-adapter/src/lib.rs).
Prepare principal rejection, tenant/delegation, unknown-lineage and request-binding cases
at these owning seams after definitions are accepted. Matrix promotion tests are not S1.

## Retained observations and next gates

The tables preserve command outcomes, including failures and unavailable coverage. Local
runner receipts retain command arrays, tool/source hashes, output references and cleanup;
they stay in each foundation's ignored validation directory and are **not copied here**.
The additional direct Server runs are retained in this task's execution transcript, with
these public terminal summaries: `104 passed` across the listed focused binaries;
Server-suite exit 0; PostgreSQL and in-process conformance each `8 passed, 0 failed`;
REST and gRPC each `9 passed, 0 failed`; owned-fixture cleanup exit 0. These summaries are
not a portable independently verifiable evidence bundle. That stronger export remains open.

FOUNDATION-01 supplies source-backed input to HUB-01/02, not acceptance of their decisions.
Close runner coverage and provenance/export gaps before a complete foundation qualification
claim. Review DEC-01 before opening S1 runtime implementation; review DEC-02/03 and minimum
DEC-07/08 before S2–S4. Server runtime remains unchanged pending those accepted definitions.
No S1 authority gate, first integrated slice or release has been declared complete.
