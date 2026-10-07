# Stage 1 development authorization

On 6 October 2026, the maintainer directed implementation of all Stage 1 work in
the [parallel build plan](parallel-build-plan.md), then explicitly directed the
repository guidance and CI changes needed to carry it out. This records that
development authorization; it does not record contract acceptance or a release.
It applies to the current Stage 1 work until completed or superseded by the maintainer.

## Repository scope

| Repository | Authorized work |
|---|---|
| `munarium-platform` | Stage 1 decision records, versioned contract candidates and export tooling, integration requirements and evidence records |
| `munarium` | Required Server foundation work: S1 bootstrap authority, S2 records, S3 principal verification, S4 lineage and minimum S6 event delivery |
| `munarium-registry` | Candidate manifest validation, resolution and authenticated admission; submitted candidates remain inactive |
| `munarium-warden` | Provider identity admission, principal verification and delegation attenuation |
| `munarium-gate` | Deterministic decision-only evaluation, refusal, recording and replay |
| `munarium-harness` | Typed proposals, canonicalization, outcomes, recovery and integrated Stage 1 tests |

Authenticated service transport, including mTLS, and the minimum identity/topology
boundary are part of this scope. Foundation inspection and validation may read
other workspace repositories. If a confirmed Stage 1 dependency requires another
repository change, record the dependency and bounded scope before editing; do not
expand into unrelated component work.
Stage 2 execution grants, credential brokering, connector dispatch and general
policy activation are outside this packet.

## Authorized implementation and supporting changes

Proceed with source, tests, documented examples, pinned dependencies, compatible
additive migrations, development tooling and documentation needed for this slice.
This includes edits to `AGENTS.md`, `CLAUDE.md`, relevant `CONTRIBUTING.md` guidance,
the hub's governance clarification, and build/test workflows under `.github/`.
Existing ownership, DCO, security checks and release protections still apply.
Do not request the same development permission again for each prerequisite or file.

Record shared semantic choices in a hub decision record before implementing them
in consumers. Proposed status permits this authorized experimental implementation
and testing; it does not make a proposal an accepted contract. Preserve existing
candidate bundles, digests and golden vectors. Prepare a new version when semantics
change and use the documented exporter and re-vendoring process for consumers.
Do not rewrite a test oracle to make implementation pass. Formal acceptance records
must identify the human disposition and exact reviewed revision.

Run local and CI tests with synthetic data and disposable resources. Temporary
test-only certificates, keys, identities, bootstrap authority and decision-only
operator bindings may be generated inside the isolated test environment. They
must have no production trust or target authority, never activate a submitted
candidate, and be created independently of the untrusted proposal path. Record
and clean up task-owned resources. Keep generated secret material out of tracked
files and logs; retain public fixtures only under the repository's existing rules.

CI may fetch pinned public dependencies and run isolated service/database tests
without production credentials or privileged publication tokens. Keep read-only
repository permissions, fork isolation and required checks. Add or extend meaningful
checks as behavior is implemented; the guidance parity check only detects drift
between `AGENTS.md` and `CLAUDE.md`, not correctness or Stage 1 completion.

## Acceptance and operational boundaries

Development authorization does not grant a running agent platform authority. The
implemented system must still verify identity, tenant, delegation, lineage and
current authority independently, fail closed, and leave candidate manifests inert.

Human contract acceptance, independent review, qualification claims, merge,
deployment, release/package publication, paid infrastructure and production
credential operations require their own applicable authorization. This packet
does not authorize changes to branch protection, ownership, trusted approval or
release workflows, scanner exceptions or signing policy. Existing explicit grants
for other bounded tasks retain their own scope. Preparing implementation and
review evidence does not require those later approvals in advance.

Track actual behavior and remaining gates in the
[Stage 1 implementation record](architecture/stage1-implementation.md) and
[composition decision](decisions/0007-stage1-composition.md). Keep failed and
unavailable checks visible. Completion requires the plan's evidence; permission,
a compiled library and a passing guidance check are not substitutes.
