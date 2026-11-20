# ADR 0023: enrolled inference outage policy and collection-owned budgets

**Accepted (20 November 2026).** This records the shared semantics of Server v1.5
"ClearView" decisions I1 and I2, which the Server design treats together for every
enrolled read. The maintainer accepted it as written; see
[Disposition](#disposition-20-november-2026). Acceptance does not publish a contract
version, advance a catalog state or set a release label. The accountable owner is the
founder under [governance](../../GOVERNANCE.md).

Normative source: the Server design at
`ef32276d593c190b5a25234a85604564769d0e60` (Server `feat/clearview`), sections
[I1](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#i1),
[I2](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#i2),
the reply rules in
[8.6](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#86-the-seam-an-inference-endpoint-behind-the-provider-gateway)
and enablement in
[8.9](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#89-enablement-and-governance).

## Context

Server v1.5 can send enrolled collections' embedding and reranking work to an
inference endpoint, with Munarium Lens as the qualified reference. Lens, the Server
consumer, the MCP tools and worker placement under
[ADR 0024](0024-shared-lens-placement.md) must agree on what an enrolled read does
when a stage is unavailable and who pays for each physical call. Unenrolled
collections keep the v1.4 hash path.

## Decision

### I1: outage policy

1. On an explicitly Lens-enrolled collection, `require` is the default for every
   configured inference stage. Only an explicit operator selection of `prefer` permits
   that stage's documented fallback.
2. Under `prefer`, an unavailable semantic embedder permits a disclosed lexical-only
   search, and an unavailable reranker permits the original fused order. Record the
   stage, reason and effective policy revision. All authorization and evidence checks
   stay in force.
3. Under `require`, an unavailable embedder or reranker produces a typed refusal for
   the governed collection read, including a failed or invalid response, an expired
   deadline or insufficient budget. A failed stage is never marked applied.
4. A rerank reply is used for order only, must account for every passage sent exactly
   once, and is treated as untrusted; Server keeps the authorized originals. Input
   beyond the model's token limit is a refusal for that request, never silently
   truncated. Shadow mode records only the candidate outcome.
5. A multi-collection read may return other independently verified results under
   [ADR 0021](0021-partial-multi-collection-reads.md), but cannot use a refusing
   collection's unapproved fallback or support an answer that requires its missing
   evidence. An authorized shadow failure affects only its comparison record.
6. Stage diagnostics distinguish disabled, unenrolled, unconfigured endpoint, failed
   probe, unavailable endpoint, exhausted budget and ready, with content-free reasons.
   MCP tool arguments cannot relax the policy, select the endpoint or enroll a collection.

### I2: budgets and attribution

1. The collection's tenant-owned budget pays for its embedding and reranking.
2. Every endpoint call, including retries and build work, is attributed to the
   initiating caller in the audit record; that identity is carried through queued work.
3. Explicitly authorized shadow evaluations are metered separately from serving calls,
   including failed or discarded attempts.
4. Reserve against the responsible budget before dispatch; denied admission makes zero
   outbound calls. One request deadline covers queueing, attempts and delivery. Record
   actual usage when known and reconcile each attempt once; missing token or tariff
   data stays unknown, and an unpriced call remains visible in coverage.
5. A multi-collection read preserves each collection's authorization and payer. A
   prepared embedding is reused only within a compatible authorized group sharing the
   same budget binding. A shared physical call is charged once and records which
   collections it served. Tenants' reservations, usage and credentials stay isolated.

## Open choices

| Choice | State in the Server design | Closing evidence named by Server |
|---|---|---|
| I2 shadow quota and its allocation within the tenant budget | Explicitly deferred to implementation and listed as an open item | Specify the allocation within the existing tenant cap and reconcile serving and authorized shadow usage under contention |
| Wire spelling of the stage policy, refusal types and stage receipt | Not specified; the receipt depends on R1 disclosure | Exported contract and conformance |
| Runtime, endpoint profile and endpoint selection | Stated as separate implementation decisions | Not a shared semantic of this record |

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
(Server `3ff798b827e3d929eb8bf87e2e92ae4945b2448b` with additive migration 0080,
ledger rows I1 and I2, the ADR 0023 table in the Server
[wire compatibility policy](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/wire-compatibility.md) and the
[inference endpoint guide](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/guides/inference-endpoints.md)):

| Choice | Resolution |
|---|---|
| I2 shadow quota and its allocation | `budgets.shadowDailyTokens` on the bound provider configuration is carved out of `dailyTotalTokens`. Shadow attempts reserve only from the carve-out; serving, build and probe attempts reserve only from the remainder. Absent, no shadow work is authorized, and a configuration without the carve-out keeps its exact v1.4 limit. |
| Wire spelling of the stage policy, refusal types and stage receipt | Stage policy `policy: "require" \| "prefer"` per stage on the collection binding, `require` when omitted. Refusal types `inference-stage-unavailable` (503, retry guidance `retry_later`) for a refused read and `inference-not-qualified` (409) for management preconditions. Fallbacks are disclosed as `lexical_only` and `fused_order`. Stage receipt `execution.stages[]` on the R1 execution disclosure, with `stage`, `policy`, `policy_revision`, `applied`, `state`, `reason`, `fallback`, `identity` and `scored`; it is serialized only when non-empty, so unenrolled reads are unchanged. |
| Runtime, endpoint profile and endpoint selection | Remain separate implementation decisions, not shared semantics of this record. The Server speaks the Lens LENS-1 profile through the `openai-compatible` provider kind. Instruction-prefix ownership is recorded separately in [ADR 0029](0029-inference-instruction-prefix-ownership.md). |

Maintainer decisions of 20 November 2026 that bear on this record:

- **Decision 6.** The inference wire fields above are accepted as release ready. The
  hub contract export named in the version policy remains a separate step; this
  disposition does not perform it.
- **Decision 2.** The Lens model pair is Qwen3-Embedding-0.6B with
  Qwen3-Reranker-0.6B at 1024 dimensions. This is an implementation choice under
  the third row above and changes no semantic of this record.
- **Decision 3.** The Server owns instruction prefixes and Lens applies none; see
  ADR 0029.
- **Decision 1.** Binary rollback across v1.5 migrations, including 0080, is by
  backup restore. Per-collection enrollment rollback (IR-4) is a separate control
  route that calls no endpoint and is unchanged.

## Alternatives

- **`prefer` as the enrolled default.** Not adopted: fallback requires an explicit
  operator choice.
- **Blending endpoint relevance scores with fusion scores.** Rejected: scores are not
  comparable between models.
- **Charging each caller's own budget.** Not adopted: the collection's tenant-owned
  budget pays, with caller attribution retained.
- **Letting Server truncate over-limit input.** Rejected: it is a refusal.

## Evidence

No implementation evidence at drafting. The implementation since is cited in the
[disposition](#disposition-20-november-2026). At drafting, the [implementation ledger](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/implementation-ledger.md)
records I1 and I2 as planned. Acceptance cases I1-T1, I2-T1 and I2-T2 define the
required evidence, including zero outbound calls after denied admission.

## Owners and affected consumers

| Owner | Responsibility |
|---|---|
| Founder | Accountable design owner and acceptance authority |
| Server retrieval maintainers | Stage policy, fallback disclosure, refusals and multi-collection grouping |
| Server tenant budget owners | Reservation, reconciliation, shadow metering and attribution |
| Lens maintainers | Endpoint behavior the probe and reply rules rely on |

Affected consumers: Lens and any other endpoint passing the generic probe, the MCP
search and answer tools, the four Server SDK families through R1 disclosure fields,
operator reports and the console.

## Version policy

Additive: unenrolled collections and omitted settings keep v1.4 behavior (COMPAT-T4).
Policy revisions are recorded with each fallback. Refusal types and receipt fields are
exported through the owning contract process before consumers rely on them. This
record adds no hub schema or vector.

## Consequences

- An enrolled collection fails closed by default; operators accept degraded retrieval
  only by explicit, recorded choice.
- Tenant owners bear inference cost for their collections while audit retains who
  caused each call; shadow work cannot silently consume serving capacity once its
  allocation is fixed.
- Until the shadow allocation is specified, shadow evaluation cannot be qualified.
  The disposition records the implemented allocation.
