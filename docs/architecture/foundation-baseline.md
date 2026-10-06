# Phase 2 foundation and repository baseline

**Source inspection recorded 6 October 2026; not foundation qualification.**
This records public source observations used to refine the next work packets. No Server or
Matrix implementation, configuration, Git history or dependency was changed by this work.
Runtime tests, release authenticity and hosted CI were not requalified. Recheck the revisions
before implementation; a source version is not an artifact digest or a compatibility result.

## Public source observations

| Repository | Inspected revision | Observation and source |
|---|---|---|
| Server | `2c40480fdc2378e66dc23acdfaf82b529b9d22ee` | [README](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/README.md) points to standalone Matrix; [workspace](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/Cargo.toml) declares Server 1.3.0. |
| Matrix | `643863fcb4433c8236f3ab22ca812f17c354f34c` | [README](https://github.com/iokaio/munarium-matrix/blob/643863fcb4433c8236f3ab22ca812f17c354f34c/README.md) and [workspace](https://github.com/iokaio/munarium-matrix/blob/643863fcb4433c8236f3ab22ca812f17c354f34c/Cargo.toml) show standalone service and clients, source version 1.2.0. Registry/principal/Council integrations remain described as planned. |
| Hub | `c7904661faefa37e09286780fbde172eac15194d` | [Preparation](https://github.com/iokaio/munarium-platform/blob/c7904661faefa37e09286780fbde172eac15194d/docs/build-plan.md) exists; no platform contract bundle, runtime or tested composition. This is the phase-2 input revision, not its resulting commit. |

Server's inspected [vendored Matrix lock](https://github.com/iokaio/munarium/blob/2c40480fdc2378e66dc23acdfaf82b529b9d22ee/server/contract/matrix/contract.lock)
declares wire contract `0.1.0` and bundle digest
`2f35a515db4501a0320f51335e3d212796f757f06af6f309f8b3f639305ced96`, but its
`source_commit` is `unknown`. FOUNDATION-01 must resolve the publisher/source provenance and
run the owning repositories' compatibility checks before this becomes a composition pin.
This observation neither establishes drift nor authorizes hand-editing the vendored contract.

## Workspace preflight

All twelve required public checkouts were present with their expected origins at inspection:
the hub, Server, Matrix, Registry, Gate, Warden, Council, Harness, Gateway, Sentinel, Assure and
Console. Demo and client-publishing checkouts were also present. This is a dated observation
of a contributor workspace, not a requirement to check out every repository to build a component.

Run the read-only [inventory script](../../scripts/workspace_inventory.py) against an explicit
parent directory to detect missing or incorrectly named clones:

```console
python scripts/workspace_inventory.py --root /path/to/public-checkouts --include-supporting
python scripts/workspace_inventory.py --root /path/to/public-checkouts --json
```

The allowlist contains the twelve core repositories and two optional supporting repositories.
The script does not discover arbitrary siblings, fetch, change Git configuration, or print
working-file contents or unexpected remote URLs. Git may read files to compare status. It reports
full source revisions, branches and
changed-path counts; a dirty checkout is reported, never cleaned. Missing/wrong-origin required
repositories fail the preflight. Optional repositories do not become runtime dependencies.
Clean/process filters and submodule inspection are disabled during status collection to prevent
side effects; counts can conservatively include filtered files and exclude submodule contents.
Presence does not establish freshness, builds, compatibility, release provenance or qualification.
VCP development is suspended as of 6 October 2026. The worthwhile experiment became too expensive
to continue and is unlikely to deliver the desired impact or independently advance the platform;
Ioka is focusing more intensely on Munarium Governance Platform. VCP is not a preflight or delivery
requirement; see the [development focus update](../../README.md#how-the-platform-is-built).

## Historical-plan crosswalk

| Historical text | Current implementation planning treatment |
|---|---|
| Revision 4 sections 3.1, 16.5 and Appendix I describe the Matrix move | The inspected public trees already have the separate layout. Do not repeat extraction, delete trees or republish 1.2.0 from the historical instructions. Confirm release evidence in FOUNDATION-01. |
| Nine license/README skeletons | Component Rust interfaces and build guides now exist; capability remains Planned. Compilation is not a runtime test. |
| S1–S9 list required Server changes | These remain qualification questions until mapped to inspected implementation and actual tests. Do not assume every historical gap is still open or already fixed. |
| Month windows and 1,320 founder hours | Capacity assumptions; the current [work packets](../build-plan.md#work-packets-and-capacity) supply near-term estimation and rebaseline rules. |
| INV-19 first gate is Stage 4 in historical Appendix C | The current delivery plan requires minimum restore safety at Stage 2 before dispatch, and broader recovery exercises at Stage 4. No evidence state advances. |
| Overview paper describes eleven services | Eleven components: Harness is an SDK and Console a human interface; component count is not a process or host count. |
| Revision 4 and the overview paper describe VCP as the primary development environment | Superseded by the 6 October suspension update: VCP development is too expensive relative to its likely impact; Ioka's effort is concentrated on the platform and its delivery does not depend on further VCP development. |

The original plan remains an attributed historical baseline. Current proposals live in the
[decision register](contract-backlog.md) and [build guide](../build-plan.md). This crosswalk
does not claim that the phase-2 proposals have been accepted. The plan and overview paper carry
explicit 6 October updates to distinguish the suspended tooling experiment from the historical
source's development assumptions.

## Qualification still required

[FOUNDATION-01](foundation-01.md) records the subsequent local runs and remaining gaps.
It preserves failed and unrun checks and does not qualify a platform composition.

FOUNDATION-01 must retain commands, toolchain, fixture versions, supported test profiles,
exit status and output references for both foundations. For each S1–S9 requirement, classify
the result as observed-and-tested, partial, absent, failed or not-run, with source and test links.
Record unavailable environments separately. Inspect S8 accounting and S9 execution seams before
factoring code; review public API compatibility and migration ownership. A failed requirement
blocks its consuming packet, not unrelated design work. Use the current owning repositories'
gates; this page supplies no substitute foundation test suite.
