# Munarium Governance Platform

**The central architectural design hub for the Munarium Governance Platform.** This repository carries the shared explanation of the platform, its roadmap, cross-component decisions, normative interface specifications, integration designs and, when available, evidence for a tested composition. It coordinates nine open-source component repositories built around the existing Munarium foundation, [Munarium Server](https://github.com/iokaio/munarium) and [Munarium Matrix](https://github.com/iokaio/munarium-matrix). It is not a runtime component, not a remote production-policy dependency, and not a duplicate implementation of anything the component repositories hold.

> **Status: hub created; build preparation present.** This repository contains architecture and design documentation, the reviewed [founder's plan](docs/platform-plan.md), and [implementation preparation](docs/build-plan.md). It has **no Rust code or Cargo workspace**. The nine component repositories have dependency-free Rust interface scaffolds; their catalog state remains **repository created**, functional capabilities remain **Planned**, and there is **no platform release, published contract bundle or tested composition**. Compilation of a scaffold is not implementation or qualification evidence.

## Read the overview paper

[*Munarium Governance Platform: An Open Source Applied AI Journey*](docs/architecture/Munarium_Governance_Platform_Open_Source_Applied_AI_Journey.pdf) (PDF, 38 pages, originally published 29 September 2026) is the business-level introduction to the platform, published by Ioka LLC in its Applied AI Governance Series. It explains why a governed applied AI platform is being built in the open, how it is designed to work, and the founder's bounded coding-agent workflow. Its historical VCP development approach is superseded by the [6 October 2026 suspension update](#how-the-platform-is-built), also noted in the PDF. Its message in one line: **let agents propose; keep authority, evidence and rules somewhere else.**

The paper is **forward-looking**. It describes intended architecture and planned work; its case studies are synthetic composites with illustrative baselines and targets; and nothing in it is a certification, a compliance determination or a support commitment. Where it differs from a repository, the repository's README and evidence are authoritative, and this README's catalogs remain the status of record.

| Sections | What they cover |
|---|---|
| 1–3 | Why: the five governance gaps agency opens, why governed memory was necessary but not sufficient, and the journey from governed memory to governed action |
| 4–8 | How it works: the four powers and the principles in business terms, the planes and services, the nine-step governed action, consequence classes, degraded operation, governing change itself, evidence and framework alignment |
| 9–10 | How it is built: the hub, contracts before code, invariants as the acceptance language, the founder-led roadmap, an illustrative cost envelope, and coding-agent guardrails; the historical VCP approach now carries a suspension notice |
| 11–13 | How to start: adoption stages and enforcement modes, brownfield patterns, three synthetic case studies (a software release path, vendor maintenance before payment, patient scheduling and messaging), twelve actions to take now and a ninety-day starter plan |
| 14–15, appendices | Ways to participate, the invariant catalog as a checklist, a working glossary and sources |

Its five takeaways:

- **Governance has to sit on the path, not beside it.** Policies in documents or prompts do not stop an agent that holds a live credential; controls belong where the consequential call is made.
- **Separate four powers.** Read, governed write, act and govern are different permissions that most early agent deployments collapse into one service account.
- **Evidence is a product feature.** Every allowed, denied, approved or unresolved action should leave a record someone outside the system can verify.
- **Start narrow and prove the boundary.** One high-value workflow, observed first and then enforced, teaches more than an enterprise-wide policy rollout.
- **Build the way you govern.** Coding agents propose and implement, but never release, the same separation the product sells.

Most of the paper's playbook needs no Munarium software. Its first recommendation: find the agent in your organization that holds a credential it should not, and move that credential somewhere the agent can only ask for it.

## Start building

The [build plan](docs/build-plan.md) maps the founder's delivery stages to repository work packets and acceptance gates. Read the [system boundaries](docs/architecture/system-boundaries.md), [contract backlog](docs/architecture/contract-backlog.md) and [foundation requirements](docs/architecture/foundation-requirements.md) before implementing a cross-component path. The [scaffold decision proposal](docs/decisions/0001-scaffold-boundaries.md) explains the source layout and its limits. The [documentation index](docs/README.md) lists all pages.

## The platform in one paragraph

Munarium began as governed memory: an append-only ledger of claims with their history, controlled access to source material, and evidence returned alongside every answer. The Governance Platform extends that into governed action. Agents may reason, gather evidence and propose changes, but their ordinary operating identity must not activate the rules governing them, must not hold the credential that acts on a target, and must not approve its own consequential effects. The platform separates **memory, action, authority and assurance** without claiming to make models infallible or to control paths it does not mediate. Every release states its actual trust boundary, deployment assumptions, unsupported paths and residual risks. Missing authority, unavailable evidence, incomplete credential isolation or an unqualified connector narrows a release; it is never a reason to waive a control.

## Four powers, four planes

The platform separates four powers. A principal may be permitted to submit a memory claim without being permitted to activate its governance profile; may propose an external action without possessing the target credential; may execute an approved request without the power to approve a broader one.

| Power | What it is | Where it is mediated | The agent's part |
|---|---|---|---|
| Read | Retrieve permitted evidence | [Server](https://github.com/iokaio/munarium), [Matrix](https://github.com/iokaio/munarium-matrix) | Scoped access |
| Governed write | Submit claims through checks | [Server](https://github.com/iokaio/munarium) | Scoped proposal |
| Act | Create a bounded external effect | [Gate](https://github.com/iokaio/munarium-gate), [Warden](https://github.com/iokaio/munarium-warden) | Proposal only |
| Govern | Activate the governing rules | [Council](https://github.com/iokaio/munarium-council), [Registry](https://github.com/iokaio/munarium-registry) | No activation |

Four planes compose the platform. They are responsibility and trust boundaries, not a requirement for eleven hosts; a small reference deployment may run several services on one machine while keeping processes, credentials, network permissions and storage roles separate, and must not claim hardware-isolated independence.

| Plane | Components | Responsibility |
|---|---|---|
| Agent | [Harness](https://github.com/iokaio/munarium-harness) and agent runtimes | Untrusted reasoning and proposals; no ambient target or governance credentials |
| Mediation | [Gate](https://github.com/iokaio/munarium-gate), [Gateway](https://github.com/iokaio/munarium-gateway), [Server](https://github.com/iokaio/munarium), [Matrix](https://github.com/iokaio/munarium-matrix) | Typed effects, model access, governed memory, read mediation |
| Authority | [Registry](https://github.com/iokaio/munarium-registry), [Warden](https://github.com/iokaio/munarium-warden), [Council](https://github.com/iokaio/munarium-council) | Approved inventory, scoped grants, independently authorized activation |
| Assurance | [Sentinel](https://github.com/iokaio/munarium-sentinel), [Assure](https://github.com/iokaio/munarium-assure), [Console](https://github.com/iokaio/munarium-console) | Ledger-derived views, evidence exports, governed operator requests |

One shared accountability record runs through them: proposal, decision, authority, claim, dispatch, receipt. Read projections are rebuildable. Gate and Warden also require durable operational claim, consumption and revocation state; the proposed [execution protocol](docs/decisions/0002-action-execution-protocol.md) specifies how it links to Server without pretending independent stores share one transaction.

## Consequence and adoption

These are planned design vocabulary, not claims of existing support. Not every action deserves the same friction. Each capability is classified from **C0** (bounded observation) through **C1** (internal, ordinarily reversible change), **C2** (bounded external effect), **C3** (irreversible, sensitive, regulated or production-critical, requiring explicit distinct authority) to **C4** (prohibited for the requesting principal). The class is computed from the approved manifest and verified context, never from the agent's description; modifiers such as amount, recipient, environment and data sensitivity can raise it but never lower it ([platform plan](docs/platform-plan.md), section 18.1).

Adoption follows the workload, not the platform. The five adoption stages are **experiment, assist, propose, act and federate**; the first two produce value without giving an agent any external action authority. Enforcement mode is a separate dial: **observe** records traffic, **advise** computes shadow decisions, **guard** enforces a selected boundary, **enforce** mediates the declared consequential paths and **assure** adds continuing evidence and operational checks. Every record identifies the mode that actually applied, and observe or advise never makes an unsafe path safe ([platform plan](docs/platform-plan.md), section 21). The [overview paper](docs/architecture/Munarium_Governance_Platform_Open_Source_Applied_AI_Journey.pdf) (sections 11 to 13) walks through brownfield patterns and synthetic case studies that start in one narrow workflow and widen only on evidence.

## The repositories

Every public repository the plan names.

| Repository | Plane | Role |
|---|---|---|
| [iokaio/munarium-platform](https://github.com/iokaio/munarium-platform) | hub | Architecture, normative contracts, decision records, roadmap and composition evidence for the whole platform |
| [iokaio/munarium](https://github.com/iokaio/munarium) | foundation (mediation) | Munarium Server: governed memory, the append-only ledger, and the Server client libraries |
| [iokaio/munarium-matrix](https://github.com/iokaio/munarium-matrix) | foundation (mediation) | Munarium Matrix: governed, read-only structured evidence from enterprise data sources |
| [iokaio/munarium-registry](https://github.com/iokaio/munarium-registry) | authority | Inventory of agents, tools, manifests, and policy bundles |
| [iokaio/munarium-harness](https://github.com/iokaio/munarium-harness) | agent | SDKs that make the governed path easy for honest agents |
| [iokaio/munarium-warden](https://github.com/iokaio/munarium-warden) | authority | Workload identity, delegation, just-in-time credentials, kill switches |
| [iokaio/munarium-gate](https://github.com/iokaio/munarium-gate) | mediation | Policy decision and enforcement point for every tool call |
| [iokaio/munarium-gateway](https://github.com/iokaio/munarium-gateway) | mediation | Model-call mediation: routing, BYOK, budgets, screening |
| [iokaio/munarium-council](https://github.com/iokaio/munarium-council) | authority | Approvals, policy lifecycle, ratified governance transitions |
| [iokaio/munarium-sentinel](https://github.com/iokaio/munarium-sentinel) | assurance | Telemetry, anomaly detection, circuit breakers, incident replay |
| [iokaio/munarium-assure](https://github.com/iokaio/munarium-assure) | assurance | Control-framework mapping and evidence packs |
| [iokaio/munarium-console](https://github.com/iokaio/munarium-console) | assurance | One interface for approvers, operators, and auditors |
| [iokaio/munarium-clients-publish](https://github.com/iokaio/munarium-clients-publish) | tooling | The one place Munarium client packages are built for release and published from |
| [iokaio/munarium-demo](https://github.com/iokaio/munarium-demo) | examples | Munarium Demo: working applications and bundled datasets for evaluating the foundation |

Development of VCP ([iokaio/vcp](https://github.com/iokaio/vcp)) is **suspended** as of 6 October 2026; the [status update](#how-the-platform-is-built) explains the cost and impact assessment behind Ioka's stronger focus on the platform. It remains a separate project, outside the nine components and their runtime dependencies. Ioka's private repositories hold planning material awaiting publication review and the proprietary Matrix analytics adapters; nothing from them is copied into a public repository without that review.

## Component catalog

The catalog distinguishes **repository created**, **prototype runs**, **contract tested**, **reference qualified** and **independently reviewed**. None of those states is inferred from a badge, a branch name or a passing documentation job; each advances only with the evidence its component README records.

| Component | GitHub description | First useful public increment | Catalog state |
|---|---|---|---|
| [Registry](https://github.com/iokaio/munarium-registry) | Inventory of agents, tools, manifests, and policy bundles | Signed manifest catalog and schema validation | repository created |
| [Harness](https://github.com/iokaio/munarium-harness) | SDKs that make the governed path easy for honest agents | Typed proposal and outcome client with examples | repository created |
| [Warden](https://github.com/iokaio/munarium-warden) | Workload identity, delegation, just-in-time credentials, kill switches | One verified identity path and one isolated broker | repository created |
| [Gate](https://github.com/iokaio/munarium-gate) | Policy decision and enforcement point for every tool call | Replayable decision engine and fake-target lifecycle | repository created |
| [Gateway](https://github.com/iokaio/munarium-gateway) | Model-call mediation: routing, BYOK, budgets, screening | One hosted and one local provider path with receipts | repository created |
| [Council](https://github.com/iokaio/munarium-council) | Approvals, policy lifecycle, ratified governance transitions | Request-bound approval and immutable activation | repository created |
| [Sentinel](https://github.com/iokaio/munarium-sentinel) | Telemetry, anomaly detection, circuit breakers, incident replay | Ledger-derived timeline and authenticated suspension | repository created |
| [Assure](https://github.com/iokaio/munarium-assure) | Control-framework mapping and evidence packs | Portable evidence pack and offline verifier | repository created |
| [Console](https://github.com/iokaio/munarium-console) | One interface for approvers, operators, and auditors | Read-only inventory and decision views before write UX | repository created |

The foundation is released software with its own evidence: Munarium Server 1.3.0 in [iokaio/munarium](https://github.com/iokaio/munarium) and Munarium Matrix 1.2.0 in [iokaio/munarium-matrix](https://github.com/iokaio/munarium-matrix). The platform plan treats the September 2026 descriptions of them as a source baseline, and a **foundation qualification record** in this hub will pin the actual revisions, tests executed, gaps confirmed and changes completed before the roadmap relies on them. The nine Server changes the platform needs (S1 to S9: a separate governance authority role, linked action-record shapes, verified principal chains, source trust metadata, signed checkpoints, structured telemetry, authenticated service channels, an extracted model gateway, and a factored guarded-execution library) are made upstream in iokaio/munarium, never copied into forks.

## What belongs here

- **Architecture**: planes, trust boundaries, deployment profiles, the governed action lifecycle, consequence classes, provenance rules and degraded-mode contracts.
- **Decision records**: versioned records of cross-component decisions. A security or protocol decision that affects several repositories is resolved here before parallel implementation begins, so that agents and contributors do not independently invent slightly different grant semantics, principal-chain rules or request hashes.
- **Contracts**: the normative wire envelopes and cross-component semantics, with golden test vectors. Runtime libraries remain with an owning component or the foundation; a factored library has one owner and one versioned release source. Generated bindings may be published by Harness and identify the contract digest they came from.
- **The invariant catalog**, below, referenced from every component by version.
- **Roadmap**: milestones, dependencies and the acceptance evidence each stage requires.
- **Integration**: cross-component conformance specifications that treat the application composition as the unit of evaluation, reporting answer quality separately from authority enforcement.
- **Examples and deployment recipes**: narrow, reproducible reference scenarios and reviewed local and enterprise recipes.
- **Releases**: composition manifests and qualification reports. A platform release means that a specific set of independently versioned components was tested together, recorded in a composition manifest, provisionally **`platform-lock.yaml`**, that lists every component by immutable release and digest with the contract bundle, policy-schema versions, migration requirements, supported deployment profile and links to build and acceptance evidence. It does not mean every repository has the same version number or that a floating `main` is a compatible composition.

Planning documents change through normal reviewed development. **Activated runtime policies do not.** The hub publishes artifacts and decisions; a deployed Registry or Council accepts only artifacts that pass the deployment's own admission and authority checks. GitHub availability must not determine whether an already installed control can execute a pinned policy, and a compromised documentation branch must not become permission to activate new runtime capability.

## What does not belong here

Production keys, customer policies, private reports, raw customer evidence, live credentials, confidential assessments and unremediated vulnerability details. A public contract can describe a private artifact's required shape without exposing its contents. Public development coexists with private vulnerability intake ([SECURITY.md](SECURITY.md)) and protected signing material.

The hub also does not become a twelfth runtime component, a component's live database, or a copy of any component's implementation.

## Repository layout

```
munarium-platform/
├── README.md              scope, status, components, entry paths (this file)
├── LICENSE, NOTICE        Apache-2.0 for Ioka-owned repository work
├── GOVERNANCE.md          maintainer roles and the decision process
├── SECURITY.md            the private vulnerability-reporting route
├── CONTRIBUTING.md        human accountability and AI disclosure
├── docs/README.md         documentation index
├── docs/platform-plan.md  the founder's delivery plan, revision 4 (the planning baseline)
├── docs/images/           the plan's figures, each as SVG source and PNG render
├── docs/build-plan.md     component work packets and delivery gates
├── docs/architecture/     boundaries, contract backlog, foundation requirements, overview paper (PDF)
├── docs/decisions/        decision index and scaffold proposal
├── docs/research/         attributed research and source notes
├── contracts/             normative wire schemas and golden vectors
├── roadmap/               milestones, dependencies, acceptance evidence
├── integration/           proposed cross-component acceptance specifications
├── examples/              narrow, reproducible reference scenarios
├── deployment/            reviewed local and enterprise recipes
└── releases/              composition manifests and qualification reports
```

The root files, `docs/README.md`, `docs/platform-plan.md`, `docs/build-plan.md`, `docs/images/`, `docs/architecture/` and `docs/decisions/` exist. The remaining paths are proposed organization, added only with reviewed content. Contracts, integration scenarios, deployment recipes and composition records are design artifacts here; runtime Rust implementations belong to components or the foundation. There is no hub `src/`, Cargo package or cross-repository workspace.

## The invariant catalog

Each invariant names a claim, its trust assumptions, its owner, the tests that exercise it and the release evidence. Component repositories reference this catalog by version and may not weaken a test that exercises an invariant; they narrow a release and record the gap instead. **A blank evidence field means unverified, not passed.** Every field is blank today.

| ID | Required property | Primary owner and first gate |
|---|---|---|
| INV-01 | Ordinary governed-write authority cannot activate a governance profile | Server and Council; stage 0 |
| INV-02 | A discovered or agent-proposed tool remains inert until authorized activation | Registry; stage 1 |
| INV-03 | Every accepted action has a verified tenant and principal context | Warden, Gate, Server; stages 1–2 |
| INV-04 | Unknown or incompatible manifests fail closed | Registry and Gate; stage 1 |
| INV-05 | Canonical requests produce the same digest across supported clients | Hub contracts and Harness; stage 1 |
| INV-06 | Missing mandatory lineage does not become trusted authority | Server and Gate; stages 1–2 |
| INV-07 | No qualified target credential is readable from the agent environment | Warden and deployment profile; stage 2 |
| INV-08 | No grant is issued without a durable, matching execution claim | Gate and Warden; stage 2 |
| INV-09 | Approval is invalid after relevant content, policy validity or target preconditions change | Council and Gate; stage 2 |
| INV-10 | A grant cannot be concurrently consumed for multiple dispatches | Warden and Gate; stage 2 |
| INV-11 | An unresolved effect is never blindly repeated | Gate, connector, Harness, Console; stages 2–3 |
| INV-12 | Revoked authority stops new affected work within the qualified bound | Warden and Sentinel; stages 2–3 |
| INV-13 | A delegated principal cannot widen its originating scope or become its own ratifier | Warden and Council; stage 2 |
| INV-14 | Required-recording failure prevents new consequential dispatch | Server, Gate, Gateway; stages 2–3 |
| INV-15 | Task and child-task reservations cannot exceed the enforced shared budget | Gateway; stage 3 |
| INV-16 | Console cannot perform a privileged operation unavailable through governed APIs | Console, Council, Warden; stage 3 |
| INV-17 | Missing evidence or telemetry is reported as a gap, not a successful interval | Sentinel and Assure; stages 3–4 |
| INV-18 | Evidence-package verification detects changed or missing required artifacts | Assure and Server; stage 4 |
| INV-19 | Restore cannot silently reactivate a consumed grant or erase an unresolved claim | Gate, Warden, Server; minimum safety at stage 2, full recovery exercises at stage 4 |
| INV-20 | A local overlay cannot waive a mandatory parent prohibition | Council, Registry, Gate; stage 5 |
| INV-21 | Untrusted pull-request code cannot acquire release secrets or replace active approval controls | Hub and repository CI; stage 0 onward |
| INV-22 | A release advertises only the profiles and capabilities supported by its evidence | Component maintainers and hub; every stage |

## Release labels

Evidence labels, not editions. All associated Ioka-owned implementation is open source. A component may be conformance-tested while another remains experimental; the platform composition must not advertise a stronger boundary than its weakest required dependency supports.

| Label | Minimum meaning |
|---|---|
| Planned | Architecture or work items exist; no functioning capability is claimed |
| Experimental | A runnable prototype exists with explicit limitations and no broad production claim |
| Conformance-tested | A named version passes the published suite for a stated environment and contract |
| Reference-qualified | The integrated composition passes operational, recovery, authority and deployment tests for a specific profile |
| Independently reviewed | A named independent review covers a stated revision and scope; findings and residual limitations are recorded |

## The roadmap

The roadmap begins when the founder starts the program. Public repositories exist from the start; each capability advances only after its acceptance evidence. The month ranges are targets that follow founder capacity and evidence; the release gates are commitments to evidence. Lower availability, unresolved foundation defects, unavailable enterprise sandboxes or security findings rebaseline the calendar, never the controls.

| Stage | Window | Scope | Exit evidence |
|---|---|---|---|
| 0 | month 1 | Populate the hub and the nine repositories; foundation qualification record; Server S1 with a non-agent bootstrap attestation; confirm current Matrix layout/release evidence rather than repeat the historical move | Public planning artifacts, verified repository ownership, a secret and rights review, reproducible foundation tests, a demonstrated refusal of an unauthorized governance transition |
| 1 | months 2–3 | Contracts and decision-only capability: Registry's catalog, Gate's evaluator, action-record shapes, verified principal context, a minimal Harness client; Warden and Council interfaces and bounded prototypes | Deterministic replay of allowed and refused proposals, unknown-manifest rejection, tenant isolation fixtures, contract compatibility, no hidden target credential in the agent environment |
| 2 | months 4–6 | The first complete governed action: Gate's durable journal, Warden's first identity and broker path, Council's minimum approval and activation; one narrow connector, one reference identity system, one deployment profile | Recorded proposal-to-outcome chain, bypass tests within the stated boundary, atomic grant consumption, crash recovery, stale-state rejection, a usable operator runbook |
| 3 | months 7–9 | Daily operational use: Gateway extraction, Sentinel timeline and suspension, Console read-only views then governed interactions; a small number of external evaluations | Clean local installation, tested budget concurrency, measured suspension propagation, recoverable views, role-safe Console interactions, at least one evaluation report with both the successful path and the remaining limitations |
| 4 | months 10–12 | Integrated open platform: Assure's evidence package and verifier, Server checkpointing, archival basics, upgrade and restore exercises, the composition manifest | Reproducible installation from pinned artifacts, verified evidence export, recovery exercises, compatibility records, security findings disposition, explicit support limits |
| 5 | months 13–18+ | Demand-led breadth in the same public repositories: identity brokers, connectors, cloud profiles, availability, offline packaging, federation | Each additional boundary has its own conformance and operational record and a maintainer who can reproduce and explain it |

The twelve-month target is a coherent single-cell reference platform: public code for all nine components, a reproducible local installation, selected qualified integrations, and a documented path from proposal to independently authorized effect. It is not a promise of broad multi-cloud general availability. When capacity is constrained, breadth goes first (connector breadth, SDK breadth, UI polish, packaging variants, simultaneous adopter commitments), then advanced analytics, federation and multi-region automation. Request binding, mandatory evidence, credential isolation and required distinct authority are never removed to preserve a date.

## How the platform is built

**Development focus update — 6 October 2026.** Ioka has suspended development of [Vibe Code Pro (VCP)](https://github.com/iokaio/vcp). The experiment was worthwhile, but continued development has become too expensive and is unlikely to deliver the desired impact or, on its own, provide a usable way to move Munarium Governance Platform forward. Ioka is concentrating its effort more intensely on building Munarium Governance Platform. Platform delivery no longer assumes VCP as its primary development environment or depends on further VCP development.

The platform will be built primarily by the founder with assistance from coding agents and multiple models. The founder retains responsibility for architecture, verification and release decisions. Agents propose and implement within a bounded work packet; a protected release path, held by a human, admits the exact approved revision; no coding agent may publish a release or rewrite its active control baseline. [GOVERNANCE.md](GOVERNANCE.md) describes the roles, the decision process, the work-in-progress limits and the limits of a single maintainer.

Nine repositories create coordination cost. The hub addresses it with a reusable repository template (the governance files every component carries), a shared CI convention, machine-checked contract compatibility, and an integration job that consumes a proposed composition change. A cross-repository feature has one hub issue linking its component issues, required order, test fixtures and acceptance evidence. Breaking interface changes use **expand, migrate, remove**: a producer adds a compatible capability, consumers adopt it, the composition records the transition, and only then is the obsolete contract removed under the declared version policy.

## Where the material comes from

The platform plan was drafted in a private Ioka repository. This hub was created on 28 September 2026 as a new public repository, not by renaming that one, so no private history is carried here. Reviewed planning material moves into the hub document by document, each with a publication review for assets, licenses, secrets, customer references and private planning material, and a migration record naming the document and its source revision. A failed publication review delays exposure of the affected history, not the availability of a clean public design.

The first document moved is the plan itself: [docs/platform-plan.md](docs/platform-plan.md), revision 4 of 28 September 2026, whose note at the top records its source revision and subsequent amendments. This README draws on that plan, the [overview paper](docs/architecture/Munarium_Governance_Platform_Open_Source_Applied_AI_Journey.pdf) of 29 September 2026, the phase-2 source inspection and the founder's 6 October development focus update. The dated VCP suspension amendment supersedes the earlier tooling assumptions. Where the plan and a repository disagree about what exists, the repository's README and evidence are authoritative.

## Acknowledgment

The founder gratefully acknowledges **Jamey Kistner of OSINTelligence LLC** for the exchange that helped sharpen the platform's treatment of the boundary between an agent's governed writes and the authority that governs those writes. Kistner's *The Sovereign Stack: Architecture, Discipline, and Evidence from One Desk* (OSINTelligence LLC; Zenodo, concept DOI [10.5281/zenodo.22316158](https://doi.org/10.5281/zenodo.22316158)) distinguishes real-time enforcement from verification outside a self-improving system's control. The acknowledgment recognizes the research and the exchange; it does not imply that Kistner endorses Munarium or that Munarium implements the Sovereign Triad. Munarium Sentinel is a software assurance component, not a claim of equivalence to the hardware-isolated External Sentinel that work describes. Research citations belong beside the decisions they inform, in `docs/research/` and the decision records, as they arrive.

## Development

The gates that run today are the repository-wide ones, on every push and pull request from [.github/workflows/repo-hygiene.yml](.github/workflows/repo-hygiene.yml):

| Gate | Command | What it holds true |
|---|---|---|
| Licence and notices | `py check_license.py` | `LICENSE` is the canonical Apache-2.0 text; `NOTICE`, `TRADEMARK.md` and `CODE_OF_CONDUCT.md` exist; every Ioka-authored source file carries `SPDX-License-Identifier: Apache-2.0` |
| Private material | `py scripts/private_material_scan.py` | The private research and planning vocabulary behind Munarium stays out of the public tree |
| Documentation links | `py scripts/docs_linkcheck.py` | Supported local Markdown paths and heading fragments resolve; every page under `docs/` is indexed; remote links and non-Markdown fragments are outside scope |
| Secrets | `gitleaks dir . --config .gitleaks.toml` | Nothing that looks like a credential is in the tree or its history |
| Sign-off | `git commit -s` | Every commit in a pull request carries a Developer Certificate of Origin trailer ([.github/workflows/dco.yml](.github/workflows/dco.yml)) |
| Gate regression tests | `python -m unittest discover -s scripts -p "test_*.py"` | Documentation-anchor and read-only workspace-preflight negative controls; temporary repositories require Git, no network |

Schema validation for `contracts/`, golden-vector checks and the integration job are added with the content they check. Coding agents working here follow [AGENTS.md](AGENTS.md).

The [phase-2 build guide](docs/build-plan.md) adds proposed decision/packet dependencies,
requirement traceability, a concrete local profile and a synthetic acceptance oracle. The
[foundation baseline](docs/architecture/foundation-baseline.md) records inspected revisions,
including standalone Matrix; it is not a qualification report. Run the optional workspace
preflight against an explicit parent directory; individual component builds remain independent.

## Licensing

Apache-2.0 ([LICENSE](LICENSE), [NOTICE](NOTICE)) for Ioka-owned repository work. The names are not part of that grant: [TRADEMARK.md](TRADEMARK.md) says what you may do without asking, which is most things. Existing dependencies, imported code, research material and previously contributed assets retain their applicable terms; open sourcing a repository does not relicense material copied into it. There is no proprietary edition of the platform components; deferred is a roadmap state, not a commercial restriction. Munarium Enterprise remains a separate, proprietary distribution built on Server and Matrix, and nothing here is reserved for it.

## Contributing, support, security

Signed-off pull requests, no CLA ([CONTRIBUTING.md](CONTRIBUTING.md)); a cross-component change starts as a decision record here. Questions that span components go to this repository's Discussions, defects and design findings to Issues, and suspected vulnerabilities to the private channel [SECURITY.md](SECURITY.md) names, never a public issue. What is and is not supported: [SUPPORT.md](SUPPORT.md). Roles and decisions: [GOVERNANCE.md](GOVERNANCE.md). Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). History: [CHANGELOG.md](CHANGELOG.md).
