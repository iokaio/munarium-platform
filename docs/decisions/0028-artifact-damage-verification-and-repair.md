# ADR 0028: artifact damage confirmation, fleet block and verified repair

**Proposed, 20 November 2026; open choices listed; experimental implementation
present.** This records the shared semantics of Server v1.5 "ClearView" decisions
ART1 and ART2 and the Server component's proposed verifier, pin and finding
definitions. It does not accept a contract, advance a catalog state, publish a
version or provide a REL1 receipt. The accountable owner is the founder under
[governance](../../GOVERNANCE.md).

Normative source: the Server design at
`ef32276d593c190b5a25234a85604564769d0e60` (Server `feat/clearview`), sections
[R10](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#r10),
[ART1](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#art1),
[ART2](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#art2)
and their acceptance cases, and the proposed
[definitions](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/artifact-damage.md#definitions)
and [open questions](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/artifact-damage.md#open-questions).
That page states that a hub record differing from its definitions takes precedence
and requires the page and the implementation to change.

## Context

A v1.4 hydration failure quarantines a cache key in process memory, and the warmer
upserts a best-effort, per-node `quarantined` residency observation with no fleet
enforcement authority. A reader already past its catalog check can finish after a
catalog change. Server v1.5 requires a durable fleet-wide block and verified repair
before release (REL1). ART1 requires verifier identity and independence criteria to
be recorded in this hub decision before qualification, so the definition of an
independent verifier is the shared semantic here.

## Decision (proposed)

### ART1: isolation and fleet block

1. The first integrity failure immediately isolates the affected local copy. Local
   isolation never counts toward a fleet block.
2. A fleet block requires two independent verifiers, each authorized for the tenant
   and pin, to fetch the same pinned object directly from the authoritative store and
   each compute a digest differing from the pin's expected digest.
3. A verifier's observation counts once. Replaying the same fetch under two names,
   retrying with the same verifier, timing out or comparing different pins cannot
   establish the condition. A clean authoritative fetch after local damage blocks
   nothing.
4. Each tenant-scoped artifact pin has a durable catalog block and an integrity
   generation that changes on block and on clearance and at no other time. The block
   commits with its incident identity and both confirming observations. A candidate
   recorded at an earlier generation never confirms a block.
5. Readers check the catalog at admission, capture the pin's generation and, at result
   release, serialize a final check against block and clearance on every contributing
   pin in a stable order. A block that commits first invalidates every outstanding read
   from the earlier generation, even if clearance follows. An unavailable check
   suppresses output. Content authorized before the block may be delivered; delivered
   data and its audit history are preserved.
6. Observation history is bounded separately from decision state. A full history never
   evicts findings and still permits blocking a newly confirmed pin and recovering its
   evidence. Absence of a finding is unknown integrity, never a clean audit.

### ART2: verified repair and clearance

1. Changing object bytes is separately authorized and outside this decision.
2. After that repair, two independent verifiers each fetch the repaired object from
   the authoritative store and compute a digest matching the trusted pin. Both
   observations bind to the tenant, object, component, active damage record and
   current repair attempt, and both fetches start after the attempt was authorized.
3. When both match, the preauthorized repair workflow clears that block and durably
   records both verifications, the workflow identity and the clearance, in one atomic,
   idempotent transition. Its clearance authority is scoped to that record.
4. A fresh mismatch during verification invalidates prior successes for that attempt.
   After clearance, a fresh mismatch starts a new ART1 incident. A replica that isolated
   its copy discards or reverifies it against the trusted pin before admitting it.

### Rollout

Keep the v1.4 default through a mixed-version upgrade. Activate fleet blocking and
automatic clearance only when every serving reader can enforce the durable state or
incompatible readers are drained. Rollback keeps an outstanding block effective or
the artifact withdrawn before a v1.4 reader returns to service.

### Proposed definitions carried from the Server page

| Term | Server proposal |
|---|---|
| Verifier identity | `verifier_id` = deployment environment ID plus instance ID (from `MUNARIUM_INSTANCE_ID`, `HOSTNAME` or `COMPUTERNAME`); independence is judged on this value alone. A fresh `run_id` per run and `fetch_id` per authoritative fetch |
| Independence | Different `verifier_id` and `fetch_id`; direct authoritative (L2) fetch; same pinned object at the current generation; both completed with a digest; fetch times within 24 hours for a block; both fetches after authorization for a clearance |
| Storage pin | Tenant and logical version; `artifact_id` as the sha256 of canonical manifest bytes; manifest key; each component's path, length and sha256 from manifest bytes that hash to the artifact ID; storage generation when the store reports one |
| Pinned object | One object with its expected digest and storage generation; observations of different stored generations are different pinned objects |
| Findings | Pins, candidates, incidents, repair attempts and a history bounded at 1,024 observations per tenant, none storing corpus or query text |
| Clearance authority | An operator preauthorizes a workflow for one incident through a CLI using the deployment's database credential; no `/v1` route, console action or REST role can clear |
| Modes | `off` (default, v1.4 behavior), `observe` (records and honors blocks, never commits one) and `enforce`; an unknown value refuses to arm |

## Open choices

| Choice | Options | State |
|---|---|---|
| Verifier authentication | (a) The Server proposal: replicas share one database credential and independence rests on a distinct, stable, operator-configured instance ID. (b) A per-replica authenticated identity, the recorded hardening path, for example the platform workload certificate | Open. ART1's text requires "independently authenticated verifier identities"; option (a) does not authenticate replicas to each other, and two replicas given the same instance ID become one verifier. Qualification must not claim the ART1 independence requirement is met until this is resolved |
| Storage generations | Whether the artifact store reports an object generation (ETag or version ID) so a block and its verifications bind to one stored generation; the store trait exposes none today and every observation records it as absent | Open |
| Per-result authorization records | The release fence commits a share-locked check, not a durable row per result; durable rows would add a write per search and need retention | Open |
| Bounds | 1,024-entry history and 24-hour confirmation window are constants in the proposal; ART1 names no values | Open |
| Mirror publication | Whether publication refuses a blocked pin; a rebuild converging on a blocked artifact ID currently republishes it | Open |
| Per-event stream fence | ART1-T2 requires content-bearing stream events after a block to be ones authorized before it; the proposal fences whole search results, from which streams are assembled, rather than each event | Listed open in the implementation ledger |

This record does not choose among these options.

## Alternatives

- **Block on the first mismatch.** Rejected: one observation isolates only locally.
- **Count retries or renamed replays as independent.** Rejected.
- **Present absence of findings as a clean audit.** Rejected.
- **Evict old observations when the history is full.** Rejected: refuse to append and
  keep decision state separate.
- **Clear through an API route or console action.** Rejected in the proposal: only a
  preauthorized workflow with two fresh independent matches clears.
- **Withdraw readiness on a block.** Not adopted in the proposal: every replica refuses
  the pin alike, and withdrawing readiness would turn one incident into a wider outage.

## Evidence

Experimental implementation only; no acceptance or release receipt is claimed.

- Server `cca06b13da4a2387789b5771df807213e735da1a` proposes the definitions above.
- Server `7c6d3650655df8bfdd6c619e0dc6ca4a6e667a57` implements them opt-in with
  additive migration `0060_artifact_damage.sql`. The
  [implementation ledger](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/implementation-ledger.md)
  records 15 ledger tests and 5 serving tests passing locally, with mutations caught,
  as deterministic single-process stand-ins.
- Not covered locally: paused second replicas on a real fleet, a stream spanning a
  block on a live server, an unavailable final check against a failing database,
  concurrent failures across processes, binary rollback and healthy reads on every
  replica after clearance. These are the deferred REL1 fleet receipts.

## Owners and affected consumers

| Owner | Responsibility |
|---|---|
| Founder | Accountable design owner and acceptance authority |
| Server Datastore maintainers | Ledger, fence, verifier identity and repair workflow |
| Hub contract owners | Verifier authentication and any exported finding or pin definitions |
| Deployment and chart maintainers | Distinct instance identities, mode rollout and rollback procedure |

Affected consumers: every serving replica and reader path, the rollout selector, the
artifact mirror publication path, operators running repair workflows and any future
workload-identity provider used for verifier authentication.

## Version policy

Additive and off by default: new tables, a mode switch defaulting to `off` and no
change to v1.4 wire responses. Changing the definition of an independent verifier
after qualification evidence is collected invalidates that evidence and requires
new receipts. This record adds no hub schema or vector; if verifier authentication
adopts a shared workload identity, its binding is exported through the owning
contract process.

## Consequences

- A single faulty replica cannot withdraw an artifact from the fleet, and a confirmed
  block cannot be bypassed by a warm cache or restart.
- A single-replica deployment cannot clear a block by design, and with one verifier
  identity it cannot confirm one either.
- Until verifier authentication is settled, the database cannot detect a deployment
  that gives two replicas one instance ID (collapsing them into one verifier) or a
  replica whose instance ID is not stable (letting it count as a new verifier).
