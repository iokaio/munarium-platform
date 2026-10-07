# Stage 2 contract candidate packet

**Directed 7 October 2026; candidate preparation, not runtime activation.** The
maintainer reported reviewing and merging hub PR 13, then instructed “Proceed as
planned” after the proposed next step of dispositions, profile selection and
versioned schema/vector preparation. The exact design input is hub
`8a58292e55d9785d57763524f849d9aa0c13a77b`; the reviewed PR head was
`36a3826abcec0742f3788dc3c2d96eb9e630351f`.

## Recorded disposition and selected scope

| Input | Disposition for this packet |
|---|---|
| Stage 1 pins and acceptance evidence | Retain the exact decision-only baseline and historical observations. No new runtime qualification or acceptance of a permanent platform-wide schema is inferred. Formal per-contract acceptance fields remain pending. |
| ADR 0010/0011 at the merged revision | Use the reviewed proposals as the directed basis for concrete candidate generation, including the second-pass corrections. New candidate bytes still require their own disposition. |
| Reference effect direction | Select single-cell Linux isolation, PostgreSQL action journal, distinct human approval and the synthetic publication target for subsequent qualification planning. Exact runtime version pins, environment availability and evidence remain open. |
| Current executable scope | Offline schema generation, fixed vectors, portable shape/semantic oracle, independent standards-validator comparison and committed-source export. No component runtime changes, credential custody or target sends. |
| Later component work | Keep Gateway, Sentinel, Assure, Console, federation and general Matrix/export work in their existing stages. Preserve their contract boundaries in the new candidate. |

This is a record of the supplied direction, not an invented human sign-off on
new wire bytes or an independent review. The [Stage 1 acceptance packet](architecture/stage1-acceptance.md)
retains its exact-revision disposition table. The
[concrete candidate ADR](decisions/0012-stage2-candidate-profile.md) names additional
wire choices for review rather than silently adding them to the approved input.

## Deliverable and owner

One hub-owned candidate under [stage2-v1](decisions/stage2-v1/README.md): request,
decision, approval, activation/receipts, shared event/action payloads and exact
acknowledgements; immutable profile and golden digests; refusal vectors; generator,
validation and exporter. No published contract or catalog status changes.
The founder remains accountable owner/reviewer; no second human is implied.

The generator creates only a new candidate and refuses to replace an existing
lock. Its check mode reproduces the pinned outputs without changing them. The
exporter accepts only committed, unchanged candidate inputs and preflights all
destination collisions before writing. Consumers use a separate namespace and
must record their own compatibility evidence; no re-vendoring into live services
is needed until the versioned candidate is reviewed.

## Next gate

Review the exact candidate digest and ADR 0012 with the selected profile, including
remaining API/signature/provider details. Then create bounded Server, Council,
Registry, Gate, Warden and Harness implementation packets from accepted inputs.
Runtime intake must name exact dependency versions, responsible environment owner,
observed availability, resource/cost limits, expiry, custody, test oracles and
cleanup. None of those operational facts is supplied by an offline fixture.

Schema/refusal checks do not establish concurrent consumption, reliable outboxes,
network isolation, propagation or restore safety. Retain H03-01–13 and uncovered
EV cases as required future work. Publication for code review is not a contract
release, installation, activation or effect authorization.

## Candidate pin and observed validation

The new aggregate candidate SHA-256 is
`8aca66588c87107a0c7a7720c68f921dfd2bdcaecf6433728afa4b1c51420aa6`.
It covers the generated schema/profile/vectors and semantic README, using the
bundle lock's LF convention. There are 19 base records and 47 mutation/context
cases: 45 refusals and two accepted recovery/refresh cases. These are offline
examples, not 47 deployed integration scenarios.

Local checks on 7 October passed: all 73 Python unittest methods (60 existing and
13 new), deterministic candidate reproduction, and 333 independent Draft 2020-12
shape comparisons with `jsonschema` 4.25.1. The comparison is independent of the
portable shape checker, not an independent language implementation or human review.
License, documentation link/index and worktree private-material checks passed;
the local gitleaks executable was unavailable. Existing Stage 1 schema/vector/lock
files and acceptance pins remained unchanged. CI remains enabled independently.

The review exceeds 500 non-generated changed lines because the closed schema
generator, fixture semantics, negative controls and safe exporter must be reviewed
together. The four generated JSON files account for 4,450 lines and are covered
by exact reproduction, lock verification and fixed-vector checks. Consumer/runtime
implementation is excluded and will receive separate bounded PRs. No operational
environment, identity or secret was created; disposable validation/export folders
are temporary local resources, not retained service evidence.
