# 0001: implementation scaffolding without shared runtime semantics

**State:** Proposed for maintainer review.

**Date:** 28 September 2026.

**Scope:** The nine new component repositories and the documentation-only platform hub.

## Context

The [platform plan](../platform-plan.md), sections 3, 7–15 and Appendix B, calls for
independently useful components with explicit boundaries and acceptance specifications.
Development preparation needs buildable source structure without implying implemented
authority, credentials, contracts or a compatible platform release.

The requested preparation adds Rust source to each new component and keeps the hub strictly
for architecture and design documents. Existing governance, notices and checks are preserved.

## Proposed structure

- One independent, dependency-free Rust library per component, rooted at `src/lib.rs`.
- Component-specific modules declare provisional local interfaces with associated input/output
  types; they supply no implementations and define no shared wire representation.
- No binaries, listeners, async runtime, storage backend, authentication library, cryptography,
  provider SDK, policy evaluator, web framework or sibling path dependency is selected.
- Cargo packages use `0.1.0-dev` solely as unreleased package metadata and `publish = false`.
  This is not a contract version, release tag or capability label.
- Rust 1.98.1 is the build-check baseline; Cargo declares Rust 1.98 and edition 2024. Lockfiles
  contain only their root package. Dependencies are reviewed and pinned when implementation needs them.
- Unsafe code is forbidden and public interface documentation is required in each library.
- Automatic component Rust checks supplement existing hygiene and DCO checks, using read-only
  permissions and no release or provider credentials.
- Console's Rust modules cover application/service boundaries; browser rendering is a later
  design choice. Harness's Rust base prepares contract fixtures; the first application binding
  is a separate choice. Gateway remains an extraction from Server, not a new accounting engine.
- The hub contains no Rust source, Cargo manifest, workspace or runtime. Integration scenarios,
  contract requirements and deployment boundaries are documented here; executable component
  implementations stay in their owning repositories.

## Alternatives considered

| Alternative | Reason to defer or reject |
|---|---|
| One shared hub Cargo workspace | Would make the architecture hub a runtime source and couple independent component builds |
| Copy Action/Grant/Approval structs into every crate now | Would independently freeze unresolved wire, hashing and identity semantics |
| Add runnable placeholder servers | Could imply useful runtime capability and introduce an accidental traffic/credential surface |
| Choose frameworks and external crates now | No implemented use case yet justifies their dependency or compatibility cost |
| Documentation with no Rust source | Does not meet the requested component build preparation |

## Evidence and limits

The observable result is source modules, manifests, indexed design pages and local build checks.
There are no runtime or conformance tests yet. Compilation validates interface declarations only.
The component catalog remains **repository created**, capabilities remain **Planned**, and every
invariant still needs actual implementation evidence. No new contract bundle or composition exists.

This record does not approve a policy engine, transaction protocol, deployment profile, release,
publication or activation. All such work follows its own accepted design and review.

## Consequences and next decisions

Internal traits may change freely before a released API exists. Once concrete shared types are
needed, the [contract backlog](../architecture/contract-backlog.md) must produce reviewed
definitions and vectors first. Runtime libraries have one component/foundation owner;
generated bindings carry the published contract digest. Future breaking changes follow
expand, migrate, remove.

Each component's build plan supplies a first bounded packet and acceptance criteria.
The [platform build plan](../build-plan.md) supplies dependency order and composition gates.
