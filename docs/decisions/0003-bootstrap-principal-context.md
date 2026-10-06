# 0003: bounded bootstrap and verified principal context

**State: proposed for maintainer review; not accepted.** Date: 6 October 2026.
Packet: HUB-01 / DEC-01. Accountable acceptance owner: founder under
[GOVERNANCE](../../GOVERNANCE.md). Consumers: Server, Warden, Council and Registry.

## Requirement and inspected boundary

S1 requires governance authority separate from an ordinary governed writer; S3 requires
verified origin and delegation. Server at `2c40480fdc2378e66dc23acdfaf82b529b9d22ee`
already has immutable governance revisions and expected-head checks in
[governance.rs](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-core/src/governance.rs).
Its [principal](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/src/munarium-server/src/state.rs)
distinguishes static callers from Server capability tokens. Neither is the platform's
verified origin/delegation chain. These are planned extensions to the documented Server
trust boundary, not evidence that existing identity checks are absent.

## Proposed decisions

1. Introduce an explicit platform authority profile. A governed writer may propose data
   and candidate artifacts but cannot install or change governing rules. Management-token
   issuance, governance activation and ordinary writes are separate permissions. No role
   implies another. Preserve the existing API in its documented legacy profile; label it
   outside platform qualification. A deployment cannot silently downgrade profiles.
2. Server verifies authority at every governing mutation, on REST and gRPC, including
   initial governance, changed child policies, publication policy, shape/runbook application
   and index approval/cutover. Inventory these paths before an S1 PR; enforcing just one
   endpoint does not pass S1. Inheritance without a rule change remains ordinary governed
   work, subject to the same stored-policy and tenant checks.
3. Bootstrap is a tenant-scoped, explicitly enabled administrative enrollment, controlled
   outside the agent process. A deployment supplies its initial trusted public key through
   operator configuration, never a request or downloaded hub document. An attestation
   binds contract version, deployment ID, tenant, target service audience, action,
   artifact digest, expected prior revision/head, bootstrap epoch, nonce, issuer/key ID,
   non-agent human subject and issuance/not-before/expiry times. A subject label is not
   evidence: its type and enrollment must be authenticated by the configured authority.
4. Verification and consumption commit with the governance transition. Reject stale prior
   state, wrong audience/tenant, revoked or retired keys, expired attestations and reused
   nonces with changed content. Same nonce and identical content returns the recorded
   transition; it never repeats the mutation. Record the verified identity, old/new state,
   attestation digest and result as append-only evidence. A signature alone is insufficient.
5. Retirement is a monotonic, durable transition for that tenant/bootstrap epoch. Install
   the successor authority and retire bootstrap atomically in Server's authority store.
   Restarts and replay cannot re-enable it; restore must remain authority-disabled until an
   externally retained epoch/cutoff is reconciled. Recovery is a separate governed process,
   not deletion of a retirement row. Full Council promotion remains DEC-04.
6. Warden verifies the upstream identity and issues a short-lived, service-audience-bound
   principal assertion. Consumers validate it locally against provisioned issuer keys and
   freshness/revocation requirements. Proposed envelope: JWS with a single pinned Ed25519
   algorithm, exact issuer and audience, explicit key ID, no algorithm negotiation or
   request-selected key URL. Algorithm/library/version qualification and signed vectors
   are required before acceptance; this document does not supply a cryptographic verifier.
7. Principal context binds deployment, tenant, immutable origin, current actor, authenticated
   service identity, subject kind, purpose, scopes, resources, expiry, delegation IDs and
   parent assertion digests. Transport peer identity must match the asserted service.
   Delegation preserves tenant/origin; intersects scopes/resources and expiry; has no
   cycles and at most four edges. Unknown scope/resource forms refuse. Agent-originated
   chains can never gain ratification or bootstrap authority, even through a human label.
8. Governance operations require current key/retirement state; an unavailable authority
   check refuses mutation. Decision-only evaluation also records unavailable identity as
   a refusal. Historical signature verification is distinct from current activation power.

## Review vectors and required S1/S3 tests

The values below are synthetic semantic oracles, not executed cryptographic vectors.
Each accepted signed vector must pin canonical payload bytes, signature, public key,
verification time, issuer state and expected result. Never commit signing private keys.

| Case | Change from valid tenant-a / server audience / epoch 1 / nonce n1 | Required result |
|---|---|---|
| B01 | Enrolled human, current key, exact prior head and bounded artifact | One transition and immutable receipt |
| B02 | Ordinary writer or agent origin | Refuse; no active-state change |
| B03 | Forged signature, unknown key or substituted payload | Refuse; no active-state change |
| B04 | tenant-b or Registry audience | Refuse; no active-state change |
| B05 | Same nonce and identical digest | Original receipt, no second transition |
| B06 | Same nonce with a changed artifact | Conflict; original receipt preserved |
| B07 | Stale prior head/revision; two concurrent transitions | At most one transition; stale request conflicts |
| B08 | Expired, future, revoked or retired key/epoch | Refuse, including after restart |
| B09 | Delegated narrower scope and shorter lifetime | Accept only narrowed authority; never ratification |
| B10 | Wider scope, changed origin/tenant, cycle or fifth edge | Refuse |
| B11 | Authority unavailable or restored pre-retirement snapshot | Refuse mutation until governed recovery |
| B12 | REST versus direct gRPC for B01–B11 | Same authority decision and persisted effects |

Run tests against both memory semantics and PostgreSQL persistence where supported;
concurrency, retirement/restart and replay require real persistence. Existing governance
revision tests remain regression coverage. No successful foundation test implies B01–B12
already pass. S1 opens only after an explicit maintainer disposition of this revision.

## Alternatives and migration

Reusing static `rw` as governance authority cannot establish S1's distinct permission.
Treating a supplied `human` flag or UID as verification cannot establish S3. Making Council
mandatory for first enrollment creates a bootstrap cycle; the bounded initial operator
attestation breaks that cycle and must be retired. A shared symmetric verification secret
would also let each verifier forge the issuer, so asymmetric assertions are proposed.

Server owns verification integration, additive storage/migrations, audit and both transports;
Warden owns identity issuance/attenuation; Council later owns approval/activation workflows;
Registry resolves candidates without activation. Core remains independent of providers,
HTTP and storage implementations. Existing capability tokens are not reinterpreted as
platform assertions. Expand with explicit version/profile negotiation, migrate deployments
and consumers using pinned vectors, then remove legacy behavior only at a declared boundary.

The [candidate schemas and signed vectors](candidates/README.md) now specify exact
algorithm, lifetime/skew, key/issuer and attenuation test inputs, with a candidate digest.
They do not establish deployment authority or S1/S3 persistence. Acceptance still requires
an explicit maintainer disposition of the reviewed revision and compatibility policy.

The [proposed Warden identity contract](warden-identity-contract.md) makes the
candidate wire bytes, trusted verification inputs, attenuation and consumer obligations
explicit for WARDEN-01. Its additional offline tests preserve the candidate oracle;
provider mapping, transport/profile pins and maintainer acceptance remain required.
