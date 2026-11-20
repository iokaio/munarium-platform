# ADR 0023: enrolled inference outage policy and collection-owned budgets

**Proposed, 20 November 2026; open choices listed.** This records the shared
semantics of Server v1.5 "ClearView" decisions I1 and I2, which the Server design
treats together for every enrolled read. It does not accept a contract, advance a
catalog state or publish a version. The accountable owner is the founder under
[governance](../../GOVERNANCE.md).

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

## Decision (proposed)

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

## Alternatives

- **`prefer` as the enrolled default.** Not adopted: fallback requires an explicit
  operator choice.
- **Blending endpoint relevance scores with fusion scores.** Rejected: scores are not
  comparable between models.
- **Charging each caller's own budget.** Not adopted: the collection's tenant-owned
  budget pays, with caller attribution retained.
- **Letting Server truncate over-limit input.** Rejected: it is a refusal.

## Evidence

No implementation evidence. The [implementation ledger](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/implementation-ledger.md)
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
