# 0008: Stage 1 service and authority boundary

**Implementation directed, 6 October 2026; acceptance evidence pending.** This
extends [0007](0007-stage1-composition.md) with the durable authority and service
boundary required to replace its in-process composition. Existing candidate
bundles and golden vectors remain immutable.

## Authority and compatibility

Server has explicit legacy and platform profiles. Existing clients and legacy
deployments retain their behavior. A platform deployment does not interpret an
ordinary write or management token as governance authority. Its separate authority
store persists enrollment, governing bindings, bootstrap retirement and immutable
receipts. The authority revision and nonce consumption commit in the same transaction.
Concurrent transitions serialize per tenant; exact retries return the original receipt.

The operator provisions the deployment, tenant, audience, enrolled non-agent
subjects and initial Ed25519 public keys outside request handling. A signed
transition binds the complete artifact digest, nonce, expected revision/head,
epoch and bounded validity interval. No delegation chain can authorize bootstrap.
Retirement installs successor authority atomically and cannot be reversed through
the public API. A separately retained authority checkpoint fences restored state;
an unavailable or inconsistent checkpoint refuses authority operations.

Legacy governing mutations are inventoried and refused in the platform profile
unless they use its authority transaction. This includes indirect shape/runbook
application and index cutover, not only endpoints named governance. The platform
profile must not expose an alternative ordinary-writer path to its authority,
event records or replay archives. Required ordinary data operations retain tenant
and stored-policy enforcement. REST and direct gRPC share admission and effects.

## Service boundary

Harness, Gate, Registry, Warden and Server use separate authenticated process
identities. Receiving services derive peer identity from mTLS, then verify signed
principal assertions against current, independently selected tenant authority.
Caller-supplied service labels and proxy headers are not authentication. Warden
maps verified provider subjects through explicit operator enrollment; it never
accepts self-reported human authority. Every hop has a recipient-bound assertion.

The initial upstream adapter accepts bounded Ed25519-signed workload JWTs with
`alg=EdDSA`, `typ=at+jwt`, a locally enrolled key ID, and exact issuer, subject and
single audience. Required `iat`, `nbf`, and `exp` use the same conservative clock
window as principal admission. This narrow profile requires canonical JSON and
has no discovery, token exchange, email mapping or human login. Provider keys and
registered subject kinds are independent of Warden's assertion-signing key.
Issuance starts at the current time; callers wait for the two-second uncertainty
window instead of receiving backdated assertions. Revocation and task/policy
changes take effect through fresh governing snapshots on every admission.

Governing `identity:<recipient-service>` bindings contain enrolled assertion `keys`,
per-presenter `peers` (current task and policy digest, interval, scopes, resources,
and maximum depth), and ADR-0005 `registrations`. The receiver selects its own
recipient name and its actual peer; callers supply only signed evidence. Warden's
identity-only export owns the shared policy adapter and verification source.
Server's authenticated authority reads are the control-plane bootstrap discovery
exception: they require an explicitly enrolled mTLS reader, without depending on
an assertion that Warden cannot issue until that read succeeds. They do not grant
record, issuance, evaluation or governance rights. Those operations separately
verify their live provider/principal evidence.

Registry persists immutable candidate bytes and never activates submissions.
Gate obtains current bindings and authoritative lineage from authenticated
services, evaluates with the pinned bounded evaluator, and records decisions
before returning success. Lookup/replay authenticate independently and never
dispatch. Harness clients retain operation identity and recover ambiguous results
through lookup. No connector, broker or target credential is part of Stage 1.

## Required evidence

Exercise the B01–B12 authority cases against memory and PostgreSQL, including
concurrency, restart, retirement and restore fencing. Run separate-process mTLS
integration with wrong-peer, wrong-tenant, invalid-provider, stale/revoked identity,
unavailable-authority, malformed-manifest, missing-lineage and recording-failure
controls. Compare REST/gRPC decisions and affected clients, preserving existing
client compatibility. Record actual commands and failed attempts. Implementation
status changes require this evidence; acceptance and independent review are not
inferred from passing component tests.
