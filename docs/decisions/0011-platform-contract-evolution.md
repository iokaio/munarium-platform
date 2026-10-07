# 0011: contract evolution across the platform

**Proposed for maintainer review, 7 October 2026.** This second pass supplements
[ADR 0010](0010-stage2-authority-durability.md), not the accepted status of any
contract. It records requirements for the next candidate cut; no schema, vector,
consumer, active authority or qualification label changes here. The accountable
owner is the founder under [governance](../../GOVERNANCE.md).

## Requirement and evidence

The [platform plan](../platform-plan.md), sections 12–19 and 22, requires shared
task accounting, monitoring coverage, offline verification, governed interfaces
and eventual federation. A contract sufficient for one publication must not
make those capabilities depend on ambiguous identities, a global epoch or an
action-only ledger. The [review findings](../architecture/platform-contract-review.md)
map these requirements to current candidates and required acceptance cases.

Retain Stage 1's exact bytes and decision-only behavior. Retain Stage 2's single
Gate transaction owner, bounded sends and durable unresolved exposure. Introduce
new versions where these semantics differ; neither permissive extra fields nor
reinterpretation of an existing digest is a migration strategy.

## Identity, intent and authorization attempts

The next action request separates the following typed identities:

| Identity | Binding and lifetime |
|---|---|
| Principal reference | Authority domain, tenant, enrolled subject and subject generation; preserves verified origin, actor and delegation attribution without making token expiry the subject identity |
| Authentication proof | Issuer, recipient, credential/token digest, issuance and validity; verified on each call and recorded as evidence, never replaced by a caller's subject string |
| Operation | Home cell plus stable semantic/business operation key and immutable intent digest; retries and credential refresh retain it |
| Evaluation / authorization attempt | Operation plus an immutable request/context digest and unique attempt ID; binds the exact decision, approval and applicable validity windows |
| Effect key | Stable target deduplication/reconciliation identity for the operation; changing an attempt, grant, process or time window does not change this key |
| Task / delegation | Verified root task and parent lineage with admitted agent release/instance references where applicable; a session or correlation label alone confers no authority |

Intent includes the exact capability operation, target, environment, parameters,
attachments and requested preconditions. Same operation with changed intent
conflicts. A changed governing context requires a new evaluated attempt and fresh
approval, not mutation of the approved bytes. Before a claim, an atomic transition
may supersede the previous unclaimed attempt. After a claim, supersession is
limited to an abandoned, unconsumed claim: Warden durably closes its issuance and
Gate conditionally disables old admission while verifying it is still unconsumed.
Both exact receipts are required before a fresh linked claim/attempt can proceed;
a concurrent consumption winner prevents supersession. A consumed claim is never
recycled. Another execution after definitive failure uses an explicitly authorized
new operation linked by `retry-of`, as in the [action lifecycle](../architecture/action-lifecycle.md).
Unresolved work prevents replacement even under a new client key; expiry or
withdrawal alone is not proof of no effect. Changed intent or compensation is
also a separately authorized operation, never an automatic retry.

Gate enforces uniqueness and unresolved exposure at operation/effect scope across
attempts; Warden's per-claim issuance uniqueness alone is insufficient. Approval,
claim, grant, cancellation and final admission bind both operation and attempt.
Requesters use a domain-specific business key where one exists; fresh random IDs
cannot establish that two requests are different business intents. The target
adapter declares its deduplication boundary and limits. Do not promise generic
semantic duplicate detection for arbitrary caller-selected keys.

Stage 1's principal digest includes the original token context. Its existing
recovery path correctly authenticates a current caller separately from the
archived request. Keep that behavior and its original digest. New action schemas
make the durable reference/proof distinction explicit; they do not recompute old
requests with refreshed tokens. Current permission governs lookup and recovery;
possession of a historical proof never grants current access or dispatch.

In Registry v2, manifest `operation_id` names a capability operation; a request's
`operation_id` identifies an instance. Preserve those existing fields. New
contracts use unambiguous typed names such as `capability_operation` and
`operation_ref`, with an explicit adapter mapping and no string interchange.

## Namespaces, epochs and context

Authoritative references bind domain, tenant, deployment/home cell, object kind,
object ID and revision/digest as appropriate. Ledger and source references also
identify their owning ledger/source. A local profile can pin the domain and cell
in its authenticated configuration, but APIs must check that binding; identical
unqualified IDs from another tenant, cell or issuer are not equivalent. No global
transaction, shared budget or interchangeable grant audience follows from UUIDs.

| Revision / epoch | Owner and meaning |
|---|---|
| Authority revision | Owning authority's identity, membership or permission state |
| Activation epoch | Selected governing artifact set in a declared admission scope |
| Recovery epoch | Externally established restart/restore generation for a cell |
| Source generation and sequence | One registered producer stream's event continuity |
| Worker fence | Gate's ownership generation for one claim |
| Target precondition/version | Target's concurrency and effect-admission state |
| Schema/profile version | Interpretation and qualification, not runtime permission |

Compare each only within its named owner and scope. A higher activation epoch
does not satisfy a target fence; a newer source sequence does not establish a
fresh authority context. Use distinct fields/types, not a generic `epoch` integer.

A decision context is an immutable set of qualified dependency pins: policies,
manifest/agent release, evaluator profile, identity/approver authority, evidence
and applicable mode. Its digest binds the exact set. Multiple ledger pins form
a composite snapshot with explicit freshness constraints, not a claim of global
atomicity. Each dependency declares which current checks invalidate admission;
unknown, stale or unavailable required checks refuse. Irrelevant changes must not
silently become equivalent authority or implicitly refresh an approval. The first
profile may conservatively invalidate the entire cell on any authority change;
it must declare that scope. Narrower invalidation requires separately tested rules.

New digest domains bind object kind and schema version as well as canonical
content. Specify exact preimage bytes and algorithm per version in golden vectors.
Do not accept arbitrary negotiated algorithms or change Stage 1 hash preimages.
Retain closed schemas and bounded canonical numbers. Monetary quantities use
declared integer units/currency and overflow checks, never floating-point JSON.

## Evidence meaning and historical interpretation

An evidence pin includes its qualified source/revision, content digest, field or
query scope, derivation/version, observation and required freshness, trust label
and the authority/verifier that assigned that label. Policy declares which fields
require authoritative evidence. An agent assertion does not become authoritative
because it has a hash, signature or Server ledger position. Conflicting claims,
corrections and supersession remain visible at the selected point-in-time pins;
missing evidence is not a favorable default.

For Matrix results, distinguish logical-result identity from serialized artifact
bytes and retain query parameters, schema fingerprint and source provenance.
Cache reuse binds those inputs plus current access and trust-label policy, not
only a query string. An archived decision records the actual enforcement mode
separately from any shadow result. Historical replay can explain that decision;
it cannot authorize a current action or present reconstructed/missing inputs as
the original verified evidence. The next action context binds these references;
general query/export implementation stays with its later foundation packet.

## Obligations, budgets and policy composition

Decisions carry versioned typed obligations with exact parameters, enforcing
owner and required evidence. The profile declares the complete supported set.
Unknown mandatory kinds, unsupported versions or unavailable enforcing owners
refuse admission; they are not advisory strings that an older consumer may drop.
The first action profile implements its approval, recording, capacity and custody
requirements only. Later quorum, monitoring and disclosure requirements need
their own payload schemas and conformance cases before use.

Gate action capacity and Gateway model spend are separate balances and commit
owners. They share authenticated task/delegation references and vocabulary for
reservation, settlement and correction, not a cross-database atomic reservation
claim. One home owner must admit each shared limit; two cells cannot each spend
the full same cap. All delegated children charge their admitted root lineage;
callers cannot evade a limit by choosing a new session or omitting their parent.
Standalone work receives an authoritative root binding at admission.

Gateway's later invocation contract must bind provider/model endpoint, data
classification and destination/location constraints, units/currency, price-source
version, bound type (exact, conservative or token-only), reservation and outcome.
Unknown cancellation/streaming charges retain exposure until settlement evidence;
unknown price is not zero cost. These are future payload requirements, not an
obligation to put prompts or model fields into every action request. Matrix query
schema/parameters and logical-result provenance use evidence references; a
read-only query can still have disclosure or cost obligations.

Later policy composition preserves mandatory parent prohibitions and permits
local restrictions only; source and destination permissions are both required.
The single-cell profile rejects cross-domain execution rather than accepting an
unchecked remote allow. Federation's issuer trust, freshness, outage and budget
allocation protocol remains a later decision, independent of the policy engine.

## Activation, suspension and profile boundaries

An activation transition binds a named scope, expected prior set/epoch, successor
set/epoch and a digest of its required participant/receipt set. ADR 0010's first
set is Council coordinating Registry, Server, Warden and Gate. Adding Gateway or
another enforcement participant requires an admitted profile/transition; a
consumer cannot silently ignore a new required participant. Observation-only
Console, Sentinel and Assure are not universal prerequisites for admission.

Use explicit states for submitted, ratified, staged, partially applied, active,
failed and retired, with per-owner receipts. During partial activation, an active
Registry pointer is not proof that the cell resumed. The composition's completion
receipt and Gate's conditional resume establish admission state. Multi-cell
activation is not globally atomic. Time-lock/not-before and expiry bind the
transition; qualification declares trustworthy clock and allowed skew. Future
emergency rollback restores only a specifically authorized digest/scope through
a fresh transition and epoch, never an arbitrary bundle or old approval.

Sentinel suspension is a bounded, authenticated request to Warden, naming subject,
scope, reason, evidence, duration and idempotency key. Separate requested, durably
accepted, enforcement-observed and expired states. Warden's acknowledgement does
not prove every Gate or target stopped; measure propagation and already admitted
work separately. Expiry ends the suspension constraint but cannot restore revoked
or otherwise absent authority. Sentinel cannot issue authority. Policies that
require current monitoring fail closed when it is missing; baseline Gate/Warden
hard controls do not depend on dashboard availability.

Wire semantics are independent of persistence, OS, IdP, broker and orchestration
choices. An immutable compatibility profile pins supported schema/event/obligation
versions, canonicalization, crypto and evaluator, timing/freshness, authority and
participant scopes, transport and custody assumptions, stores and target behavior.
The local Linux/PostgreSQL proposal is one profile, not a universal protocol
requirement. Windows, air-gapped, managed cloud and on-premises profiles need their
own evidence; matching wire bytes alone does not qualify isolation or recovery.

## Accountability shared by all event families

Prepare a common versioned envelope and separately versioned, closed payload
families. The envelope binds event identity/kind/version, domain/tenant/cell,
authenticated source/stream/generation/sequence and predecessor, payload digest,
causal references, and producer occurrence time with its clock provenance. Server
records a distinct receipt time and ledger position. Time is not a universal order.
Action payloads require operation/attempt/request and admission context; model
invocation, activation and suspension payloads require their own relevant bindings.
Do not require fake action IDs, mode or activation epochs on unrelated facts.

Each authoritative producer commits its state transition and immutable outbox in
one local transaction (or a qualified equivalent). Gate is not the only producer
that needs crash-safe delivery: Council approvals, Warden issuances/suspensions
and Registry transitions do too. Server authenticates producer/kind authority,
enforces per-stream continuity and conflict rules, and acknowledges exact event
and payload digests at a qualified ledger position. A required acknowledgement
depends on the operation/profile; no fabricated no-op action fills that role.

Stream scope is registered and authorization-compatible, at least tenant-scoped
for the first profile. Sequence continuity is per stream, not per operation; one
operation can link facts from several streams without a universal order. Required
prerequisites and permitted cross-source references are defined by payload kind.
An out-of-order delivery is pending/refused, never acknowledged as accepted.
Unsupported kinds may be preserved only by an explicit opaque archival path;
archiving them cannot satisfy a required validated acknowledgement or admission.

The historical recovery path in ADR 0010 retains original source bytes and proven
old prerequisites while authenticating a current recorder. Recorded history is
not current authority. Historical issuer/key validity, verification time basis
and known compromise/revocation evidence are retained for offline interpretation;
a signature alone proves neither completeness nor current permission.

## Coverage, access and retention

Reserve the read/export contract now, implement S5/S6 and later consumers in their
planned packets. A view/export identifies its authorized scope, immutable range
or composite pins, source stream/generation, committed cursor and known coverage
through a cutoff. Pagination binds that same scope/cutoff; current access checks
apply on every page and after permission changes. No silent switch to live data.
Distinguish no events from missing intervals, lag, aggregation, withheld data,
expired content and unsupported interpretation. Server cannot attest to events
never produced: coverage is relative to registered sources and their evidenced
watermarks, not a promise that every real-world action was captured.

Sentinel projections are rebuildable from those ranges. Assure packages name
composition/profile, trust anchors supplied independently of the package, exact
artifacts and ledger ranges, inclusion/omission rules and unresolved outcomes.
Signatures establish integrity under that trust context, not completeness or the
truth of source claims. Redacted/aggregated exports state their reduced coverage;
they do not reuse a full-evidence qualification label.

Keep minimal non-reusable operation/grant tombstones and unresolved exposure
separate from sensitive payload retention. The first action profile has no
automatic identity/outcome expiry; that is not a rule to retain raw prompts,
credentials or customer content forever. Payloads use controlled content-addressed
references with classification, access and retention metadata. A digest/reference
does not confer read access or authorize fetching an arbitrary URL. Corrections,
supersession and governed removal leave explicit historical disposition and lost
reconstructability. A package with removed inputs cannot claim full replay.

Console and CLI use the same governed public APIs. Mutation intent binds the exact
request/context digest, current human authority, expected revision and idempotency
key; stale content requires a new review. Session, CSRF and provider specifics
belong to the client/admission profile, not caller-asserted authority headers.
Responses separate policy outcome, workflow/admission state, target effect and
recording status; HTTP success or approval is never presented as completed effect.
Typed errors distinguish invalid input, conflict/stale context, denied authority,
unsupported semantics and unavailable required evidence. Recovery guidance names
the existing operation/attempt and permitted lookup or exact retry; an ambiguous
effect never suggests creating a new operation or sending again.

## Alternatives, ownership and migration gate

Extending today's closed schemas in place would invalidate pins and independent
clients. Making all payloads freeform would hide unsupported obligations and
break offline interpretation. Building a universal federation/runtime framework
now would delay the first slice without evidence. Use typed shared semantics and
bounded profiles, with later payloads introduced only when their owners implement
them. Tradeoffs include additional attempt identity and explicit context/coverage
metadata; these make recovery and interpretation reviewable rather than implicit.

| Owner / consumers | Next cut or later responsibility |
|---|---|
| Hub; Harness and all clients | Version/digest rules, valid and negative cross-language vectors, composition compatibility matrix |
| Warden; Council, Gate, Registry, Gateway | Durable identity/proof distinction, qualified authority, task/delegation admission; later suspension protocol |
| Gate; Council, Warden and connectors | Operation/attempt/effect binding, scoped invalidation, atomic action journal and typed obligations |
| Council and Registry; all enforcement participants | Exact approval, scoped activation/compatibility state and participant receipts |
| Server; all producers | Common envelope, action payload coexistence, producer outboxes, historical recovery; later range/export verification |
| Gateway; Server and Harness | Later invocation/price/settlement payload and shared task attribution, with separate admission owner |
| Sentinel, Assure and Console | Later coverage/projection/package/API implementations against explicit shared semantics |
| Matrix; Gate and Server | Read-only provenance and controlled disclosure; no dependency on private adapters |

Before cutting Stage 2 candidates, resolve the next-cut rows in the review and
pin this ADR with ADR 0010 and the selected profile. Generate new schemas/vectors
through the owners' exporter/re-vendoring process; keep old artifacts and consumer
tests. Exercise refusal of unsupported versions and mixed compositions, not just
new happy paths. Expand, migrate, remove only after exact consumer/profile pins
and compatibility evidence exist. No silent downgrade on a side-effecting path.
Later Gateway, export, UI and federation implementations remain separate packets;
their absence does not block the single-cell profile unless it claims them.
