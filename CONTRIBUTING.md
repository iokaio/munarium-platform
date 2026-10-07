# Contributing to the Munarium Governance Platform hub

Contributions are welcome from anyone. What follows is the whole process; there is no contributor
license agreement to sign. This repository holds architecture, decision records, contracts and
evidence rather than a runtime, so most contributions are documents, schemas and fixtures, and the
review asks whether a document says only what the evidence supports.

## Rights and license

- **Every commit carries a Developer Certificate of Origin sign-off**: `git commit -s`, which adds
  `Signed-off-by: Your Name <you@example.com>`. By signing off you certify the
  [DCO](https://developercertificate.org/), that the work is yours to submit under this
  repository's license, or that you have the right to submit it. A pull request with an unsigned
  commit fails its check.
- **Accepted work is Apache-2.0**, the license of the whole repository ([LICENSE](LICENSE)), by
  section 5 of the license itself: a contribution intentionally submitted for inclusion is licensed
  under the same terms, copyright and patent alike. That is why no CLA exists; a CLA would add the
  right to relicense your contribution later, and that right is not wanted.
- Research material, standards text and other people's work keep their own terms. Cite them;
  do not copy restricted text into the tree. A contribution changes nothing about Ioka's
  trademarks ([TRADEMARK.md](TRADEMARK.md)) or the support boundary ([SUPPORT.md](SUPPORT.md)).

## Disclosure

The pull request template asks four questions; answer each, and "none" is an answer:

1. **third-party material**: any file, fragment, figure or text you did not write, with its license;
2. **generated content**: what generated it, from what;
3. **AI-tool provenance**: which tools helped, and that you reviewed every line;
4. **employer or contractual restrictions** on what you may contribute.

You must have the right to submit every file in the pull request. Every contribution has a human
submitter who accepts responsibility for it.

## Process

1. Fork the repository (maintainers: a topic branch) and make the change.
2. Run the gates below. Every new source file carries `SPDX-License-Identifier: Apache-2.0` on its
   first line, the second after a shebang or an XML declaration.
3. Open a pull request against `main`. CI runs offline with no private credential.
4. A code owner reviews ([.github/CODEOWNERS](.github/CODEOWNERS)); Ioka squash-merges.

### Decision records

A change to a cross-component contract or semantic (a wire envelope, the request hash, the principal
chain, the outcome vocabulary, a consequence-class rule, a policy-engine choice) is a **decision
record** first, under `docs/decisions/` once that directory exists. The record names the
requirement, the alternatives considered, the evidence, the consequences for each affected
repository and the version policy the change follows. Component pull requests land only after the
record is merged. The [Stage 1 authorization](docs/stage1-authorization.md) permits
experimental implementation and testing against recorded proposals while formal
acceptance remains pending; it does not authorize merging or release composition.
[GOVERNANCE.md](GOVERNANCE.md) describes who decides.

### Contracts

`contracts/` is normative once it exists. A change is a version bump under the declared policy and
follows expand, migrate, remove: a producer adds a compatible capability, consumers adopt it, the
composition records the transition, and only then is the obsolete contract removed. Golden vectors
change with the contract they exercise and never alone. Generated bindings are regenerated from the
published contract and carry its digest; they are never hand-edited.

### Evidence and status

The component catalog, the invariant catalog, the roadmap and every qualification report state only
what the linked evidence supports. A status advances in the pull request that adds the evidence. A
blank evidence field means unverified; a failed test or unresolved finding stays in the record, and a
release narrows its scope rather than relabelling a failure.

## Gates

| Gate | Command |
|---|---|
| Licence and notices | `py check_license.py` |
| Private material | `py scripts/private_material_scan.py` |
| Documentation links and indexes | `py scripts/docs_linkcheck.py` |
| Secret scan | `gitleaks dir . --config .gitleaks.toml` |
| Whitespace | `git diff --check` |

Use `python` or `python3` where `py` is unavailable. Schema validation, golden-vector checks and the
integration job are added to this table, and to CI, in the pull request that adds the content they
check. The CI workflows under `.github/workflows/` are the source of truth for what runs.

Rules the gates and reviewers enforce that are easy to trip:

- **Every page under `docs/` is listed from an index**, and every relative link resolves.
- **Nothing here is runtime authority.** A document, schema or example that a deployment could
  mistake for an activated policy, or that would make a deployed control depend on GitHub, is
  declined.
- **Private material stays private.** Planning documents move here only after a publication review;
  a migration record names each moved document and its source revision. Customer references,
  credentials, private endpoints, internal work-item identifiers and the private research
  vocabulary the scanner names do not enter the tree.
- **Attribution is preserved.** Research that informed a decision is cited beside the decision,
  with the DOI or stable locator its author provides, and without implying endorsement.
- **Proposed is labelled proposed.** Directory layouts, schemas, budgets, schedules and release
  criteria that are not yet decided say so.

## Conduct and venues

[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) applies everywhere in this project. Questions go to GitHub
Discussions, defects and design findings to Issues, and suspected vulnerabilities to the private
channel [SECURITY.md](SECURITY.md) names, never to a public issue.

## Protected files

Only Ioka changes `LICENSE`, `NOTICE`, `TRADEMARK.md`, this file, `GOVERNANCE.md`,
`CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, `AGENTS.md` and `CLAUDE.md`, anything under
`.github/`, the invariant catalog, `contracts/` and `releases/` once they exist, and any signing or
release configuration. A pull request that touches them is declined unless a maintainer opened it.

The [Stage 1 development authorization](AGENTS.md#stage-1-development-authorization)
is the maintainer's explicit direction to prepare the scoped guidance, build/test
workflow and contract candidate changes. Contributors carrying out that direction
may edit those files; protected-file ownership, review and merge requirements still
apply. It grants no release authority or permission to weaken approval controls.
