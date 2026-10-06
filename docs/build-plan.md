# Platform build preparation and delivery sequence

**Working implementation guide derived from the
[founder's platform plan, revision 4](platform-plan.md).**
The original plan remains the historical strategy baseline. This guide makes the next work
reviewable without advancing catalog states, release labels or invariant evidence.

The hub is architecture and design documentation only: no Rust code or Cargo workspace.
The nine component repositories contain non-publishable Rust library scaffolds and design
guides. They declare local interfaces without implementations or wire types. Supported
contracts, deployment profiles and production action paths remain **none**.

**Phase 2 is planning and verification tooling.** The [dated source baseline](architecture/foundation-baseline.md)
confirms all twelve required public checkouts, including standalone Matrix. It records source
inspection, not runtime qualification. The proposals below require maintainer review and
accepted contracts before runtime implementation; this contribution changes neither foundation.

**Development focus — 6 October 2026.** Ioka has suspended VCP development: the experiment was
worthwhile, but continued development has become too expensive and is unlikely to deliver the
desired impact or independently provide a usable way to advance Munarium Governance Platform.
Ioka is concentrating more intensely on building the platform. The work packets below use a
bounded coding-agent workflow and do not depend on further VCP development or on VCP as a primary
development environment. See the [status update](../README.md#how-the-platform-is-built).

## Start here

1. Run the read-only [workspace preflight](architecture/foundation-baseline.md#workspace-preflight),
   then inspect and qualify the [foundation requirements](architecture/foundation-requirements.md).
2. Review the [decision register](architecture/contract-backlog.md#decision-register),
   [scaffold proposal](decisions/0001-scaffold-boundaries.md) and
   [execution proposal](decisions/0002-action-execution-protocol.md). Proposed is not accepted.
3. Resolve only the decisions blocking the next packet. Implement accepted principal,
   manifest/request, evaluator and minimum event definitions before effect-producing work.
4. Use the [local profile](architecture/reference-profile.md),
   [lifecycle](architecture/action-lifecycle.md) and
   [reference scenario](architecture/reference-scenario.md) as linked design review inputs.
5. Retain an experimental run record from the first integrated slice; successful compilation
   or documentation validation never advances a runtime capability or release label.

## Repository entry points

| Component | Implementation plan | Source modules | First bounded packet |
|---|---|---|---|
| Registry | [Build guide](https://github.com/iokaio/munarium-registry/blob/main/docs/implementation-plan.md) | `catalog`, `intake`, `activation` | REG-01: validate and resolve a candidate manifest without activating it |
| Gate | [Build guide](https://github.com/iokaio/munarium-gate/blob/main/docs/implementation-plan.md) | `evaluation`, `journal`, `connector` | GATE-01: deterministic decision-only evaluation and replay |
| Warden | [Build guide](https://github.com/iokaio/munarium-warden/blob/main/docs/implementation-plan.md) | `identity`, `grants`, `broker`, `revocation` | WARDEN-01: verify one identity path and reject widened delegation |
| Council | [Build guide](https://github.com/iokaio/munarium-council/blob/main/docs/implementation-plan.md) | `approval`, `governance`, `activation` | COUNCIL-01: request-bound approval through a minimal authenticated interface |
| Harness | [Build guide](https://github.com/iokaio/munarium-harness/blob/main/docs/implementation-plan.md) | `proposal`, `client`, `recovery` | HARNESS-01: consume canonicalization and outcome vectors |
| Gateway | [Build guide](https://github.com/iokaio/munarium-gateway/blob/main/docs/implementation-plan.md) | `routing`, `budget`, `provider`, `settlement` | GATEWAY-01: document and test the Server extraction seam |
| Sentinel | [Build guide](https://github.com/iokaio/munarium-sentinel/blob/main/docs/implementation-plan.md) | `timeline`, `telemetry`, `suspension` | SENTINEL-01: rebuild a task timeline from synthetic authoritative events |
| Assure | [Build guide](https://github.com/iokaio/munarium-assure/blob/main/docs/implementation-plan.md) | `package`, `verification`, `report` | ASSURE-01: verify one compact evidence package offline |
| Console | [Build guide](https://github.com/iokaio/munarium-console/blob/main/docs/implementation-plan.md) | `views`, `session`, `commands` | CONSOLE-01: read-only inventory and decision views |

These are repository entry points, not immutable implementation inputs. Record the full source
SHA and accepted decision/contract revision when opening each packet. Identifiers below are local
planning references; concrete hub/component issues are linked when execution begins. No issue,
accepted decision or release is implied by an identifier.

## Dependency sequence and exit evidence

| Stage | Work in dependency order | Exit evidence before advancing |
|---|---|---|
| 0 · preparation | FOUNDATION-01; DEC-01 then Server S1 if still required; explicit non-agent bootstrap | Inspected/pinned sources, actual foundation checks and refusal of unauthorized governance transition; no assumed September gaps |
| 1 · decision only | DEC-02/03, minimum DEC-07 identity/topology and DEC-08 records; S2 record shape, S3 principal verification, S4 lineage; WARDEN-01, REG-01, GATE-01 and HARNESS-01 | REF-01 replay plus manifest/lineage/tenant refusals, cross-client vectors, reproducible decision-only installation and experimental run record; no target authority |
| 2 · one action path | DEC-04–07 plus mandatory-durability subset of DEC-08 accepted; S2/S3/S4/S7/S9; durable Gate journal/action reservations, Warden broker/grants, Council approval/activation, REG-02/03 and one disposable connector | REF-02–19 with real persistence/isolation; atomic consumption, fencing, revocation, minimum restore/quarantine safety, installation and operator investigation recipe |
| 3 · daily operation | S8 Gateway extraction before model admission expansion; S6 telemetry, Sentinel timeline/suspension; Console reads before writes | Preserved Server compatibility, model-budget concurrency, measured suspension, rebuildable views, session/tenant-safe UX and repeatable installation |
| 4 · integrated evidence | S5 checkpoints; Assure offline verification, retention, full upgrade/restore exercises and released composition preparation | REF-20 plus independent verification, retained gaps, immutable pins, operational/security evidence and explicit support boundary |
| 5 · demand-led breadth | Additional identity/broker/provider/connector profiles, availability, offline packaging and federation | Separate conformance and operational evidence, actual test environment and maintainer for each added boundary |

Month windows in plan section 25 remain capacity assumptions. Preparation does not complete
Stage 0: no foundation qualification or S1 authority test is supplied by these scaffolds.
The [historical crosswalk](architecture/foundation-baseline.md#historical-plan-crosswalk) explains
why Matrix extraction is no longer a new work packet. The local reference milestone is the core
commitment to pursue; an enterprise profile is conditional on a named environment owner, access,
cost authority, expiry and committed review. No unavailable sponsor is on the core critical path.

## Work packets and capacity

One major capability slice and one foundation maintenance lane remain the work-in-progress
limit. The founder accepts each packet and its oracle; model review is advisory. The estimates
below are initial founder effort ranges including review, not measured velocity. Model/tool
spend caps must be recorded at intake; none of these estimates authorizes a paid run.

| Packet / repository | Prerequisite | Concrete deliverable and acceptance | Initial effort / uncertainty |
|---|---|---|---|
| FOUNDATION-01 / hub; foundations inspected | Workspace preflight | S1–S9 source/test map, exact revisions, current supported test commands, observed outcomes and provenance gaps. Preserve failed/unrun checks. | 8–16 hours for inventory/test planning; execution cost re-estimated per available environment |
| HUB-01 / hub | FOUNDATION-01 observations | DEC-01 ADR and bootstrap/principal vectors; maintainer decision before opening an S1 implementation packet. | 12–20 hours; existing Server seams and retirement design |
| HUB-02 / hub | Identity model from HUB-01 | DEC-02/03, minimum DEC-07 identity/topology and DEC-08 records; evaluator comparison, canonical/outcome vectors. Resolve ADR-0001 disposition without claiming runtime approval. | 28–52 hours plus DEC-07's intake allocation; canonicalization/evaluator uncertainty; split into reviewed subpackets |
| SLICE-01 / Registry, Warden, Gate, Harness, Server | Accepted HUB-01/02 contracts; S1 gate | REG-01, WARDEN-01, GATE-01, HARNESS-01 with S2–S4; REF-01 and refusal fixtures from a clean installation, exact input/run pins. | Estimate implementation after foundation audit; no calendar commitment while contract work is open |
| HUB-03 / hub | Recorded Stage 1 inputs; DEC-01/02 accepted | DEC-04–06, remaining DEC-07 effect profile and durable DEC-08 decisions; fault histories and action reservation oracle. | 36–56 hours plus remaining DEC-07 allocation and 8–16 for event durability; high storage/restore uncertainty |
| SLICE-02 / Gate, Warden, Council, Registry, Harness, Server | Accepted HUB-03; S7/S9 foundation gates | Reference effect, REF-02–19, installation/teardown and investigation runbook; no dispatch qualification with failed restore or bypass cases. | Estimate after protocol spike on selected durable storage |
| OPS-01 / Gateway, Sentinel, Console, Server | Stage 2 record/API contracts | S8 extraction compatibility first, then model budget; S6 projections and suspension; governed UI/session tests. | Estimate each component from accepted seams; do not run three major capabilities concurrently |
| EVIDENCE-01 / Assure, Server, hub | Stage 1/2 retained records; S5 | REF-20, offline verification, full retention/upgrade/restore evidence and composition proposal. | Estimate from actual record volume and supported retention boundary |

Every executable packet must add: repository/base SHA; accepted ADR and contract/vector digests;
permitted files; excluded work and unchanged APIs; fixture/oracle revision; exact commands and
required environment; estimated implementation and human review hours; time/spend ceiling;
failure/stop conditions; evidence destination; accountable owner and acceptance reviewer. Missing
required fields keep the packet in design. Upstream foundation changes get separate authorization
and PRs; this phase-2 planning branch performs none of them.

Review estimates weekly against accepted work, review delay, integration failures and rework.
At the first six-week review replace the annual 1,320-hour assumption with observed capacity,
explicit maintenance/adopter allocations and contingency. Defer breadth before authority controls.
An unestimated implementation packet is a visible planning gap, not zero effort. Calendar dates
follow the critical path and available review; they do not force a capability label.

## Requirement traceability

This is a scheduling map, not evidence. The [catalog](../README.md#the-invariant-catalog) remains
the claim source; the reference cases are specifications until actually run. Each implementation
PR supplies source/test/run links for its rows. Component tests supplement the integrated oracle.

| Requirement | First implementation / gate | Required evidence or scenario |
|---|---|---|
| S1; INV-01 | HUB-01 then upstream S1 / Stage 0 | Ordinary writer refuses activation; bound bootstrap and retirement; REF-05 integration later |
| S2; INV-14 | SLICE-01 record shape, SLICE-02 durability / Stages 1–2 | Required acknowledgements, REF-12/13; Gateway admission recording at Stage 3 |
| S3; INV-03/13 | WARDEN-01 then Council/Gate / Stages 1–2 | Verified origin, tenant isolation, scope attenuation and non-ratifier delegation; REF-05/06 |
| S4; INV-06 | SLICE-01 / Stage 1 | Missing or untrusted lineage refuses; authoritative field bindings; REF-04 |
| S5; INV-18 | EVIDENCE-01 / Stage 4 | Signed ranges and independent trust inputs; REF-20; no hidden missing artifacts |
| S6; INV-17 | DEC-08 in Stage 1; OPS-01 / Stage 3 | Source IDs/ranges and gap markers first; duplicate/out-of-order projection rebuild and telemetry-loss tests later |
| S7; INV-07 | SLICE-02 / Stage 2 | Authenticated hops and denied network/mount/credential paths; REF-07 |
| S8; INV-15 | GATEWAY-01/02 within OPS-01 / Stage 3 | Before/after Server compatibility; concurrent model root/child reservations and uncertain settlement |
| S9; INV-08/10/11/19 | SLICE-02 / Stage 2 | REF-08/10–15/17; durable claim/consumption, no uncertain resend, old-snapshot quarantine; full restore qualification at Stage 4 |
| INV-02/04 | REG-01 in Stage 1, REG-02/03 in Stage 2 | Candidate remains inert; unknown/incompatible artifacts refuse; activation conflict and retired-cache tests |
| INV-05 | HARNESS-01 / Stage 1 | Cross-language canonical bytes/digests and rejected ambiguity vectors |
| INV-09 | COUNCIL-01 and GATE-03 / Stage 2 | REF-03/04/18/19; request, context, target, mode epoch and validity changes invalidate authority |
| INV-12 | WARDEN-04 in Stage 2; Sentinel suspension in Stage 3 | REF-09; measured revocation bound, unconsumed/in-flight distinction and partition tests |
| INV-16 | CONSOLE-01–04 / Stage 3 | Two-tenant reads, session expiry, CSRF and same authority through UI/headless APIs |
| INV-20 | Federation packet / Stage 5 | Both domains permit; local policy cannot waive mandatory parent prohibition |
| INV-21/22 | Every packet / Stage 0 onward | Protected release path, no untrusted release secrets, source/contract/run pins and bounded claims |
| Cumulative action limits | DEC-06 then GATE-02/03 / Stage 2 | REF-16/17; independent of Gateway's monetary/token allowance |

## First reference scenario

Use a disposable local release target with a proposed source revision, exact build artifact,
test evidence, target environment and change window. Begin by evaluating and explaining the
request without dispatch. Enable the effect only after Stage 2's authority and durability
requirements are met.

The [reference specification](architecture/reference-scenario.md) defines exact artifact bytes,
tenant/approver fixtures, target epochs, an independent effect-count oracle and REF-01–20.
Harness owns the future integration runner; Gate owns the disposable target/connector tests;
the hub owns the reviewed scenario and run-record requirements. Record authority enforcement
separately from model answer quality. Do not call a real publisher or deployment target.

## Cross-repository work and shared code

One coordinating hub issue should name component issues, order, contract revisions and acceptance
evidence when implementation starts. The hub is not a runtime dependency. No shared DTO crate,
Server fork or copied execution/accounting subsystem is introduced by scaffolding.

The decision-only slice precedes real authority. Console is not a dependency of the first
approval path; a minimal authenticated Council interface/CLI is sufficient. Gateway first
preserves Server's existing accounting lineage. Assure verification must run without Console.

## Local development and what the checks mean

Each component's validation guide gives the exact commands. All initial crates build without
external dependencies or sibling checkouts. Run format, locked offline build, Clippy with
warnings denied, tests and API docs from each component root, followed by its hygiene checks.
No runtime tests exist yet; zero executed tests are not acceptance evidence.

This repository's checks remain documentation, licensing and hygiene checks from
[CONTRIBUTING](../CONTRIBUTING.md). Also run the gate regression tests:

```console
python -m unittest discover -s scripts -p "test_*.py"
python scripts/docs_linkcheck.py
```

The link checker validates its documented subset of local Markdown anchors and paths; it does
not validate remote URLs, PDF anchors or runtime claims. Negative controls include the original
broken numbered TOC, missing/cross-file/duplicate anchors, wrong repository origins and absent
required checkouts. The workspace preflight is local-only; CI clones the hub alone and runs its
script tests with temporary fictional repositories. CI and DCO remain independent checks.

## Release composition design

A future composition records immutable Server/Matrix/component releases and digests, contract
bundle, schema versions, migration requirements, deployment profile, policy/identity assumptions,
acceptance runs and unresolved findings. No placeholder `platform-lock.yaml` is created now:
there is no tested composition to describe.

Before that release, every integrated attempt retains an
[experimental run record](architecture/reference-scenario.md#experimental-run-record-from-the-first-integrated-slice).
It names participating components and explicit omissions; it need not include all nine to test
a bounded slice. Records preserve failed attempts and separate unavailable coverage from passed
tests. They cannot activate policy or advertise a released/qualified composition.

Before a capability becomes reference-qualified, its runbook must cover identity provisioning,
required dependency failure, migration and rollback, backup/restore, key rotation, revocation,
and unresolved outcomes. A release narrows scope when evidence is missing; it never replaces
request binding, recording, credential isolation or distinct authority with a schedule promise.
