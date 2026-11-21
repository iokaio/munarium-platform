# ADR 0022: safe build-job failure messages and stable codes

**Accepted (20 November 2026).** This records the shared semantics of Server v1.5
"ClearView" decision C2. The maintainer accepted it as written; see
[Disposition](#disposition-20-november-2026). Acceptance does not publish a contract
version, advance a catalog state or set a release label. The accountable owner is the
founder under [governance](../../GOVERNANCE.md).

Normative source: the Server design at
`ef32276d593c190b5a25234a85604564769d0e60` (Server `feat/clearview`), sections
[R5 and C2](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#c2)
with acceptance case
[C2-T1](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#c2-t1),
and the build-job state finding in the
[design review](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/design-review.md).

## Context

In v1.4 the builder stores an error's string form in `index_build_jobs.error` and
returns it unchanged in `IndexBuildJobDto.error`. For a storage error that string is
the database driver's message, which carries table, column and constraint names;
Server already withholds such text from per-item ingest results. Clients have no
stable machine-readable failure code. The DTO is served on REST, carried to the four
Server SDKs and shown in the console, so its fields and their meaning are shared.

## Decision

1. The existing `error` field carries a safe, human-readable message.
2. Only a genuinely classified failure receives an `error_code`. Capture the stable
   code from the typed cause when the failure is recorded and store it in a nullable
   field.
3. For a historical failed row containing only diagnostic text, return a generic
   build-failure message in `error` and **omit the `error_code` member entirely**. The
   same rule applies to a free-text failure written by a v1.4 worker during rollout.
4. Leave historical rows intact. The read path never infers a code by parsing an old
   message.
5. A successful job keeps the existing omission of failure fields.
6. **Proposed first code: `attempts_exhausted`.** An expired final claim moves the
   job to `failed` with a safe message and this code. Each code is listed in the Server
   error registry, and typed mappings are checked against it.

## Open choices

| Choice | State in the Server design |
|---|---|
| Code vocabulary beyond `attempts_exhausted` | Each classified case receives "the documented code"; no further codes are named |
| Code syntax and length | Not specified for Server. The compared system restricts codes to at most 128 characters of `[a-z0-9_]`; the design cites this as an observation, not a Server rule |
| Typed gRPC carrier | The design names the REST DTO and error registry only |

## Disposition (20 November 2026)

**Accepted by the maintainer on 20 November 2026, as written**, reviewing hub
revision `dc3aa258b0bde8b82a1ad676a4727204264997db` (`dc3aa25`, this record as
drafted). The Server implementation ledger records the acceptance as
[maintainer decision 5](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/design/implementation-ledger.md#maintainer-decisions-20-november-2026)
at Server `89e1bc2019c80d697d2d8adc9237a9ce577cf3d7`. This disposition changes the
record's state only. It publishes no contract version, composition manifest or
release label, advances no catalog state or invariant evidence field, and activates
nothing.

The open choices are resolved as the Server implemented them on `feat/clearview`
(Server `d0a789acb67638c22d6ca097fcc77238dbd727d0`, additive migration 0047, ledger
row R5 · C2, and the Server [error registry](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/api/errors.md#build-job-failure-codes)):

| Choice | Resolution |
|---|---|
| Code vocabulary beyond `attempts_exhausted` | Six codes, each captured from the failure's typed cause when recorded and each with a fixed safe `error` message: `attempts_exhausted`, `invalid_input`, `not_found`, `storage_error`, `datastore_unavailable` and `provider_error`. Any other cause is unclassified: a generic message and no `error_code`. Codes are registered in the error registry and checked against it by the Server's documentation coverage test. |
| Code syntax and length | Lowercase snake case of at most 64 characters, `^[a-z][a-z0-9_]{0,63}$`, enforced on write by a database CHECK. |
| Typed gRPC carrier | None added. gRPC callers receive `error_code` through the native bridge's JSON; no typed RPC carries it. |

Maintainer decisions of 20 November 2026 that bear on this record:

- **Decision 6.** The C2 wire field is accepted as release ready. The hub contract
  export named in the version policy remains a separate step; this disposition does
  not perform it.
- **Decision 7.** R4 expired-claim cleanup, which records `attempts_exhausted`, is
  on by default, and a drained final claim counts as a claim (SCALE-2). The code's
  meaning is unchanged.
- **Decision 1.** Binary rollback across v1.5 migrations, including 0047, is by
  backup restore. The historical-row rule (item 4) is unchanged: rows are not
  rewritten in place.

## Amendment (21 November 2026)

The maintainer approved a classified failure for isolated PDF extraction under
`MUNARIUM_PDF_EXTRACTION_DEFERRED=fail`. A queued build emits
`extraction_deferred` with the fixed display message in the Server registry.
A direct failure uses `extraction-deferred`, HTTP 429 and gRPC
`RESOURCE_EXHAUSTED`, with `retryable: false` and `retry_action: retry_later`.
The default skip behavior and historical omission rules still apply.
The current registry also includes `artifact_blocked` from the 20 November
artifact publication decision. Both are additive codes of the existing field.
Clients keep reading it as a string.
[Maintainer decisions and implementation](https://github.com/iokaio/munarium/blob/67e368d88cd3275acdb71d91635cc40f336de718/server/docs/design/implementation-ledger.md#maintainer-decisions-21-november-2026)
· [Current error registry](https://github.com/iokaio/munarium/blob/67e368d88cd3275acdb71d91635cc40f336de718/server/docs/api/errors.md#build-job-failure-codes)

The [ClearView candidate](clearview-c2-mcp-v1/README.md) captures the current
registry and failure-member omission vectors for contract review.

## Alternatives

- **Return the raw error chain (v1.4).** Rejected: it discloses storage internals.
- **Infer codes for old rows from their text.** Rejected: the read path must never
  parse old messages.
- **Rewrite historical rows.** Rejected: rows stay intact.
- **Serialize an absent code as `null`.** Not adopted: the member is omitted.

## Evidence

Partial experimental implementation at drafting. The implementation since and the
acceptance are in the [disposition](#disposition-20-november-2026); no release
receipt is claimed.
Server `3c0d7c7850a83bc9f3ac91f43dc9c27b1786731e` (R4 first slice) fails expired
final claims with a fixed safe message, `ATTEMPTS_EXHAUSTED_MESSAGE` in
`munarium-store-pg/src/jobs.rs`, whose documentation states that the machine-readable
code waits for this hub record and is neither stored nor returned yet. The
[implementation ledger](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/implementation-ledger.md)
records R5 · C2 as planned, with v1.4 fixtures for historical storage-text and
free-text failures and their exact v1.4 DTOs.

## Owners and affected consumers

| Owner | Responsibility |
|---|---|
| Founder | Accountable design owner and acceptance authority |
| Server job-store and API maintainers | Classification at record time, nullable storage, DTO and error registry |

Affected consumers: the four Server SDK families, the console's build views and
attention strip, operator scripts reading `error`, and v1.4 workers during rollout.

## Version policy

Additive: a new optional member and a new nullable column. Existing `error` remains
present with changed, safer text, which the design requires to be documented as a
displayed-text change. Migrations are additive. The exact field and code registry
are exported through the owning contract process before Server returns the code.
This record adds no hub schema or vector.

## Consequences

- Clients can branch on stable codes for classified failures without parsing text.
- Historical and rollout-era failures read as generic failures without a code; this
  is deliberate loss of precision rather than a guessed classification.
- Displayed `error` text changes for storage failures; scripts matching that text
  must move to `error_code` where one exists.
