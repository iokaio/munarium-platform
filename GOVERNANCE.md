# Governance

How the Munarium Governance Platform is built and who decides. This file describes the
organization of one: a single founder, assisted by coding agents, with optional reviewers,
sponsors, contributors and deployment partners who strengthen the project without being counted as
its delivery capacity. It says what that organization can and cannot claim.

## Roles

**The founder** (Ioka LLC) owns architecture, scope, repository stewardship, integration decisions
and the final acceptance of changes across the hub and the nine component repositories. The founder
is the sole required builder and maintainer, holds the release credentials and signing material,
and is the accountable human on every merged change. `CODEOWNERS` in every repository names one
owner; it is split when a component gets a second maintainer, not before.

**Coding agents** (VCP, Claude Code, Codex and others) perform bounded implementation,
investigation, test generation, documentation and review tasks. They receive the minimum context and
permissions a work packet needs. Their use changes nothing about repository ownership, contract
versions, test obligations or release authority. A model's statement that tests passed points to
actual commands, exit status and retained output. A second model's review is additional analysis,
not a second accountable person, and the record says so.

**Contributors** submit signed-off pull requests under the process in `CONTRIBUTING.md`. Every
contribution has a human submitter who accepts responsibility for it, a bounded scope, relevant
tests and an ownership and attribution declaration. Contributions that reduce maintenance burden are
prioritized: conformance fixtures, reproducible bugs, compatibility evidence, narrow adapters, clear
documentation. A new supported integration needs a maintainer or an explicit statement that it is
experimental; the process does not turn an unmaintained demo into a silent support obligation.

**Reviewers, sponsors and design partners** are welcome additional capacity. The critical path
contains only work the founder can perform or work for which a reviewer or sponsor has explicitly
committed resources. A sponsor can fund a named milestone, a public adapter, a test environment or an
independent review; the resulting Ioka-owned implementation remains public, and a sponsor's
preference does not confer authority to weaken a core invariant. Enterprise deployments appoint
their own approvers, security administrators and recovery custodians; those roles are not resources
for building the platform.

## The authority boundary in a one-person organization

During development, the founder authorizes an agent-originated change through a separate,
human-controlled release path. The agent cannot possess the release credential, modify the trusted
approval workflow, or replace the test baseline used to judge its own change. That is meaningful
separation between the coding agent and the founder.

It is not independent human oversight of the founder. If the founder designs, writes, reviews and
releases a change alone, the record says so. For a change whose risk policy requires independent
human review, the release obtains that review or remains outside the corresponding production
claim. The software supports stronger separation than the founder's own organization can
demonstrate internally, and the platform never advertises the stronger separation as achieved
until it is.

## Decisions

A cross-component decision (a wire envelope, the request hash, the principal chain, the outcome
vocabulary, a consequence-class rule, a policy-engine choice, a security or protocol semantic) is
made in a **decision record** in this hub before parallel implementation begins. Component
repositories may narrow what they accept; they may not redefine what a contract means. Where
exploration is necessary, candidate branches are labelled experiments and kept out of release
composition.

Decision records are versioned, attributed, and link the requirement, the alternatives considered,
the evidence and the resulting contract or roadmap change. Research citations sit beside the
decisions they inform. A decision that weakens an advertised guarantee is visible in the release
boundary and its evidence, never quietly absorbed.

Breaking interface changes use expand, migrate, remove: a producer adds a compatible capability,
consumers adopt it, the platform composition records the transition, and only then is the obsolete
contract removed under the declared version policy. Agents preparing coordinated pull requests may
not treat a successful change in one repository as permission to merge unverified changes elsewhere.

## The work packet and the limits on parallel work

A work packet identifies the repository and revision, the problem, an approved design or a bounded
design question, permitted files, interfaces that must not change, acceptance tests, and a time or
model-spend limit. Security-sensitive packets also identify forbidden effects: release publication,
policy activation, credential changes, modifications to protected workflows, mutation of the
reference test baseline.

The starting work-in-progress limit is **one major capability slice, one maintenance lane for
released software, and no more than two bounded agent implementation tasks awaiting substantive
review**. The scarce resource is founder attention, not code generation; the limit keeps agent
throughput from creating a review backlog larger than one person can responsibly resolve. It is a
planning choice, revisable after measuring review delay, integration failures and rework.

A weekly review closes or splits oversized packets, reconciles the work ledger and updates the next
acceptance milestone. Monthly reviews report completed capability, review backlog, model spend,
unresolved security issues and the next release gate. The public roadmap shows why an item moved
rather than presenting a delay as an unexplained change in priority. The founder tracks model spend
per accepted change, review hours, rework, escaped defects, security findings, restore success and
elapsed time to a useful capability, disclosing sample sizes; no blanket productivity multiplier is
assumed.

## Releases and their labels

Every release is pinned to an immutable source revision. Containers and packages expose source
provenance and a software bill of materials. A platform release is a composition manifest listing
independently versioned components tested together; a floating `main` is never a compatible
composition. Release labels (planned, experimental, conformance-tested, reference-qualified,
independently reviewed) are statements about evidence, and the composition advertises no stronger
boundary than its weakest required dependency supports.

Release publication, policy activation and changes to protected workflows, branch protection,
ownership, signing material and trusted publishers are outside coding-agent authority. Untrusted
pull-request code never runs with production secrets or publication authority, and the code under
review cannot replace the checks used to approve it.

When capacity is constrained, scope is reduced in a fixed order: connector breadth, SDK breadth, UI
polish, packaging variants and simultaneous adopter commitments first; advanced analytics,
federation and multi-region automation next. Request binding, mandatory evidence, credential
isolation and required distinct authority are never removed to preserve a date.

## Openness and commercial boundaries

All nine components and their Ioka-authored platform features are open source from their first
public commits, under Apache-2.0. There is no code-based Community versus Enterprise boundary for
the planned components; a capability delivered later is deferred, not reserved. Open source does not
require publication of customer records, live credentials, confidential assessments or unremediated
vulnerability details; historical confidential documents receive a publication review before
anything moves here.

Ioka may offer bounded architecture reviews, implementation assistance, training, sponsored
development and support contracts consistent with actual capacity. The first commercial constraint
is capacity, not a paywall. No sales objective implies around-the-clock coverage, independent
dual-human review, or a breadth of qualified integrations the project does not possess. The support
boundary is stated in each repository's `SUPPORT.md`.

## Continuity

The founder is a concentration of architectural knowledge and administrative authority. The
mitigation is documentation, reproducible builds, public source, exportable issues and decisions,
protected recovery material, and a succession procedure a future maintainer can follow. The project
maintains a current release checklist, key inventory, recovery procedure and map of privileged
accounts; recovery secrets remain private and separately protected, and their custody model is
documented without publishing the secrets. A trusted future custodian or independent reviewer is
added when there is an explicit agreement, not listed as a hypothetical safeguard. None of these
measures creates a second available operator today, and this file says so rather than implying one.

## Conduct, security, changes to this file

`CODE_OF_CONDUCT.md` applies in every Munarium repository. Suspected vulnerabilities go to the
private channel in `SECURITY.md`. This file changes only through the owner, by a pull request that
says what changed in the decision process and why.
