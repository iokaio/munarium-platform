# Platform build preparation and delivery sequence

**Working implementation guide derived from the
[founder's platform plan, revision 4](platform-plan.md).**
The original plan remains the historical strategy baseline. This guide makes the next work
reviewable without advancing catalog states, release labels or invariant evidence.

The hub is architecture and design documentation only: no Rust code or Cargo workspace.
The nine component repositories contain non-publishable Rust library scaffolds and design
guides. They declare local interfaces without implementations or wire types. Supported
contracts, deployment profiles and production action paths remain **none**.

## Start here

1. Read [system boundaries](architecture/system-boundaries.md) and
   [foundation requirements](architecture/foundation-requirements.md).
2. Review the [scaffold decision proposal](decisions/0001-scaffold-boundaries.md).
3. Resolve the first items in the [contract backlog](architecture/contract-backlog.md)
   before adding concrete cross-component types or runtime behavior.
4. Take one component work packet below, record its exact input revisions, and implement
   its acceptance cases with a retained oracle.
5. Record local checks and gaps. Advertise a capability only with its evidence and review;
   successful compilation is not that evidence.

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

These links describe the prepared repository paths; until the local changes are published,
open the corresponding sibling checkout. No remote issue, accepted decision or release is
implied by a work-packet identifier.

## Dependency sequence and exit evidence

| Stage | Work in dependency order | Exit evidence before advancing |
|---|---|---|
| 0 · preparation | Review public material; establish source layout; pin/qualify Server and Matrix; implement Server S1 with explicit non-agent bootstrap | Reviewed public artifacts, rights/secret checks, actual foundation test record and refusal of unauthorized governance transition |
| 1 · decision only | Principal/manifest/proposal/decision contracts and vectors; one evaluator choice; Registry catalog, Gate replay and minimal Harness; Warden/Council interface work | Deterministic allowed/refused replay, unknown-manifest rejection, tenant isolation, client compatibility and no target credential in agent environment |
| 2 · one action path | Shared S2/S3/S7/S9 support; durable Gate journal, Warden identity/broker/grants, Council approval/activation; one isolated disposable connector | Full recorded chain, request binding, distinct authority, atomic consumption, fencing, crash/restore handling, revocation and operator investigation recipe |
| 3 · daily operation | Gateway S8 extraction before admission expansion; Sentinel timeline and bounded suspension; Console read-only before governed interactions | Preserved Server compatibility, budget concurrency, measured suspension, rebuildable views, session/tenant-safe UX and repeatable local installation |
| 4 · integrated evidence | Assure offline verification, Server checkpoints, archive/retention, upgrade and restore exercises, composition definition | Independently reproducible verification, retained gaps, immutable component/contract pins, operational/security evidence and explicit support boundary |
| 5 · demand-led breadth | Additional identity/broker/provider/connector profiles, availability, offline packaging and federation | Separate conformance and operational evidence, actual test environment and maintainer for each added boundary |

Month windows in plan section 25 remain capacity assumptions. Preparation does not complete
Stage 0: no foundation qualification or S1 authority test is supplied by these scaffolds.
Matrix migration/release is its own maintenance work; verify current upstream state before
acting on the historical Appendix I.

## First reference scenario

Use a disposable local release target with a proposed source revision, exact build artifact,
test evidence, target environment and change window. Begin by evaluating and explaining the
request without dispatch. Enable the effect only after Stage 2's authority and durability
requirements are met.

The integration specification must cover the permitted action and:
substituted artifact, changed target, stale approval, attempted self-ratification,
missing evidence, direct credential/egress bypass, concurrent redemption, revoked grant,
lost target response and restart/restore. Record authority enforcement separately from
model answer quality. Do not call a real publisher or deployment target for the first proof.

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
[CONTRIBUTING](../CONTRIBUTING.md). Every new design page is indexed, and links resolve locally.
Existing CI and DCO coverage remains independent of local validation.

## Release composition design

A future composition records immutable Server/Matrix/component releases and digests, contract
bundle, schema versions, migration requirements, deployment profile, policy/identity assumptions,
acceptance runs and unresolved findings. No placeholder `platform-lock.yaml` is created now:
there is no tested composition to describe.

Before a capability becomes reference-qualified, its runbook must cover identity provisioning,
required dependency failure, migration and rollback, backup/restore, key rotation, revocation,
and unresolved outcomes. A release narrows scope when evidence is missing; it never replaces
request binding, recording, credential isolation or distinct authority with a schedule promise.
