# Support

The Munarium Governance Platform hub is open source under the Apache License 2.0
([LICENSE](LICENSE)). **The license includes no support from Ioka LLC**, and nothing in this
repository is a support commitment.

## Where the platform stands

The foundation, Munarium Server and Munarium Matrix, is released software with its own support
boundary, stated in [iokaio/munarium](https://github.com/iokaio/munarium) and
[iokaio/munarium-matrix](https://github.com/iokaio/munarium-matrix). The nine new components are
public skeletons at **repository created**; there is no platform release, no published contract and
no tested composition. [README.md](README.md) says what exists and what does not.

## What is available to everyone

- **Questions** that span components, or about the architecture, roadmap and contracts, go to
  GitHub Discussions on this repository. A question about one component goes to that repository.
- **Defects and design findings** go to GitHub Issues: a decision record that contradicts a
  contract, a golden vector that two clients cannot both satisfy, a catalog entry the evidence does
  not back, a dead link. Say which document or contract version and what you expected it to say.
- **Cross-repository features** have one hub issue linking their component issues, required order,
  test fixtures and acceptance evidence. Open it here.
- **Vulnerabilities** go to the private channel in [SECURITY.md](SECURITY.md), never an issue.
- **Compatibility** is recorded in the platform composition manifest once one exists; until then,
  each component README states the contract versions it supports, and none does yet.

Issues are read and triaged by one maintainer. There is no response-time commitment on this
repository, and a finding may be closed as "recorded, not scheduled", which is a truthful answer
rather than a dismissal.

## The support boundary in the first year

Asynchronous community assistance, reproducible issue reports, documented reference
configurations, and a limited number of scheduled design-partner sessions: no more than two active,
high-touch design partners at once. Six technically relevant enterprise evaluations over the first
year are an outreach and learning target, not six production contracts, six founder-operated
installations or six qualified stacks. A useful design partner supplies an owner, a test
environment, a narrow workflow, a review cadence and permission to share sanitized lessons; an
adopter that cannot may remain a self-service evaluator. Enterprise production operation remains the
adopting organization's responsibility unless a separate, sustainable agreement explicitly says
otherwise.

## What is not

A production support relationship, a managed service, or a certification. Ioka may offer bounded
architecture reviews, implementation assistance, training, sponsored development and support
contracts consistent with actual capacity; a sponsor can fund a milestone, an adapter, a test
environment or an independent review, and the resulting Ioka-owned implementation remains public.
A support badge or conformance report describes the scope of testing and the party responsible; it
never implies a general security certification. Munarium Enterprise is a separate, proprietary
distribution built on Server and Matrix; the platform components reserve nothing for it.

Commercial enquiries go to **info@ioka.io**.

## Running it yourself

When there is a composition to run, everything needed to operate it without Ioka will be public:
the local development recipe, the single-cell reference profile, the runbooks, the composition
manifest and the integration suite that tells you whether your deployment behaves. The core sample
suite will run without paid cloud services wherever possible, with provider-specific tests as
separate, labelled jobs. That is deliberate.
