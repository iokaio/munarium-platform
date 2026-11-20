# ADR 0022: safe build-job failure messages and stable codes

**Proposed, 20 November 2026; open choices listed; partial experimental
implementation present.** This records the shared semantics of Server v1.5
"ClearView" decision C2. It does not accept a contract, advance a catalog state or
publish a version. The accountable owner is the founder under
[governance](../../GOVERNANCE.md).

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

## Decision (proposed)

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

## Alternatives

- **Return the raw error chain (v1.4).** Rejected: it discloses storage internals.
- **Infer codes for old rows from their text.** Rejected: the read path must never
  parse old messages.
- **Rewrite historical rows.** Rejected: rows stay intact.
- **Serialize an absent code as `null`.** Not adopted: the member is omitted.

## Evidence

Partial experimental implementation; no acceptance is claimed.
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
