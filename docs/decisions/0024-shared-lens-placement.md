# ADR 0024: shared and dedicated Lens worker placement

**Accepted (20 November 2026).** This records the shared semantics of Server v1.5
"ClearView" decision SC2. The maintainer accepted it as written; see
[Disposition](#disposition-20-november-2026). Acceptance does not publish a contract
version, advance a catalog state or set a release label. The accountable owner is the
founder under [governance](../../GOVERNANCE.md).

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

## Decision

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

## Disposition (20 November 2026)

**Accepted by the maintainer on 20 November 2026, as written**, reviewing hub
revision `dc3aa258b0bde8b82a1ad676a4727204264997db` (`dc3aa25`, this record as
drafted). The Server implementation ledger records the acceptance as
[maintainer decision 5](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/design/implementation-ledger.md#maintainer-decisions-20-november-2026)
at Server `89e1bc2019c80d697d2d8adc9237a9ce577cf3d7`. This disposition changes the
record's state only. It publishes no contract version, composition manifest or
release label, advances no catalog state or invariant evidence field, and activates
nothing.

This record listed no open choices. The placement-policy representation its version
policy leaves to the owning process is recorded as the Server implemented it on
`feat/clearview` (Server `9a14fd021de00d21ffcc18a933b4bc5943b37683`, additive
migration 0081, ledger row SC2 and the Server
[placement guide](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/guides/inference-endpoints.md#shared-and-dedicated-placement)):

| Item | Resolution |
|---|---|
| Pool declaration | `inference.placement` on an `openai-compatible` provider configuration: `mode` `dedicated` or `shared`; a shared pool lists every covered tenant in `tenants` and declares at least one `processing` rule. Sharing is never implied by omission. |
| Binding requirement | Optional `placement` on the collection binding: `isolation` `dedicated` or `shared`, plus required `processing` rules compared exactly. A rebind without `placement` keeps the existing requirement, so placement is never loosened implicitly. |
| Refusal reasons | `placement_tenant_not_covered`, `placement_undeclared`, `placement_dedicated_required` and `placement_processing_incompatible`: a refused bind or probe is 409 `inference-not-qualified`; an existing binding that no longer satisfies placement turns its stages `unconfigured`, and the ADR 0023 stage policy then refuses or takes the disclosed fallback, which sends nothing. |
| Check point | Before any content is sent, on serving, shadow, build and every retry. Server never chooses another endpoint when dedicated capacity is lost. |

Cluster placement receipts (SC2-T1 to SC2-T3 on a fleet) remain deferred.

Maintainer decisions of 20 November 2026 that bear on this record:

- **Decision 6** accepts the inference wire fields as release ready. The placement
  fields extend the same inference configuration but were added the same day
  (`9a14fd0`); whether decision 6 covers them awaits the maintainer's confirmation.
  The hub contract export named in the version policy remains a separate step.
- **Decision 17.** Cluster qualification, including the placement receipts, runs
  only on the maintainer's workstation cluster and is deferred.
- **Decision 1.** Binary rollback across v1.5 migrations, including 0081, is by
  backup restore.

## Alternatives

- **Share pools by default.** Rejected: sharing requires explicit coverage of every
  participating tenant.
- **Fall back to a shared pool when the dedicated pool is empty.** Rejected: fallback
  is the collection's stage policy, still subject to placement.
- **Keep a cache that cannot enforce isolation or expiry.** Rejected: disable it.

## Evidence

No implementation evidence at drafting. The implementation since is cited in the
[disposition](#disposition-20-november-2026). At drafting, the [implementation ledger](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/implementation-ledger.md)
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
