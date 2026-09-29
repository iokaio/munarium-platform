## What and why

<!-- One paragraph. Link the issue, and for a cross-component change the decision record this
     pull request adds or implements. -->

## Scope and consequences

<!-- Which documents, contracts, vectors or reports change; which component repositories are
     affected and in what order; which version policy applies. For a status, label or evidence
     change: link the evidence. -->

## Validation evidence and limitations

<!-- Name commands, results and unavailable coverage. A document that claims a capability,
     status or evidence links to what supports it, or does not claim it. -->

## Checks

- [ ] Every commit is signed off (`git commit -s`; the DCO, see CONTRIBUTING.md).
- [ ] `check_license.py`, `scripts/private_material_scan.py` and `scripts/docs_linkcheck.py` are green;
      `gitleaks dir . --config .gitleaks.toml` finds nothing.
- [ ] A cross-component contract or semantic change has, or is, a decision record.
- [ ] A contract change follows the declared version policy (expand, migrate, remove) and its golden
      vectors change with it.
- [ ] No catalog state, invariant evidence field or release label advances without linked evidence.
- [ ] Every page under `docs/` is listed from an index; proposed things are labelled proposed.
- [ ] New source files carry `SPDX-License-Identifier: Apache-2.0` on the first line.

## Disclosure

Answer each; "none" is an answer.

1. **Third-party material** in this pull request (any file, fragment, figure or text you did not write), with its license:
2. **Generated content** (what generated it, from what):
3. **AI-tool provenance** (which tools helped write this, and that you reviewed every line):
4. **Employer or contractual restrictions** on contributing this:

I have the right to submit every file in this pull request under the Apache License 2.0.

## Maintainer self-review

<!-- For a pull request the owner merges on their own review: the compensating control
     for a sole approver. -->

- [ ] Read the whole diff once more after CI went green, as a reviewer would.
- [ ] No credential, hostname, internal path, customer reference or private planning document
      entered the tree; a moved document has its publication review and migration record.
- [ ] Nothing here could be consumed by a deployment as activated policy.
