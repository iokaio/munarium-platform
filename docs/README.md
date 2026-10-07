# Munarium Governance Platform documentation

Munarium Governance Platform extends governed memory into governed action. Its foundation stores claims, history and supporting evidence; the planned components add controls over what an agent may propose, which actions may execute, who may authorize them, and how the result can be checked. The central rule is that an agent's ordinary identity cannot activate the rules governing it or acquire the target credentials needed to bypass those rules.

The architecture separates four powers: **read**, **governed write**, **act** and **govern**. Requests pass through explicit policy, identity, approval and recording boundaries. The intended guarantee applies to the paths a deployment actually mediates; it does not make models infallible or cover unmanaged tools and credentials. See [system boundaries](architecture/system-boundaries.md) for the flows, trust assumptions and failure behavior.

The [platform repository](https://github.com/iokaio/munarium-platform) is the shared architecture and design hub. It coordinates the roadmap, decisions, contract requirements and acceptance criteria, while each component repository owns its implementation. The hub contains no Rust code and is not a runtime dependency.

## Foundation

| Component and repository | Role in the platform |
|---|---|
| [Munarium Server](https://github.com/iokaio/munarium) | Governed memory and the append-only accountability ledger: claims, history, evidence and governed writes. The platform plan adds linked action records and a separate governance-authority boundary here. |
| [Munarium Matrix](https://github.com/iokaio/munarium-matrix) | Governed, read-only access to structured data through reviewed query contracts and typed evidence. It supplies evidence for decisions without becoming a target-write path. |

Server and Matrix have their own releases and implementation evidence. The [foundation requirements](architecture/foundation-requirements.md) identify the extensions and qualification work needed before a platform composition can rely on them.

## The nine new components

These summaries describe the **planned responsibilities**. The repositories currently contain Rust interface scaffolds and build guides; their functional capabilities remain **Planned**. There is no qualified platform composition or production action path. The [component catalog](../README.md#component-catalog) and each repository's README record status.

| Component and repository | Plane | Planned responsibility |
|---|---|---|
| [Munarium Registry](https://github.com/iokaio/munarium-registry) | Authority | Inventory of agents, tools, manifests, owners and policy bundles. Keeps discovered or proposed capabilities inert until a separately authorized activation makes them effective. |
| [Munarium Harness](https://github.com/iokaio/munarium-harness) | Agent | Client libraries, proposal builders, diagnostics and framework adapters. Makes the governed path easy to use and exposes explicit outcomes; enforcement remains outside the agent and SDK. |
| [Munarium Gate](https://github.com/iokaio/munarium-gate) | Mediation | Evaluates action proposals against policy and evidence, records durable execution claims, and dispatches authorized work through isolated connectors. Preserves unknown outcomes for investigation instead of blindly retrying. |
| [Munarium Warden](https://github.com/iokaio/munarium-warden) | Authority | Verifies workload identity and delegation, issues narrowly bound execution grants, brokers credentials only to isolated connectors, and enforces bounded suspension and revocation. |
| [Munarium Council](https://github.com/iokaio/munarium-council) | Authority | Manages approvals bound to exact requests and the governance-change lifecycle. Separates proposal, ratification and activation; does not execute target operations. |
| [Munarium Gateway](https://github.com/iokaio/munarium-gateway) | Mediation | Controls model routes and data disclosure, reserves shared task budgets before invocation, and settles usage afterward. Begins by extracting Server's existing gateway and accounting lineage. |
| [Munarium Sentinel](https://github.com/iokaio/munarium-sentinel) | Assurance | Builds operational timelines and telemetry from authoritative records, exposes coverage gaps, and requests pre-authorized suspension through Warden. Cannot grant or restore broader authority. |
| [Munarium Assure](https://github.com/iokaio/munarium-assure) | Assurance | Assembles portable evidence packages and verifies their integrity, references and declared coverage offline. Reports omissions and control mappings without claiming automated compliance or certification. |
| [Munarium Console](https://github.com/iokaio/munarium-console) | Assurance | Provides human views of inventory, decisions, approvals and unresolved work. Starts read-only; later operator actions use the same governed service APIs, with no hidden administrative path. |

## How the components fit together

In the planned action path, Harness submits a proposal to Gate. Gate resolves Registry's manifest, uses Warden-verified identity, evaluates policy and obtains Council approval when required. Required records and a durable claim precede Warden's execution grant and isolated connector dispatch. Server retains the accountability chain; Sentinel exposes its operational state, Assure packages the evidence, and Console presents it to people. Gateway separately mediates model calls, including their data and budget consequences.

Implementation advances from contracts and decision-only replay to one complete governed action, then operational views and evidence export. The [build plan](build-plan.md) links each component's first work packet and the evidence required at each stage.

Related repositories provide [foundation examples](https://github.com/iokaio/munarium-demo) and [client package publishing](https://github.com/iokaio/munarium-clients-publish); they are not additional platform runtime components.

## Documentation index

The repository [README](../README.md) carries the component and invariant catalogs, release labels and roadmap. The pages below provide the detailed plan and implementation preparation.

| Document | What it is |
|---|---|
| [platform-plan.md](platform-plan.md) | The founder's delivery plan for the platform, revision 4 of 28 September 2026, with the 6 October VCP suspension amendment: strategy, architecture, the nine components, the governed action lifecycle, threat model, roadmap, sustainability, and appendices with the repository checklist, invariant catalog, illustrative contracts, standards alignment, glossary, sources and the Matrix consolidation plan. The hub's planning baseline. |
| [Build plan](build-plan.md) | Phase-2 work packets, decision dependencies, S1–S9/invariant traceability, capacity and evidence gates |
| [Parallel build plan](parallel-build-plan.md) | Proposed two-machine work allocation, component pairings, dependency order and integration gates |
| [Stage 1 development authorization](stage1-authorization.md) | Maintainer-directed implementation scope across six repositories, supporting CI changes and separate acceptance boundaries |
| [Overview paper (PDF)](architecture/Munarium_Governance_Platform_Open_Source_Applied_AI_Journey.pdf) | *An Open Source Applied AI Journey*, 29 September 2026, with a 6 October status update: a forward-looking, business-level introduction to the platform and its bounded-agent development method. VCP development is suspended; Ioka is focusing more intensely on the platform. Its case studies are synthetic; the repositories remain authoritative for status. |
| [Architecture index](architecture/README.md) | Foundation baseline, system boundaries, decision register, proposed lifecycle, local profile and reference acceptance scenario |
| [Decision index](decisions/README.md) | Cross-component design records, beginning with the scaffold proposal |

The founder's plan is the historical baseline. The build guide and design records make preparation actionable without changing release labels or claiming that proposed controls exist. Research notes, normative contract artifacts and composition evidence arrive with their own reviewed content. This hub contains no Rust code.

Phase 2 records current public source observations and concrete proposals for review. Its scripts
check repository presence and documentation correctness; they do not implement platform controls.
The [baseline crosswalk](architecture/foundation-baseline.md#historical-plan-crosswalk) explains
which historical statements no longer describe the current trees. The overview PDF's page-4
Word export instruction was removed as an editorial repair; its dated planning claims remain
historical, with notices superseding its VCP development assumptions. The
[6 October development focus update](../README.md#how-the-platform-is-built) records that the
VCP experiment was worthwhile but continued development became too expensive and is unlikely to
deliver the desired impact or independently advance the platform. Component count does not
prescribe a service count: Harness is an SDK.
