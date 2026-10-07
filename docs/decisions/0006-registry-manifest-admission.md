# 0006: signed manifest admission and tenant ownership

**State: proposed for maintainer review; not accepted or published.** Date: 6 October 2026.
Packet: HUB-02 / DEC-02, Registry admission subpacket. Accountable acceptance owner:
founder/maintainer under [GOVERNANCE](../../GOVERNANCE.md). Consumers: Registry, Gate,
Harness, Warden, Council and Server. Depends on [0003](0003-bootstrap-principal-context.md)
and [0004](0004-decision-only-contracts.md), plus
[0005](0005-warden-identity-admission.md) for receiving-side identity admission.
This record does not accept those proposals. Renumbered from the unpublished Registry
draft after Warden ADR 0005 landed at hub `c46f86400732223a6a7c23f5d186250ab4a144eb`.

**Implementation authorization, 6 October 2026:** the user requested creation of the
contracts and Registry implementation in this session. The [Registry v2 bundle](registry-v2/README.md)
records the concrete experiment, schemas and signed vectors. This authorizes bounded local
implementation without representing formal ADR acceptance, publication or qualification.

## Problem, inputs and bounded scope

REG-01 needs signed candidate validation and immutable, tenant-scoped resolution. The
existing [candidate definitions](candidates/README.md) supply manifest shape and hashing
but sign principal assertions, not artifacts. They leave artifact publisher authority,
tenant/owner binding and retained-byte identity unspecified. Implementing those choices
independently in Registry and Gate would create incompatible authority checks.

Inspected hub base: `eaa33e8dfafc53f2874fecaa5b62e69208d45793`; Registry scaffold:
`f2efebac7ed1c86e72264a0d7f2b6110fcce212a`. Candidate bundle:
`5ee201e48a2390b7cf66fdf6aa8750f751f1ec9241e9e04131b6632745612238`.
The current [manifest definition](candidates/foundation.schema.json) lacks a tenant,
owner, publisher, operation identifier, classifications and manifest obligation declaration.
Its sample schema digests are placeholders, not resolvable capability schemas.

The original documentation packet proposed these boundaries. The subsequent implementation
packet adds the separate Registry v2 bundle and its generator/checks in the hub, and the
consumer, tests, vendored contract and documentation in Registry. Work is bounded to one
local REG-01 slice, with no paid environment. Preserve the earlier candidate and its approval
history. Operational trust changes, activation, publication, catalog advancement and
foundation modification remain excluded. Protected workflow changes need specific approval.

## Alternatives and proposed choice

| Question | Alternatives | Proposed choice and consequence |
|---|---|---|
| Artifact signature | Compact JWS; detached signature; general multi-signature envelope | One compact JWS carrying the complete manifest. It makes covered bytes explicit and reuses a standard primitive, while multi-publisher thresholds need a later profile. |
| Tenant binding | Unsigned intake metadata; signed tenant; portable global manifest plus signed tenant endorsement | Tenant in the signed payload. Cross-tenant reuse requires a separately signed version for the receiving tenant; no global digest lookup bypass. |
| Owner binding | Free-text owner; submitter is owner; signed enrolled owner reference | Sign an existing tenant-scoped owner ID and validate publisher-to-owner authorization independently. No ownership or approval authority comes from submitting a string. |
| Immutability | Normalize and replace; identify only by payload digest; retain exact signed artifact | Admit canonical inputs only and retain the exact envelope. Changed bytes under the same tenant/ID/version conflict, including re-signing; key rotation requires a new artifact version. |
| Approval | Treat trusted signature as activation; independent activation binding | A valid publisher signature permits candidate admission only. Activation remains a separate authority path. |

## Proposed signature profile and byte identity

Use compact JWS as specified in [RFC 7515, section 3.1](https://www.rfc-editor.org/rfc/rfc7515#section-3.1).
The proposed protected header has exactly `alg`, `kid` and `typ`: `alg` is `Ed25519`,
`typ` is `munarium-manifest+jws`, and `kid` selects an independently provisioned publisher
key. `Ed25519` is the fully specified JOSE algorithm in
[RFC 9864, section 2.2](https://www.rfc-editor.org/rfc/rfc9864#section-2.2).
These references define the signature primitive; the restrictions below are platform choices.

Header and payload must already equal their `decision-json-v1` canonical UTF-8 bytes.
Verify rather than repair them. Base64url must be unpadded and canonical, with three
nonempty segments separated by two dots. The signing input is the ASCII encoded header
segment, a dot, and the encoded payload segment. Reject other algorithms, extra headers,
remote key references, detached payloads, multiple signatures and principal-token types.
No header or payload may supply a trusted key or select the deployment's trust store.

Proposed limits: decoded protected header at most 512 bytes, decoded payload at most
65,536 bytes, compact envelope at most 90,000 ASCII bytes, signature exactly 64 bytes and
Ed25519 public key exactly 32 bytes. Check encoded bounds before decoding. Apply ADR-0004's
16-container nesting bound, duplicate-key rejection and numeric/Unicode restrictions.
Boundary vectors must test each limit; these bounds are proposed, not measured capacity.

The expanded payload uses `schema_version: 2` and `profile: registry-manifest-v2` to
distinguish it from the existing unsigned version-1 candidate. These names are reservations
within this proposal, not published versions. Let `P` be the admitted canonical payload
bytes and `E` the exact ASCII compact JWS bytes, without a trailing newline:

```text
manifest_digest = "sha256:" + lowercase_hex(SHA256(UTF8("munarium:manifest:v2") || NUL || P))
artifact_digest = "sha256:" + lowercase_hex(SHA256(UTF8("munarium:manifest-artifact:v2") || NUL || E))
```

Here `NUL` is one zero byte. The existing version-1 manifest hash and decision-request hash
are unchanged. A version-aware consumer must select the declared manifest profile; it
must not attempt both domains until one succeeds. Neither digest is a field of `P`.
Requests continue to bind `manifest_digest`; a separately admitted activation binds that
digest to the exact `artifact_digest`, tenant, target/environment and epoch. DEC-04 owns
that activation protocol. A payload digest alone establishes neither signature nor authority.

Registry retains `E` and `P` without reserialization. Resolution returns their exact bytes
and both digests to an authorized reader. If the same `(tenant, id, version)` is submitted
again, identical `E` is an idempotent candidate retry after current authorization checks;
any different `E` conflicts and leaves the original untouched. Noncanonical re-encodings
are invalid before lookup. Canonically different payloads, signatures or header key IDs
never replace the original. Version values are opaque identifiers, not "latest" selectors.

This intentionally makes re-signing require a new version, even for unchanged business
content. A future signature-renewal mechanism needs an explicit decision; it cannot mutate
this profile's immutable record. Publication and replication do not reset identity conflicts.

## Proposed payload and referenced content

The complete payload is a closed object. Retain the candidate manifest's required `id`,
`version`, `capability_id`, `target_id`, `environment`, `credential_audience`, parameter
and result schema digests, `base_consequence`, `modifiers`, `required_inputs`, `effect`,
`idempotency` and `compensation`. Change its schema version as above and add:

| Required field | Proposed meaning |
|---|---|
| `profile` | Exact value `registry-manifest-v2`; unknown profiles refuse. |
| `tenant` | Exact tenant identity verified against the caller context and deployment inventory. |
| `publisher_id` | Tenant-scoped publisher enrolled independently of the submission. |
| `owner_id` | Tenant-scoped enrolled human or organizational owner; an agent identity is insufficient. |
| `operation_id` | Exact operation in the target/connector's admitted operation inventory, not a friendly tool alias or wildcard. |
| `data_classifications` | Nonempty, duplicate-free list of classification IDs from the admitted tenant vocabulary; unknown IDs refuse. No implicit "public" default. |
| `required_obligations` | Duplicate-free list of supported obligation kinds. Initially only `distinct-approval`, or an explicit empty list; unknown kinds refuse. |

New identifiers follow the candidate's bounded ASCII identifier convention: 1–128
characters matching `[a-zA-Z0-9][a-zA-Z0-9:._/-]*`, case-sensitive and without aliases.
Classification and obligation lists each contain at most 32 entries. Every field is required;
no null, ignored extension field or inferred default is permitted. Modifiers only raise the
base class. Owner, operation, classification or audience changes require a new artifact version.

An obligation kind in a manifest declares a minimum requirement, not a satisfied obligation.
Gate adds the actual request/policy digests and eligible approver scope under ADR-0004;
it cannot drop a manifest requirement because policy omitted it. Council verification and
approval remain separate. Selecting an evaluator, classifying actual derived data and
proving that a connector implements the advertised operation remain owning-component work.

Parameter/result schemas must be available as pre-admitted immutable artifacts in the same
tenant, with their expected digest, dialect and supported vocabulary verified. Propose
Draft 2020-12 with a versioned, closed vocabulary and bounded local references; no network
resolution, implicit installation or arbitrary executable validators. Unsupported keywords,
unresolved/cyclic references, mismatched content or unavailable validator refuse admission.
The [Registry v2 profile](registry-v2/README.md#capability-schema-profile) supplies the
exact vocabulary, schema-artifact digest domain, bounds and inventory shapes. Its first
increment rejects all schema references, including local ones, and contains real small
parameter/result schemas. This narrows the local-reference proposal without granting fetch
authority. Formal acceptance must review both the profile and its pinned schema/vector bundle.

## Tenant, publisher and owner authority

Submission carries an independently verified principal/service context following ADR-0003
and Warden ADR-0005. The receiving service verifies the original compact chain on each
operation against current keys, task/policy bounds, registered edges, clock and actual peer.
The Registry v2 profile specifies the local submit/read/list permission adapter. Its host
selects exact registered resources independently; callers cannot supply that policy mapping.
Forwarded attribution never becomes a Registry caller or original-actor authority.
Registry checks permission for candidate submission in that tenant; signature possession
does not confer submission permission. An agent may submit only within that permission.
The manifest tenant must exactly equal the authenticated tenant. There is no "all tenants"
mode, wildcard owner, caller-selected principal or implicit trust across tenants.

Trusted deployment state maps `(tenant, publisher_id, kid)` to one Ed25519 key, its
manifest-signing purpose, current enabled status, allowed owners and allowed target/
environment/operation scope. It also records enrolled owners and supported inventories.
Operators admit this state through a distinct governing path. Intake cannot create or alter
it. Reusing a key value across tenants does not reuse its authorization. Issuer keys for
principal assertions do not gain manifest-signing purpose by sharing an algorithm.

Before admitting a candidate, require a current, available trust snapshot; verify the
signature, publisher scope, enrolled owner, target bindings and referenced content against
that snapshot. An owner field is a signed responsibility claim whose admissibility is
checked against the enrolled owner and allowed publisher mapping; it is not the owner's
approval. Pin the trust/inventory revisions in the admission receipt. An implementation
must reject/retry if those revisions change before admission commits rather than recording
authorization checked against superseded state. Missing, disabled, revoked, ambiguous or
unavailable trust refuses. This proposal does not implement publisher enrollment or rotation.

REG-01 has no offline trust cache: each admission, retry and verified candidate resolution
requires current trust/owner state. A trust-state outage refuses those operations. Revocation
does not delete historical bytes; a later, separately authorized historical-evidence API may
return them with explicit unverified/retired status, never a successful current verification.
REG-03 must specify bounded caching before any consumer caches a successful verification.
No self-reported signing timestamp grants validity after revocation.

Resolve and list are separately authorized read operations scoped to the verified tenant.
Authorize before inspecting another tenant's keys, identities or conflict state. A foreign
artifact is indistinguishable from an absent artifact to that reader; error details and
pagination/counts cannot disclose foreign inventory. Internal audit detail stays within its
authorized tenant. This does not assert constant-time storage or eliminate all side channels.

## Candidate admission and activation remain distinct

Intake validates fully before inserting an inert record. It cannot write an effective
pointer, epoch or revocation state, and its dependencies must expose no activation writer.
Read interfaces cannot mutate either store. Admission returns candidate identity, both
digests and checked trust/inventory revisions; it returns no activation epoch, approval,
grant or executable permission. Submitter-supplied `active` fields are invalid.

Gate must distinguish candidate inspection from evaluation using an active binding. The
first isolated REG-01 tests may compare an explicitly empty effective view before and after
intake; they cannot claim the integrated activation path exists. Stage 1's admitted initial
catalog must come from the separately authorized bootstrap path under DEC-01/S1, never an
intake shortcut. DEC-04 governs later Council activation, compare-and-set and recovery.
Consumers retain digest, epoch and revocation context when caching eventually becomes supported.

Same-identity insertion must be atomic in the selected storage boundary. A component-local
in-memory prototype can test sequential conflicts and admission failures; it cannot qualify
durable races or crash recovery. Storage/acknowledgement uncertainty is not a permission to
retry with changed bytes or report successful activation. REG-02 owns persistence evidence.

## Required evidence and acceptance disposition

The table specifies acceptance requirements. [Registry v2](registry-v2/README.md) now supplies
32 fixed signed-artifact cases and an independent OpenSSL checker; Registry adds component
state and failure tests. These checks do not establish integrated activation or identity.
The earlier candidate remains unchanged.
Use fictional tenants and test-only signing material; retain only public verification keys
and signed messages in fixtures. Do not generate or replace operational signing keys.

| Case | Required observation |
|---|---|
| Valid signed candidate and identical retry | Exact original envelope/payload and both digests resolve; retry returns the same candidate; effective view remains unchanged. |
| Changed identity content | Changed payload, owner, signature or `kid` under the same tenant/ID/version conflicts; original bytes remain readable while currently authorized. |
| Signature failures | Unsigned, corrupt, wrong key/purpose/type, unsupported algorithm and extra/remote-key header refuse; principal JWS is never a manifest. |
| Encoding and limits | Duplicate decoded keys, noncanonical JSON/base64url, malformed Unicode, trailing bytes and size/depth boundary violations refuse without repair. |
| Tenant isolation | Shared raw key or identical IDs across two tenants do not authorize cross-tenant submit/resolve/list; counts and refusal details reveal no foreign inventory. |
| Owner/publisher trust | Unknown owner, forbidden publisher-owner pair, wrong target/environment/operation, disabled key, stale revision and unavailable trust refuse. |
| Complete semantics | Missing classification/obligation/operation, unknown vocabulary, lowering modifier, substituted schema and unsupported schema keyword refuse. |
| Version compatibility | Old unsigned candidate and unknown profile refuse under v2; request and manifest hash domains are never interchanged. |
| Revocation and retries | Previously admitted bytes persist but revoked trust prevents current verified resolution and admission retry. |
| Authority separation | Agent submission and forged active metadata cannot change effective pointers; Gate refuses a candidate without its independently admitted active binding. |

Acceptance requires machine-readable closed shapes for every new record/reference, fixed
positive and negative signed vectors, exact byte/digest agreement from independent consumer
implementations, reviewed trust provisioning and revocation assumptions, and a maintainer
disposition naming the exact reviewed revision/date and bundle digest. The candidate-lock
check for the existing bundle is preservation evidence only, not evidence for this proposal.
Schema/fixture review and adversarial analysis do not substitute for accountable acceptance.

## Compatibility and component handoff

| Consumer | Required change after acceptance |
|---|---|
| Registry / REG-01 | Implement the accepted validator, inert storage, exact lookup and tenant-safe listing; pin contract/vector digests; retain failure evidence. |
| Gate | Verify the declared manifest profile and exact active artifact binding; carry manifest-required obligations and refuse missing references/trust. |
| Harness | Produce canonical signed-artifact submissions through authorized tooling; agent clients need no publisher private key; distinguish candidate receipts from authority. |
| Warden | Supply the accepted verified caller context and tenant-scoped permissions; do not conflate publisher keys with principal issuers. |
| Council / Server | Consume exact artifact/content bindings in later approved activation and event records; preserve historical artifacts without reactivating them. |

Expand by adding a new candidate bundle alongside the current one, with a new lock and
explicit supported profiles. Migrate consumers and their request/event vectors to the new
manifest digests and record the exact composition. Remove obsolete profiles only through
the accepted version policy. Do not edit old vectors to make the new implementation pass,
reinterpret their v1 hashes as v2, or infer compatibility from matching package numbers.
No currently released runtime claims support for either candidate.

REG-01's local candidate implementation is authorized; formal acceptance remains pending.
Shared HUB-01/02,
the S1 foundation gate and S2–S4 integration requirements in the
[build plan](../build-plan.md#dependency-sequence-and-exit-evidence) remain independent
prerequisites. This record closes no evidence gap by declaration and grants no release or
activation authority.
