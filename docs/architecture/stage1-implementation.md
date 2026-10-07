# Stage 1 implementation record

**6 October 2026: Stage 1 service implementation complete; formal acceptance remains open.**
Both rows of the [parallel plan](../parallel-build-plan.md) now have executable
implementations, authenticated service integration and local regression evidence.
ADRs [0007](../decisions/0007-stage1-composition.md),
[0008](../decisions/0008-stage1-service-boundary.md) and
[0009](../decisions/0009-stage1-recovery-profile.md) record the shared choices.
Existing contract candidates and golden vectors were preserved. Candidates remain
inactive; no execution grant or target dispatch is in the service profile.

| Repository | Implemented behavior | Local evidence |
|---|---|---|
| Server | Explicit platform authority; non-agent enrollment; atomic nonce/transition receipts; monotonic retirement; external restore fence; reserved records and replay archives; shared REST/gRPC admission | 270 binary tests passed, 8 explicitly ignored; memory/PostgreSQL authority and record tests; 4 live mTLS REST/gRPC tests |
| Warden | Verified workload-provider mapping; root issuance; registered delegation attenuation; current per-recipient policy; mTLS service | Provider/delegation and principal tests; real service issuance/refusal/revocation |
| Registry | Signed candidate validation, current trust on every operation, SQLite custody, immutable candidate bytes and trust revision digests; mTLS service | 25 unit/integration tests plus compile-fail doc test; restart, substitution, tenant and storage failure controls |
| Gate | Current authenticated manifest/policy/lineage; bounded native OPA; durable recording intent; exact acknowledgement verification; authenticated lookup/replay | 8 tests; native OPA controls; separate-process restart and lost-acknowledgement recovery with evaluator absent |
| Harness | Independent Rust/Python canonicalization, typed outcomes/refusals, single-attempt mTLS transports and read-only recovery | 2 Rust and 7 Python tests; 13 library composition case groups; real service composition on both Server stores |
| SDKs | Named platform authority/record operations and caller-owned mTLS transport support in Python, Rust, .NET and Java | Generated contract drift/compatibility checks; language builds/tests; Python live REST/gRPC parity |

Separate-process tests use ephemeral operator, provider, publisher and service keys,
required mTLS and current Server authority on every admission. A certificate-checking
fault proxy deliberately loses an acknowledgement after Server archive commit. After
Gate restart with the evaluator unavailable, lookup and exact recovery return the
original decision. Tests also cover candidate restart, forged/misbound provider,
manifest signature and tenant refusal, REF-01 replay, changed operation conflict,
another actor's refused recovery, missing lineage, current revocation and authority
checkpoint outage. This is observed behavior, not an inferred library capability.

Harness's `scripts/run_services.py` records exact source inventories, dirty states,
binary/evaluator hashes, commands, output digests and exit statuses. Its separate
`scripts/run_stage1.py` retains the 13-case in-process composition, including the
unchanged Registry/Warden signed vectors. Reproduction commands and configuration
fields are in each component's service guide. Run evidence is local, not a released
immutable input or an assertion that remote CI passed.

A second code review added persistent Registry trust-content pins (including an
additive upgrade path), isolated outbound CA trust, typed recorded client refusals,
and corrected dependency-outage status mapping. Regression tests cover these changes.
The component workflows retain their checks. The coordinated Harness workflow accepts
exact sibling commit SHAs, uses a read-only token and retains sanitized run evidence.

The hub's full filesystem private-material scan still reports 55 pre-existing matches
in scanner source copied into nested local worktrees. Those unrelated worktrees are
excluded from the contribution, preserved, and not suppressed by a scanner exception.
The other five repositories' scans passed. License and documentation-link checks pass.

## Acceptance and operational limits

The first native evaluator profile is Windows amd64 OPA 1.21.1 with the pinned worker,
100 ms evaluation deadline and 64 MiB worker boundary. Server supports a single platform
replica; Registry and Gate require exclusive SQLite custody. Restore protection assumes
an independently retained authority checkpoint; restoring checkpoint and database to
the same older state cannot be detected locally. These implementations are not scale
or production qualified. The library retains later-stage Warden experiments, but its
Stage 1 service mounts no broker or grant route.

Human contract acceptance, published immutable composition inputs and independent
review remain open. No reviewer approval or production network-isolation qualification
is recorded on the maintainer's behalf. Matrix is excluded from this synthetic slice
because it consumes no structured-data source. Advancing to Stage 2 effects requires
its own accepted authority contracts and evidence.
