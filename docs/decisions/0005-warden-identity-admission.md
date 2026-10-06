# 0005: Warden identity mapping, delegation registration and forwarding

**Proposed for maintainer review, 6 October 2026; not accepted or released.**
Scope: the missing WARDEN-01 admission definitions under DEC-01 and minimum DEC-07.
Depends on [0003](0003-bootstrap-principal-context.md),
[0004](0004-decision-only-contracts.md) and the
[assertion contract](warden-identity-contract.md). The founder is the acceptance owner.
Consumers are Warden, Registry, Gate, Harness and Server. No runtime is supplied.

## Review packet and bounds

Base: hub `eaa33e8dfafc53f2874fecaa5b62e69208d45793`, Warden
`b404e150001fa3656a80498e206c2e4df3b9a1a6`. This packet adds three proposed record
shapes, fictional examples and offline checks. It preserves the existing foundation
schema, signed vectors, candidate lock and oracle. Existing signatures cannot be
regenerated to make a new rule pass. The new records are separate review candidates;
their presence is not admission into any deployment's governing state.

The [schema](candidates/warden-admission.schema.json) defines `provider_binding`,
`delegation_registration` and `forwarded_attribution`. All named properties are
required, additional properties refuse, and null/default/type coercion is forbidden.
The [vectors](candidates/warden-admission-vectors.json) supply trusted fictional
contexts separately from the records under examination. They never authenticate
themselves. The [offline tests](../../scripts/test_warden_admission.py) exercise the
schema and semantic refusal cases without a provider, network, signing key or runtime.

## 1. Provider identity mapping

The initial profile accepts **registered service or agent origins only**, for
decision work. Human login, bootstrap, impersonation and ratification are unavailable.
A workload must never acquire a human origin through a label, email or actor claim.
This narrows admission; it does not redefine the shared principal schema's human kind.

The provider adapter must first verify its protocol's issuer, audience, signature,
time bounds and workload identity using an established library. An opaque in-process
verified result supplies `issuer`, `subject`, `subject_kind`, `audience`, `nbf`, `exp`.
These are **adapter facts**, not an accepted JSON request or a caller's `verified` flag.
`subject_kind` comes from authenticated provider enrollment and deployment mapping,
not a token's self-reported human/agent role. Unsupported or ambiguous identity refuses.

For OIDC identities, preserve the exact issuer/subject pair; do not use an email or
display name as the identifier. This follows the identifier distinction in
[OpenID Connect Core section 5.7](https://openid.net/specs/openid-connect-core-1_0-errata2.html#ClaimStability).
It does not prescribe an OIDC ID token as a workload API credential. The selected
provider adapter still needs its token type and enrollment semantics qualified.

Select exactly one currently admitted `provider_binding` by trusted deployment,
tenant, verified provider issuer and subject. Zero or multiple matches refuse, even
if duplicate records would produce the same origin. Strings compare exactly; no
case folding, URL rewriting, Unicode normalization, prefix match or account fallback.
The binding's subject kind must equal the verified kind and its `peer_service` must
equal the authenticated requester. The upstream token audience must be Warden's
configured upstream audience; the requested downstream audience must be listed in
the binding. The upstream issuer and the platform assertion issuer are distinct.

| Binding fields | Meaning |
|---|---|
| `schema_version`, `binding_id` | Version 1 and immutable registration identifier within the admitted snapshot. |
| `deployment`, `tenant` | Trusted installation/tenant partition; no cross-tenant matching. |
| `provider_issuer`, `provider_subject`, `origin_kind` | Exact verified upstream identity and its admitted nonhuman kind. |
| `origin`, `peer_service` | Registered platform origin and permitted authenticated requester. Root actor equals origin. |
| `audiences`, `scopes`, `resources` | Explicit downstream audiences and exact authority caps; no wildcards. |
| `nbf`, `exp` | Registration validity, independently checked with the two-second uncertainty bound. |

For root admission, requested scopes/resources must be nonempty subsets of the
intersection of binding, registered task and target policy. Refuse a wider request
or an empty intersection. Task and policy come from the independently selected
admitted snapshot for this operation, not caller-provided records. Refuse unavailable
or stale required state. All upstream/binding/task/policy intervals must be current.
Assertion issuance may never outlive any of them or the assertion profile's 60 seconds.
Its issuance/not-before timestamps must respect the existing two-second validity rule;
do not backdate an assertion to make it immediately valid.

Successful mapping returns registered origin/kind, actor equal to origin, authenticated
service, and the requested bounded scopes/resources. It returns no provider token,
signing key or target credential. The candidate tests verify this mapping from assumed
verified adapter facts; they do not establish that a provider supplied those facts.

## 2. Delegation registration

Signature validation and decreasing scopes are necessary but insufficient. Every
edge also needs one current admitted `delegation_registration` matching the verified
parent and child under the same trusted operation context.

| Registration fields | Meaning |
|---|---|
| `schema_version`, `registration_id` | Version 1 and immutable registration identifier. |
| `deployment`, `tenant`, `origin`, `origin_kind` | Exact preserved chain origin and partition. |
| `from_actor`, `to_actor` | The permitted adjacent actors; no wildcard transitions or repeated actor. |
| `presenter_service`, `audience` | Registered child service and receiving service; the leaf service must also match the actual peer. |
| `task_digest`, `policy_digest` | Exact independently selected task/policy revision references, never request-selected authority. |
| `scopes`, `resources` | Additional caps on child authority, alongside every ancestor, task and policy. |
| `max_depth` | Maximum total chain depth allowed by this registration, from one through four edges. |
| `nbf`, `exp` | Current registration interval; the child interval must fit inside it. |

Run the existing complete-chain signature/identity checks first. For each edge,
require exactly one matching registration, matching task/policy references, current
validity, and child scopes/resources and interval contained within registration,
task and policy. Reject duplicate registration IDs and ambiguous matching records.
Total depth must fit both Registry's current task limit and every edge registration,
as well as the four-edge assertion ceiling. Missing registrations, retired snapshots
or unavailable lookups refuse. No state supplied alongside an assertion can declare
itself current or admitted.

The successful verification evidence retains the complete assertion digest and ordered
registration IDs with the trusted snapshot, task and policy references. These are
admission evidence associated with the exact verified chain; they are not new unsigned
authority fields on the JWS. This proposes how ADR 0003's delegation-ID requirement
is represented without silently changing the existing signed principal schema.
The runtime evidence transport/custody must bind them to that chain and its recipient.

Root service-to-agent delegation preserves a service origin; agent-to-agent delegation
preserves an agent origin. Neither can become human, `govern` or `ratify`. A registration
cannot make a widened or invalidly signed chain acceptable. Changes to an admitted
registration remain a separately authorized governing operation, unavailable here.

## 3. Cross-service forwarding

The initial profile **does not exchange or retarget an assertion**. Every assertion
in a presented chain must name the current receiving service; its leaf must match
the actual transport peer. Forwarding a Harness-to-Gate assertion on a Gate-to-Server
connection therefore cannot authenticate Harness at Server. Changing its audience,
service, origin or parent bytes invalidates it; constructing a new root would lose
ancestry and is not an allowed workaround.

Instead, Gate authenticates to Server/Registry using its separately registered service
identity and recipient-bound assertion. It may carry a `forwarded_attribution` record
inside an authenticated, integrity-protected request or authoritative event:

| Attribution fields | Meaning |
|---|---|
| `schema_version`, `purpose` | Version 1, purpose exactly `attribution-only`. |
| `deployment`, `tenant` | Same trusted partition as both the sender and recorded operation. |
| `sender_service`, `recipient_service` | Actual authenticated sender and receiving service. |
| `principal_digest`, `request_digest` | Original verified leaf assertion and exact original request references. |

The receiver must independently admit the sender for this operation and bind both
digests to the exact verified operation/evidence context. Unknown references, tenant
substitution, peer substitution, changed request or missing authenticated evidence
refuse. Attribution grants **no** authority: the caller remains the sending service.
An API requiring the original actor's live authority must refuse this record and wait
for a separately accepted exchange protocol. It must not fall back to service authority.

Original evidence is retained through the authoritative record's access controls; it
is not copied into arbitrary request headers or logs. An attributed human or agent in
an event is not an authenticated caller of the receiving service. No backend trusts
forwarded headers merely because traffic came through a proxy or loopback network.

[RFC 8693](https://www.rfc-editor.org/rfc/rfc8693.html#section-1.1) distinguishes
delegation from impersonation. This candidate deliberately does not implement token
exchange: audience retargeting with lineage preservation needs a separate reviewed
protocol and signed vectors. Explicit refusal keeps that unsupported path bounded.

## Transport limits and error boundary

Propose a 65536-byte UTF-8 body ceiling, 16-container nesting ceiling, no compression
or remote references, and at most five compact assertions per identity presentation.
Apply the body limit before JSON/base64 decoding, then the existing canonical profile
and per-record schema. A component may admit less. Fragmenting a chain across requests
does not bypass the limit. These are design bounds, not measured capacity.

Malformed/oversize input, failed verification, ambiguous registration, absent required
state and unsupported forwarding all return refusal with no verified principal or
authority. External errors must not expose raw evidence, upstream subjects or tokens.
Endpoint/status-code selection remains component transport design; test-oracle exception
strings are not public error codes. No listener or wire service is supplied here.

## Evidence, alternatives and acceptance

The vectors cover service-origin mapping, exact issuer/subject and tenant binding,
ambiguous mappings, task/policy narrowing, permitted delegation, missing/expired or
mismatched registrations, depth limits, and attribution without authority. They reuse
`valid-delegation` from the unchanged signed corpus for edge checks. Service mapping
and attribution fixtures are semantic examples, not newly signed identity evidence.

Automatic mapping from an email or display name would conflate identity and labels.
Accepting any decreasing signed chain would omit registration. Retargeting an existing
assertion would contradict the current audience/parent bindings. This proposal chooses
explicit enrollment, per-edge admission and refusal of unsupported authority forwarding.

Acceptance must pin this ADR, schema/vector digests and test output with ADRs 0003/0004.
The additive review bundle is not included in the existing foundation lock; neither
bundle is published. Consumers must not mix unreviewed revisions. After acceptance,
the maintainer-controlled contract publication supplies the combined versioned bundle.
Future changes follow expand, migrate, remove; no legacy Server token changes meaning.

Before WARDEN-01 runtime work, select and pin the provider/library, qualify the adapter
facts and registration lookup/evidence custody, confirm foundation prerequisites, and
assign the bounded implementation/review allocation. Signed service-origin integration,
mTLS isolation and actual provider outages remain component tests. Human authentication,
audience exchange, grants, broker, revocation propagation and activation stay outside
this packet. The proposal creates none of those capabilities or governing resources.

## Local review results

On 6 October 2026, Python 3.13.12 and OpenSSL 3.2.4 on Windows ran
`py -m unittest discover -s scripts -p "test_*.py" -v`: exit 0, 58 test methods,
including 45 admission cases within the vector test and 13 assertion-consumer methods.
No tests were skipped. The original signed cases and foundation digest checks passed.
This is offline candidate evidence, not Warden or provider conformance.

The initial expanded run exited 1 because the new lock producer concatenated filenames
in insertion order. Correcting it to ordinal filename order fixed the new bundle;
the expected hashing rule, existing lock and signed fixtures were unchanged.
The passing additive digest is
`9ed4a12563d064e5d2068658b903a8b8813ffe49e8cd66356931af1447080283`, recorded in the
[separate lock](candidates/warden-admission-lock.json).

`py scripts/check_warden_admission_jsonschema.py` with installed `jsonschema` 4.26.0
exited 0: Draft 2020-12 meta-validation and 48 independent shape comparisons agreed.
That optional check is separate from CI's standard-library unittest discovery.
`py check_license.py`, `py scripts/private_material_scan.py`,
`py scripts/docs_linkcheck.py`, `gitleaks dir . --config .gitleaks.toml --no-banner --redact --exit-code 1`
and `git diff --check` each exited 0. Full command output, including the initial
failure, is retained in the task transcript. No runtime check or hosted CI was run.
