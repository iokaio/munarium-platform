# ADR 0020: Matrix ownership transfer and the Server consumer record

**Accepted (20 November 2026).** This records the shared semantics of Server v1.5
"ClearView" decision M1. The maintainer accepted it as written; see
[Disposition](#disposition-20-november-2026). Acceptance does not publish a contract
version, advance a catalog state or set a release label. The accountable owner is
the founder under [governance](../../GOVERNANCE.md).

Normative source: the Server design at
`ef32276d593c190b5a25234a85604564769d0e60` (Server `feat/clearview`), sections
[M1](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/repository-handoffs.md#m1),
[transfer order and rollback](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/repository-handoffs.md#transfer-order-and-rollback)
and the [M1 switch receipts](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/matrix-switch-receipts.md).
Where this record and that text differ, the difference is a review finding to
resolve in both places, not a silent override.

## Context

Matrix has shipped its runtime, adapters, clients and `mxctl` from its own
repository since 1.2.0, and owns the structured-evidence wire schemas and golden
examples. The Server tree still compiles the Matrix contract version into its
kernel, calls the peer, exposes reports to clients and ships Matrix operator
commands in `mmctl`. Deleting paths that contain the word "matrix" would break the
build and miss the provider in a mixed-purpose source file. The split between the
Matrix publisher and the Server consumer is therefore a cross-repository contract
choice, and the Server decision register lists M1 as "Hub record pending".

## Decision

1. **Ownership.** Server owns its structured-evidence consumer, authorization,
   sealed evidence, report and bundled CLI entry point. Matrix owns the command and
   query definitions, schemas, examples, manuals and producer tests.
2. **Compatibility names stay.** Server keeps the released v1.4 compatibility
   names: the kernel's `CONTRACT_VERSION`, the REST `GET /v1/reports/matrix` and
   gRPC `MatrixReport` operations, `/admin/matrix`, stored `matrix:<dataView>`
   references, `matrix.` finding filters, the existing configuration inputs and the
   `mmctl matrix` spelling in the shipped `mmctl`.
3. **Minimal generated consumer record.** In place of the vendored contract copy,
   Server retains a generated record of the supported wire version, the reviewed
   publisher revision and the locked bundle digest, with the actually verified source
   commit recorded separately (the existing lock records `source_commit: unknown`).
   The publisher generates it; nobody edits it by hand. Its generated inputs are part
   of the Server source distribution.
4. **The `0.1.0` cut is preserved byte for byte**, including its README and
   validator, because those files are inside its digest. Revised publication guidance
   and tooling ship through an independently versioned export or a new cut.
5. **CLI descriptor boundary.** If a publisher-generated, locked data descriptor is
   adopted for compile-time values, it selects fixed methods and relative routes
   only. The operator still sets the peer base URL; CLI operands cannot select a
   different host or run a hook. It is adopted only after it is shown to reproduce the
   existing CLI error and output behavior; otherwise the forwarding shim remains until
   a bundled compatible replacement passes.
6. **Transfer order.** Inventory the exact release; make the Matrix destination
   verifiable; switch the Server consumer without changing deployment (no new Matrix
   release, extra download, process or configuration key); then remove each
   inventoried Server path only after its destination, replacement, tests and both
   owning reviewers' confirmation exist. A post-removal regression reverts the
   affected transfer and restores the last verified pin and gates.

## Open choices

| Choice | Options recorded in the Server design | Closing evidence named by Server |
|---|---|---|
| Minimal descriptor format (Server open item "M1 minimal descriptor format") | (a) The publisher's `--consumer-out` profile, which the experimental candidate uses: `format_version` 1 with a `wire_contract` pin and an `mmctl_matrix` command table, bound by a `profile_digest`. (b) Keep the forwarding shim until a bundled compatible replacement passes, recording the row as outstanding. | v1.4 CLI coverage, deterministic export, digest verification and standalone builds before deleting prior paths |
| Publisher revision to pin | The candidate pins Matrix `feat/clearview` `79aa8c573011e8095c171dc532b01f19a6ecda63`, recorded as not reviewed or merged. The design requires re-pinning to the reviewed, merged revision before source removal. | Matrix review and merge, then the coupled Server CI change |

As drafted, this record did not choose between (a) and (b). The
[disposition](#disposition-20-november-2026) records the resolution.

## Disposition (20 November 2026)

**Accepted by the maintainer on 20 November 2026, as written**, reviewing hub
revision `dc3aa258b0bde8b82a1ad676a4727204264997db` (`dc3aa25`, this record as
drafted). The Server implementation ledger records the acceptance as
[maintainer decision 5](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/design/implementation-ledger.md#maintainer-decisions-20-november-2026)
at Server `89e1bc2019c80d697d2d8adc9237a9ce577cf3d7`. This disposition changes the
record's state only. It publishes no contract version, composition manifest or
release label, advances no catalog state or invariant evidence field, and activates
nothing.

The open choices are resolved as the Server implemented them on `feat/clearview`:

| Choice | Resolution | Where recorded |
|---|---|---|
| Minimal descriptor format | Option (a) for the consumer record: the publisher's `--consumer-out` profile (`format_version` 1, `wire_contract` pin, `mmctl_matrix` command table, `profile_digest`), written with the generated `matrix_pin.rs` by `server/tools/matrix_pin.py`. The existing `mmctl matrix` dispatcher stays in place until the command table is shown to reproduce the v1.4 CLI behavior (decision item 5); until then that removal row is outstanding. | Server `8b1ff2bcd1208f6030a4a6f32c1a732e8b6ad84d`; [ledger row M1 · Step 3](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/design/implementation-ledger.md#phase-m-matrix-isolation) |
| Publisher revision to pin | Unchanged by acceptance: the candidate pin remains Matrix `feat/clearview` `79aa8c5`, recorded as not reviewed or merged. Re-pinning to the reviewed, merged revision is still required before step 4 removes any Server path. | Ledger row M1 · Step 3; [maintainer decision 4](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/design/implementation-ledger.md#maintainer-decisions-20-november-2026) |

Maintainer decisions of 20 November 2026 that bear on this record:

- **Decision 4.** Resolution of Matrix PR #4 is delayed until the work is code
  complete; work continues on `feat/clearview`. The pin therefore stays a candidate
  and step 4 (source removal) stays blocked on the reviewed, merged revision.
- **Decision 13.** The Matrix pin check is an approved CI addition. The coupled
  Server CI change (the `matrix_pin.py --check` gate with its baseline, assertions and
  negative controls) remains to be made in the Server.
- **Decision 1** (binary rollback across v1.5 migrations by backup restore) does not
  change item 6: a post-removal regression still reverts the affected source
  transfer and restores the last verified pin and gates.

## Alternatives

- **Delete by name.** Rejected by the design: it breaks the build and misses the
  provider in a mixed-purpose file.
- **Keep the compile-time read of the vendored `VERSION` file.** Replaced in the
  candidate by the generated pin; the vendored copy and its checker remain only until
  the replacement gate validates the standalone inputs.
- **Require a new Matrix release or extra runtime artifact at cutover.** Rejected:
  step 3 must change no deployment input.
- **Rewrite the `0.1.0` cut to carry new guidance.** Rejected: it would change the
  locked digest.

## Evidence

Experimental implementation, as drafted. Acceptance of this record is in the
[disposition](#disposition-20-november-2026); no release receipt is claimed.

- Server `8b1ff2bcd1208f6030a4a6f32c1a732e8b6ad84d` (M1 step 3, recorded in the
  [implementation ledger](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/implementation-ledger.md)
  as "prepared as a candidate; not final") generates the consumer export and
  `matrix_pin.rs`; `CONTRACT_VERSION` now comes from the pin. The pinned wire version
  is `0.1.0` with the same locked bundle digest as the vendored v1.4 lock.
- The [switch receipts](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/matrix-switch-receipts.md#m1-t1-results-19-november-2026)
  record local M1-T1 rehearsal results on 19 November 2026: cut reproduction,
  refusal of tampered, missing and unlisted vectors and of a wrong publisher revision,
  a standalone build and a local container build. The design labels these rehearsal
  evidence from an unreviewed candidate, not a release receipt. The offline-network
  and source-distribution repeats are open.
- M1-T2 (installed peer and clients) was not run. Step 4 (source removal) has not
  started. The Server CI change that adds the pin check is pending Matrix review.

## Owners and affected consumers

| Owner | Responsibility |
|---|---|
| Founder | Accountable design owner and acceptance authority |
| Matrix publisher maintainers | Contract source, publisher, consumer export, CLI definitions, manuals, producer tests and the `matrix-server-contract.yml` job |
| Server contract and CLI maintainers | Consumer pin, compatibility names, `mmctl` entry point, Server CI coupling and removal receipts |

Affected consumers: the Server kernel and API types, the four Server SDK families,
`mmctl` and existing operator scripts, the Helm chart's Matrix values, the console
Matrix page, stored runbooks and evidence references, and Matrix's cross-repository
CI job.

## Version policy

The Matrix contract keeps its own compatibility rule (major for a wire break,
minor for additive change, patch for examples and prose), as cited in the
[Server contract guide](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/contract/README.md).
The consumer record pins one exact cut by digest; a contract change is re-cut and
re-pinned in a coordinated change, never edited in place. This record adds no hub
schema or vector and leaves every existing hub candidate unchanged.

## Consequences

- Server can build without a sibling Matrix checkout while keeping v1.4 callers
  working; the evidence for that remains the outstanding M1 receipts.
- Removal of each Server path is blocked until its receipt passes; a missing
  receipt keeps the vendored copy and current gates.
- The Matrix CI job that sparse-checks out `server/contract/matrix` must change
  together with the Server `contract.matrix` gate at removal time.
