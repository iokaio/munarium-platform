# Foundation requirements before platform implementation

**Qualification design, not a completed qualification report.**
[Platform plan revision 4, section 16](../platform-plan.md) is a historical requirements
baseline. The [hub README](../../README.md#component-catalog) describes Server 1.3.0 and Matrix
1.2.0 as the foundation. Confirm actual repository revisions and behavior before relying on
either; no upstream code, dependency pin or release is changed by scaffolding these components.

The [phase-2 baseline](foundation-baseline.md) records inspected public revisions and separates
the already changed repository layout from qualification still required. Server and Matrix
remain read-only during this planning contribution; upstream implementation is later work.

## Qualification record to create from actual runs

For Server and Matrix, retain the repository URL, immutable revision and release, toolchain,
contract digest, command and exit status, test profile, known gaps and retained output.
Separate an observed implementation from a source-plan description. Mark unrun environments
unavailable and failures unresolved. The Matrix migration in Appendix I is historical planned
work; do not repeat it merely because the plan still describes the pre-cutover tree.

## Server changes and their consumers

| ID | Required change | Consumer / first dependency | Evidence needed |
|---|---|---|---|
| S1 | Separate governance authority, with explicit non-agent bootstrap attestation | Council/Registry; Stage 0 | Ordinary governed writer cannot activate; transition binds expected prior state; bootstrap scope/retirement recorded |
| S2 | Linked durable action records | Gate/Council/Warden; Stage 1–2 | Required proposal/decision/claim/grant/dispatch/outcome records survive relevant failures |
| S3 | Verified principal chains | Warden/Gate; Stage 1–2 | Verified origin and delegation, no self-reported identity accepted |
| S4 | Trust metadata and lineage | Gate/Matrix evidence; Stage 1–2 | Missing lineage stays unknown; extracted content cannot silently acquire authority |
| S5 | Signed checkpoints and optional witnesses | Assure; Stage 4 | Verifiable ranges, explicit signer custody and stated tamper-evidence limits |
| S6 | Structured telemetry | Event shape in Stage 1; Sentinel export in Stage 3 | Pinned event/convention version; mandatory facts separated from loss-tolerant metrics |
| S7 | Authenticated service channels | First complete action slice; Stage 2 | One qualified topology with every hop, including proxy termination, explicit |
| S8 | Extract shared model-gateway capabilities | Gateway; Stage 3 | Existing Server behavior preserved; one accounting lineage; new admission behavior tested separately |
| S9 | Factor guarded execution semantics | Gate/Warden; Stage 2 | One owner-maintained protocol/library with crash, conflict, replay and unresolved tests |

S1 does not wait for full Council. S2 does not wait for Console. S3 and canonicalization
must agree before usable target authority is enabled. S8 and S9 require inspection of
the upstream implementation and existing tests before code extraction; this hub does
not host Rust libraries or copies of foundation code.

The [delivery traceability table](../build-plan.md#requirement-traceability) assigns every S-item
and invariant to a first gate. S4 is needed by Stage 1 lineage refusal tests; it is not implicit
future Matrix work. Minimum S9 restore/quarantine behavior is a Stage 2 prerequisite even though
full operational recovery and S5 archival evidence arrive at Stage 4. A missing Matrix checkout
does not block a standalone component build, but it prevents a complete foundation audit.

## Matrix boundary

Matrix stays governed and read-only, with its public SPI preserved. The proposed platform
integration registers approved query capabilities, accepts verified identity and produces
evidence references for approval. Disclosure, destination and cost affect consequence;
a SELECT statement does not automatically mean C0.

Private adapters, credentials, deployment material and private repository history remain
outside this work. Any future publication or migration needs its own ownership and
publication review. The nine new component crates do not depend on a sibling checkout
or copy adapter source.
