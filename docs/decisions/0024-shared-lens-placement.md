# ADR 0024: shared and dedicated Lens worker placement

**Proposed for maintainer review, 20 November 2026.** This records the shared
semantics of Server v1.5 "ClearView" decision SC2. It does not accept a contract,
advance a catalog state or publish a version. The accountable owner is the founder under
[governance](../../GOVERNANCE.md).

Normative source: the Server design at
`ef32276d593c190b5a25234a85604564769d0e60` (Server `feat/clearview`), sections
[SC2](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/repository-handoffs.md#sc2)
and [independent Lens replicas](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/repository-handoffs.md#independent-lens-replicas),
with the placement note under
[I2](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#i2).

## Context

Lens serves embedding and reranking from independently sized pools that several
tenants' enrolled collections may reach. Whether content from two tenants may meet
on one worker, and what happens when a dedicated pool is empty, is a boundary shared
by Server admission, Lens deployment and operators' tenant policies.

## Decision (proposed)

1. Admit work to a shared Lens pool only with explicit, current authorization covering
   each participating tenant and compatible processing, location, retention and
   isolation requirements.
2. Resolve the authenticated tenant, permitted collection, model binding and placement
   policy **before sending any content**, including build inputs, queries, retries and
   shadow traffic.
3. Keep credentials, results and budget reservations scoped to the tenant. Budget
   enforcement follows [ADR 0023](0023-enrolled-inference-policy-and-budgets.md).
4. Any enabled cache of inputs, vectors or results isolates entries and lookups by
   tenant, authorized binding and model identity, and honors that tenant's retention
   policy. Disable the cache when isolation or expiry cannot be enforced.
5. A tenant requiring isolation uses its approved dedicated pool. If that pool has no
   ready worker, apply the collection's configured stage policy under ADR 0023,
   including any authorized fallback; each fallback remains subject to placement checks.
6. Route by requested stage and exact served identity; a replica joins a pool only
   after verifying its manifest and passing a probe. Automatic load-balancer replays of
   submitted inference calls are disabled; Server accounts for any permitted new attempt.

## Alternatives

- **Share pools by default.** Rejected: sharing requires explicit coverage of every
  participating tenant.
- **Fall back to a shared pool when the dedicated pool is empty.** Rejected: fallback
  is the collection's stage policy, still subject to placement.
- **Keep a cache that cannot enforce isolation or expiry.** Rejected: disable it.

## Evidence

No implementation evidence. The [implementation ledger](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/implementation-ledger.md)
records SC2 as planned, pending this record. Acceptance cases SC2-T1 to SC2-T3
require zero request content at a forbidden worker on serving, build, retry and shadow
paths.

## Owners and affected consumers

| Owner | Responsibility |
|---|---|
| Founder | Accountable design owner and acceptance authority |
| Server inference admission maintainers | Placement resolution before dispatch and per-tenant isolation |
| Lens maintainers | Pool identity, readiness, cache behavior and replay settings |
| Deployment and chart maintainers | Pool configuration and operator documentation |

Affected consumers: Lens deployments, Server scale-out qualification (SC1), tenant
administrators who approve sharing, and the Server operator runbooks.

## Version policy

The Server design names the placement-policy contents but not its representation.
That representation and its rejection vectors are exported through the owning
contract process with ADR 0023's stage policy before consumers rely on it. With no
enrollment, nothing is sent to any pool (COMPAT-T4). This record adds no hub schema
or vector.

## Consequences

- Sharing is an explicit, auditable tenant decision; a missing or incompatible policy
  sends nothing.
- Dedicated isolation can reduce availability; the stage policy, not an implicit shared
  fallback, governs that case.
