# Security

Do not file a vulnerability as an issue or a pull request.

Report a suspected vulnerability in anything in this repository, or anything that crosses Munarium
repositories, privately, by either route:

- GitHub's private vulnerability reporting ("Report a vulnerability" under the Security tab), or
- email to **info@ioka.io** with "security" in the subject.

Say what you found, where, and how to reproduce it. Do not include live credentials, customer data,
or a proof of concept run against a system you do not operate. You will get an acknowledgement
within two business days, and a fix, or a recorded decision, on the affected path before any related
release. Credit is given if you ask for it.

## Supported versions

The hub has no release of its own. Its contracts, once published, are versioned, and a platform
release is a composition manifest naming component versions tested together. A vulnerability in a
component's code is fixed in that component's repository under its own supported-versions rule;
report it there, or here, and it is routed. A vulnerability in a published contract or golden
vector is fixed here, re-published under the declared version policy, and its consumers are named
in the record.

## What matters most here

- **A contract ambiguity that lets two components disagree about authority**: a canonicalization
  rule two clients implement differently, a principal-chain shape that admits a self-reported
  actor, an outcome vocabulary that lets unresolved read as retryable, a grant or approval shape
  that does not bind what it must.
- **A gap between what a release advertises and what its evidence supports**: a composition
  manifest, qualification report or component-status entry that claims a profile, capability or
  label the evidence does not back.
- **A path by which this repository becomes runtime authority**: anything that would let a
  deployed Registry, Council, Gate or Server treat a hub branch, document or artifact as an
  activated policy without the deployment's own admission and authority checks.
- **A decision record, contract or golden vector changed without the version policy**, or a change
  to the repository's own CI, branch protection or ownership that would let untrusted pull-request
  code acquire secrets or replace the checks used to approve it (INV-21).
- **Private material in the public tree**: planning documents that did not pass publication review,
  credentials, customer references, restricted standards text.

## What is deliberate, and is not a defect

- **The hub is documentation and contracts, not a service.** That nothing here listens, enforces or
  authenticates is the design; a deployment's controls execute pinned policy whether or not GitHub
  is reachable.
- **The catalog and invariant tables say "repository created" and carry blank evidence fields.**
  Blank means unverified, not passed, and the README says so. A report that the platform "claims
  capabilities it has not built" describes a claim the hub does not make.
- **The founder's own operation cannot demonstrate independent two-human review.** `GOVERNANCE.md`
  states that limit; a release that requires such a quorum obtains it externally or stays outside
  the corresponding production claim.

## Secrets

If you have committed a token or key, treat it as compromised: rotate it first, then report it.
