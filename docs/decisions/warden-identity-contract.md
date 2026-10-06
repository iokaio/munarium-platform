# Proposed Warden identity contract

**Draft for maintainer acceptance, 6 October 2026; no published contract version.**
This is the WARDEN-01 consumer specification for [ADR 0003](0003-bootstrap-principal-context.md)
and the identity portion of [ADR 0004](0004-decision-only-contracts.md). It makes the
existing candidate's verification boundary explicit for Warden and its consumers.
It does not accept those ADRs, select a provider or enable a runtime.

## Inputs and ownership

The review base is hub `eaa33e8dfafc53f2874fecaa5b62e69208d45793` and Warden
`b404e150001fa3656a80498e206c2e4df3b9a1a6`. The [candidate lock](candidates/candidate-lock.json)
declares bundle SHA-256 `5ee201e48a2390b7cf66fdf6aa8750f751f1ec9241e9e04131b6632745612238`.
The [principal schema](candidates/foundation.schema.json) at `#/$defs/principal`,
[signed vectors](candidates/identity-vectors.json) and
[canonical JSON definition](0004-decision-only-contracts.md#canonical-requests-and-candidate-artifacts)
are the concrete review inputs. This proposal preserves their bytes and expected outcomes.

The founder is the accountable acceptance authority under [GOVERNANCE](../../GOVERNANCE.md).
Warden owns upstream identity verification and issuance/attenuation of platform assertions;
Server, Gate, Registry and later Council/Gateway verify assertions at their own boundaries.
No component accepts an actor array merely because another request calls it verified.
The first implementation is decision-only: grants, bootstrap transitions, ratification,
credential brokering and consequential execution remain unavailable.

## Assertion bytes

Each assertion is a compact JWS with exactly three nonempty ASCII segments separated
by two periods: protected header, payload and signature. Every segment uses canonical,
unpadded base64url. The candidate JSON files split these into `protected`, `payload`
and `signature` for inspection; that fixture object is not a new HTTP API.

The decoded protected header has exactly `alg`, `kid`, `typ`: `alg` is `Ed25519`,
`typ` is `munarium-principal+jws`, and `kid` selects only an independently provisioned
issuer key. Unknown keys, retired keys, `EdDSA`, extra headers and request-selected
key URLs refuse. The fully specified algorithm and signing input follow the references
in the [candidate profile](candidates/README.md#concrete-proposed-profile-choices).
Public keys are 32 bytes and signatures 64 bytes; an established verification library
must verify the ASCII `protected.payload` signing input.

Both decoded JSON objects must already equal their `decision-json-v1` canonical bytes.
Reject ambiguous JSON, unknown fields and unsupported versions. Do not normalize,
fill defaults, discard unknown fields or reserialize a payload to rescue its signature.
The shared canonical profile's size and nesting limits apply to each decoded JSON input;
the transport's aggregate request/chain byte bound still needs an accepted profile pin.

The principal digest is `sha256:` plus the lowercase SHA-256 of the **complete compact
JWS bytes**, including its signature. It is not the request hash, a payload-only hash
or the digest of the fixture JSON object. A parent reference uses this exact digest.

## Principal fields

All fields below are required; the schema rejects additional properties. Null is allowed
only where the schema explicitly permits it. Identifier, integer and collection limits
come from the pinned schema, not independently chosen component constants.

| Fields | Required interpretation |
|---|---|
| `schema_version` | Exactly `1` within this candidate; no default or coercion. |
| `deployment`, `tenant`, `audience` | Match independently trusted deployment, tenant and receiving service for every chain member. |
| `issuer` | Match the configured issuer of the verified key. The key must permit the assertion's purpose. |
| `origin`, `origin_kind` | Immutable initiating identity; kind is `human`, `agent` or `service`, authenticated by the issuer's admitted mapping. |
| `actor` | Current actor; root actor equals origin, later actors cannot repeat. |
| `service` | At the leaf, equal the authenticated transport peer's registered service identity. Network location is not identity. |
| `purpose` | `decision` for WARDEN-01. The shared schema also models `bootstrap` for Server's separately authorized transition path. |
| `scopes`, `resources` | Nonempty unique sets represented as arrays. Resources are exact identifiers, with no wildcard or inferred hierarchy. |
| `iat`, `nbf`, `exp` | Nonnegative integer UTC seconds, constrained by the validity and attenuation rules below. |
| `parent_digest` | Null at the root; otherwise the immediately preceding complete compact assertion's digest. |
| `bootstrap` | Null for decision assertions. The bootstrap object cannot authorize a Warden decision or be silently ignored. |

Origin identity and service identity serve different purposes. In particular, `service`
does not make an agent-originated chain a service-originated or human-originated chain.
Provider subject IDs and token claims need an admitted mapping to these fields before
Warden issues a root. [ADR 0005](0005-warden-identity-admission.md) proposes the explicit
nonhuman mapping, per-edge registration and forwarding boundaries with separate review
schemas/vectors. Those additions remain unaccepted.

## Trusted verification inputs

Callers supply evidence, never the verification policy. Deployment configuration and
authenticated service context must independently supply:

- expected deployment, tenant, audience and actual peer service;
- issuer/key bindings, allowed purposes, current retirement/authority availability and
  restore-quarantine state;
- a clock and its qualified uncertainty bound;
- registered delegation transitions, task scope and target-policy restrictions for
  the provider/issuance path.

The oracle's `context` and `keys` objects represent these trusted inputs only in tests.
They must not be accepted as request-controlled state by a runtime. Their custody,
freshness, authorized update path and outage behavior require the deployment profile.
Enrolled human/bootstrap state belongs to Server's bootstrap tests, not a way to
upgrade decision authority. Absent, ambiguous, unsupported or unverifiable required
inputs refuse; they never select a permissive default.

## Verification and attenuation

Verify an ordered root-to-leaf chain containing one through five assertions, at most
four delegation edges. Every assertion must pass schema, signature, issuer/purpose,
deployment/tenant/audience, current-key and time checks. Refuse if required authority
state is unavailable or the context is restore-quarantined. WARDEN-01 admits only
decision-purpose chains; a general bootstrap verifier's successful result is not
a decision assertion.

For the candidate two-second uncertainty bound, require
`iat <= nbf <= now - 2` and `now + 2 < exp`. A decision assertion has
`exp - iat <= 60`. There is no additional expiry grace. Check every ancestor's
validity too. These are proposed conservative bounds, not measured synchronization.

At the root require null parent and actor equal to origin. At each child:

1. Verify the immediate parent digest, preserve origin, origin kind and purpose, and
   reject any repeated actor.
2. Require child scopes/resources to be subsets of its parent's sets and child
   validity interval to stay within its parent's: `nbf` cannot decrease and `exp`
   cannot increase. A presented widened chain refuses; do not silently trim it.
3. Reject `govern` or `ratify` in any delegated assertion, or any assertion whose
   origin kind is `agent`. A human-looking actor does not change this check.

For issuance, effective authority is the intersection of originating authority,
every allowed actor transition, registered task and target policy. An upstream
signature proves neither registration nor entitlement. A narrow valid assertion
can still fail task/policy admission. Provider and registration adapters must supply
the accepted bindings before issuance; the fixture oracle does not establish them.

Check the leaf's service against the actual authenticated peer before returning
a verified result. Do not reuse a previous hop's verification result at a new
audience or peer boundary. A proposal to reissue for another audience must preserve
verified origin and attenuation under a separately specified issuance procedure.
ADR 0005 refuses audience exchange in the initial profile and instead specifies
separately authenticated service calls carrying attribution without original-actor authority.

## Output and consumer obligations

Successful verification returns the exact validated leaf principal and its compact
assertion digest, with the verified ancestry retained for evidence. Public output
must not contain upstream bearer credentials, private keys or target credentials.
Refusal returns no verified principal; externally visible diagnostics must not echo
raw identity evidence. A common refusal wire vocabulary remains a transport decision;
the oracle's Python exception strings are not public error codes.

Gate/Harness bind a proposal's `principal_digest` to that verified leaf digest.
Consumers recheck tenant and current receiving-service/peer context; a hash alone
does not authenticate its referenced principal. Server records the verified origin
without manufacturing a human identity. A valid principal permits only identity
admission; policy evaluation and durable authority checks still decide the operation.
This reusable, time-bounded decision assertion is not a single-use execution grant.

## Evidence and remaining acceptance work

The existing 32 signed cases cover valid/forged/delegated/retired-key inputs.
[Consumer-boundary tests](../../scripts/test_warden_identity_contract.py) additionally
assert the exact narrowed output, absence of invented human attribution, decision-path
context substitution, ancestor omission/reordering, signature absence, current-key
retirement and both sides of the clock boundaries using unchanged signed candidates.
The preparation review also adds malformed/noncanonical base64url, duplicate/noncanonical
JSON, invalid signature-size and exact leaf-digest checks. These refuse malformed JSON
before attempting cryptographic verification; signed positive cases still use OpenSSL.
They exercise an offline OpenSSL-backed oracle, not a Warden runtime or provider.

Reproduce with `py -m unittest discover -s scripts -p "test_*.py"` from the hub root.
Missing OpenSSL is a failure; no signing or fixture regeneration is required.
The suite also validates the existing candidate bundle digests. The review record
must retain command output, exit status, tool versions and any failures/unavailable checks.

Initial run on 6 October 2026: Python 3.13.12 and OpenSSL 3.2.4 on Windows passed
`py -m unittest discover -s scripts -p "test_*.py" -v`, exit 0: 48 test methods,
including eight added consumer checks and the existing 32 signed cases, with no
skips. The license, private-material, documentation and gitleaks 8.30.1 directory
checks and `git diff --check` each exited 0. Output is retained in the task
transcript. This is local candidate evidence; hosted CI and runtime integration
were not run. Temporary test directories were scoped by the existing test tools;
no provider, service, persistent key or deployment was created.

The subsequent [ADR 0005 review](0005-warden-identity-admission.md#local-review-results)
records the expanded 58-method suite, including 13 assertion-consumer methods, its
separate admission-vector checks, independent schema comparison and corrected lock
generation failure. It supersedes the initial test count without changing the signed corpus.

Acceptance still needs an explicit maintainer disposition of this document and
ADRs 0003/0004 at an exact revision, plus ADR 0001 disposition. Before runtime intake,
pin the published contract/vector bundle, choose/review the verification library
and disposable provider, accept the proposed ADR 0005 mapping/registration/forwarding
rules and aggregate bounds, and assign owner/reviewer and time/spend ceiling.
S1 and the relevant S2–S4 foundation evidence remain integration gates. No check here
closes provider custody, authenticated topology or foundation qualification.

## Alternatives and compatibility

Keeping only associated Rust types leaves consumers without byte-level agreement;
this contract makes the existing hub candidate the common review target. Treating
unsigned actor lists or caller-supplied verification context as identity fails the
required trust boundary. Copying the fixture oracle into Warden would replace library
and provider qualification with test infrastructure and is excluded.

There is no existing released principal contract to migrate. After acceptance,
publish through the maintainer-controlled contract process and pin the same digest
in each consumer. Do not reinterpret Server's legacy capability tokens as these
assertions. Later semantic/schema changes follow expand, migrate, remove with a
new contract version and reviewed vectors; changing this draft does not silently
change a deployed trust profile. Consumers may narrow admission but not redefine
the signed bytes, identity meanings, request binding or attenuation rules.
