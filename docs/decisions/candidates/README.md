# Foundation contract candidate fixtures

**Proposed, not accepted or released.** These are review inputs to
[ADR 0003](../0003-bootstrap-principal-context.md) and
[ADR 0004](../0004-decision-only-contracts.md), based on hub revision
`767e4613d9e18a3ae9f93b7f49f983b6aaeee664`. They are not activated policy,
a deployed verifier, a published contract version or an S1–S4 qualification.
Runtime implementations remain in their owning repositories after accepted definitions.

## Review artifacts

| Artifact | Meaning |
|---|---|
| [foundation.schema.json](foundation.schema.json) | Draft 2020-12 definitions for principal/bootstrap, requests, manifests, lineage, decisions, Stage 1 events, refusals and acknowledgements |
| [identity-vectors.json](identity-vectors.json) | Public verification keys, signed fictional messages, trusted fixture state and expected acceptance/refusal |
| [record-vectors.json](record-vectors.json) | Positive record shapes; tests derive reproducible missing-field, extra-field and cross-record negative cases |
| [candidate-lock.json](candidate-lock.json) | Exact data-file digests and aggregate candidate digest; no release or signature claim |
| [warden-admission.schema.json](warden-admission.schema.json) | Separate proposed ADR 0005 record shapes for provider bindings, delegation registrations and forwarding |
| [warden-admission-vectors.json](warden-admission-vectors.json) | Fictional trusted contexts and acceptance/refusal cases for those records |
| [warden-admission-lock.json](warden-admission-lock.json) | Separate additive candidate digest, bound to the existing foundation candidate |

The Warden admission candidates belong to [ADR 0005](../0005-warden-identity-admission.md).
They do not change the existing foundation schema, signed vectors or their lock.
Their vector format stores one base per operation, dot-path replacements in `changes`,
and an optional `duplicate` naming a list whose first record is copied in memory.
Each case declares `accept` or `reject`; acceptance compares the exact base `expected`
result. Task/policy/request digest strings are fictional references supplied by a trusted
test context, not proofs of retrieved artifacts. A runtime must resolve and verify the
actual admitted records. The [admission oracle](../../../scripts/test_warden_admission.py)
checks semantic examples and closed schemas; only its delegation cases use the original
signed chain. It does not verify a real upstream provider or authenticated transport.
Run the optional independent schema comparison with
`py scripts/check_warden_admission_jsonschema.py` from the hub root when `jsonschema`
is installed. The regular unittest suite remains dependency-free apart from its existing
OpenSSL tool requirement. The additive lock uses the same LF-normalized file hashes
and ordinal filename ordering as the foundation candidate lock.

All named fields are required and top-level records reject unknown properties. Explicit null
means unavailable for nullable lineage bindings; it is never converted to verified trust.
Parameters remain capability-schema-owned objects, subject to `decision-json-v1` limits.
The manifest pins parameter/result schemas; these fixtures do not evaluate arbitrary
capability schemas or policy predicates. Manifest candidates have no caller-supplied active
flag. Activation is a separate admitted binding, not a property the schema can prove.

Schemas check shape. The [offline oracle](../../../scripts/candidate_contract.py) also checks
upward-only consequence modifiers, complete verified-lineage bindings, tenant agreement,
approval/request/policy bindings, event payload-kind agreement, predecessor presence,
payload integrity and acknowledgement identity. An allow or approval-required result cannot
carry unknown/untrusted lineage. Even complete verified metadata does not prove that a
source/field/derivation is authoritative: that requires independently verified evidence and
the admitted manifest/policy. No shape validator is a substitute for that runtime check.

## Concrete proposed profile choices

JWS uses protected `alg=Ed25519`, `typ=munarium-principal+jws` and a provisioned `kid`.
The fully specified algorithm name follows
[RFC 9864](https://www.rfc-editor.org/rfc/rfc9864.html); `EdDSA`, extra headers, remote key
URLs and unknown keys refuse. The signature covers the ordinary ASCII JWS signing input
`base64url(protected) + "." + base64url(payload)`. Each JSON component must already equal
its `decision-json-v1` canonical bytes. Base64url is unpadded and canonical. A principal
digest is SHA-256 of the complete compact JWS bytes, including the signature, prefixed
`sha256:`. JSON fixtures store its three parts separately for readable public test material.
Only public keys and signatures are retained; no private signing key enters the tree.

Epoch times are nonnegative integer UTC seconds. Maximum lifetime is 300 seconds for
bootstrap and 60 seconds for decision assertions. The proposed clock uncertainty is two
seconds: require `iat <= nbf <= now - 2` and `now + 2 < exp`; no extra grace period is
allowed. Governance additionally requires current authority/retirement state. Unknown
authority or restore quarantine refuses. These conservative bounds are review choices,
not measured clock synchronization or a service-level guarantee.

Trusted fixture state supplies deployment, tenant, audience, authenticated peer service,
issuer keys/purposes, enrolled human identities, current bootstrap transition and retirement
state. A token cannot select those values. Each chain member is issuer-verified; root actor
equals origin, and origin/kind/purpose stay fixed. Each child pins its parent's complete
token digest and narrows resources, scopes and time. Exact resource identifiers are used;
there is no wildcard hierarchy. Permit at most four delegation edges and reject cycles.
Agent origins and all delegated chains cannot acquire governance/ratification authority.
Bootstrap requires an enrolled human root, no delegation, exact epoch/nonce/artifact/prior
revision/head, and a nonretired bootstrap context. The final service must match the peer.

This verifies supplied state, not its custody or durability. Same-nonce replay/conflict,
atomic activation/retirement, concurrent expected-head checks, restart/restore protection,
revocation delivery and REST/gRPC parity still require Server's real S1/S3 implementation
tests. The fixture verifier does not fabricate those storage guarantees.

Request hashes retain ADR 0004's `munarium:decision-request:v1` domain. This candidate adds
`munarium:manifest:v1`, `munarium:decision-event-payload:v1` and
`munarium:decision-event:v1`. Each is UTF-8 domain bytes, one NUL byte and canonical JSON,
hashed with SHA-256 and represented as lowercase `sha256:` hex. Event acknowledgement binds
both payload and whole-event digests, tenant, event ID and durable position. Changing event
context cannot be hidden behind an unchanged payload digest. Sequence 1 has a null
predecessor; later sequences require its digest. No global service order is asserted.

Stage 1 event kinds are proposal, decision and refusal. Approval/activation/claim/grant/
dispatch/outcome/correction remain reserved for HUB-03 and are rejected by this candidate,
rather than accepted as arbitrary objects. No event fixture claims an effect occurred.
Attachments have at most eight descriptors and 1 MiB aggregate declared bytes; this does
not permit fetching URLs. Bytes/digests and artifact admission need consumer checks.

The typed obligation is `distinct-approval`, with `policy_digest`, `request_digest` and
`approver_scope`. The selector identifies authority required by the admitted policy; it
does not confer it. An approval-required decision must carry obligations; ordinary allow
and denial cannot. Runtime Council must verify a distinct eligible approver and every
context binding; these fixtures cannot approve their own request.

## Validation and reproducibility

Run from the hub root:

```console
python -m unittest discover -s scripts -p "test_*.py"
```

The existing CI unittest discovery executes these checks. Signed-vector tests require
OpenSSL 3 or later; missing executable or failed verification fails the suite rather than
skipping coverage. On Windows the checker also recognizes Git's bundled OpenSSL. Verification
uses [pkeyutl](https://docs.openssl.org/3.3/man1/openssl-pkeyutl/) with Ed25519 raw input and
public DER keys, in disposable temporary directories. It does not use the fixture generator.

The portable checker implements only the explicitly checked JSON Schema vocabulary used
here; unsupported schema keywords fail instead of being ignored. It is not a general JSON
Schema implementation and consumers should use their supported standards validator.
Local independent Draft 2020-12 meta-validation and 119 positive/negative comparisons with
`jsonschema` 4.25.1 agreed. Reproduce with the optional
[comparison script](../../../scripts/check_candidate_jsonschema.py):
`python scripts/check_candidate_jsonschema.py`. It requires `jsonschema` and is not part of
current CI. The local Python 3.13.7 suite passed all 32 unittest methods, including 32 signed
cases verified with OpenSSL 3.1.4; none were skipped.
No deployed client claims support for this candidate; existing Python/.NET canonical vectors
remain separate byte-compatibility evidence. Generated runtime bindings follow acceptance.

The [generator](../../../scripts/generate_candidate_fixtures.py) is an explicit revision
operation: `python scripts/generate_candidate_fixtures.py --new-candidate`. It requires
`cryptography` (local generator run: 45.0.6), creates a fresh ephemeral Ed25519 key in memory,
and rewrites the schemas, vectors and lock. New public keys/signatures change the candidate
digest and require review. It is deliberately not a CI step or a deterministic key generator.
No new Python package or service dependency is installed by the checks. Regeneration must
not reuse operational signing keys. OpenSSL/cryptography are test tools, not selected
runtime dependencies; deployment versions and vulnerability review remain separate.

File digests normalize CRLF to LF. Aggregate SHA-256 covers sorted relative filename,
one NUL, lowercase file hash and newline for every entry in the lock. This describes
exact candidate data, not artifact provenance, publication, signature or acceptance.
Future semantic/schema changes get a new reviewed candidate digest; released contracts
follow expand, migrate, remove with versioned vectors. No catalog/invariant state advances.
