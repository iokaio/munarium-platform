# Munarium Governance Platform hub release notes

The hub has no release of its own. Once contracts are published, each contract version is recorded
here with its consumers; once a composition is tested, each platform release is recorded here with
a link to its composition manifest and qualification report. Until then the entries record the
repository's history.

## Unreleased

- **Build preparation.** Added an indexed delivery guide, system boundaries, contract backlog,
  foundation requirements and proposed scaffold decision. Linked the nine component build plans.
  The hub stays documentation-only with no Rust source or Cargo workspace; catalog states,
  invariant evidence and release labels are unchanged.

- **28 September 2026.** Repository created as a new public repository, not by renaming the private
  planning repository, with an Apache-2.0 `LICENSE` and a one-line `README.md` carrying the GitHub
  description, "The central architectural design hub for Munarium Governance Platform". No private
  history is carried here.
- **Governance and contribution files.** `README.md` with the platform overview, the repository
  map, the component catalog at "repository created", the invariant catalog INV-01 to INV-22 with
  every evidence field blank, the release labels and the six-stage roadmap; `GOVERNANCE.md`;
  `NOTICE`; `SECURITY.md`; `CONTRIBUTING.md`; `SUPPORT.md`; `CODE_OF_CONDUCT.md`; `TRADEMARK.md`;
  `AGENTS.md` and its identical copy `CLAUDE.md`; issue and pull request templates; `CODEOWNERS` and
  `FUNDING.yml`; the DCO and repository-hygiene workflows with the checks they run
  (`check_license.py`, `scripts/private_material_scan.py`, `scripts/docs_linkcheck.py`, gitleaks).
  `LICENSE` replaced with the canonical Apache-2.0 text so that the licence gate can pin it; the
  copyright line moved to `NOTICE`.

### Status

Hub created. No contract, decision record, composition manifest or qualification report exists yet;
the proposed directories in the README are added with their first reviewed content.
