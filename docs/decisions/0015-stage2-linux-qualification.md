# ADR 0015: Linux execution qualification and recovery packets

**13 October 2026; implementation directed, contract acceptance pending.**
The maintainer directed implementation, testing, signed-off commits, pull requests,
exact-head CI verification and squash merging of the next-step plan. Supporting
build/test workflows are in scope. Releases, production trust, paid resources and
acceptance of an unidentified wire revision remain outside this direction.

## Problem and baseline

The [8 October execution record](../stage2-implementation.md#live-execution-review-packet-8-october-2026)
implements prepared synthetic requests, approval, activation, journaling, grant/
credential custody, one-shot admission, target observation and snapshot quarantine.
Its evidence retains `qualification:false`. The [architecture review](../architecture/architecture-review.md#10-review-findings-and-completion-gates)
identifies physical isolation, dynamic evaluation and reconciled reopening as P0 gaps.

Verified merged implementation inputs on 13 October:

| Owner | Source | Evidence |
|---|---|---|
| Hub | `c9c381b73b3f905ded5a480586d6bf7536047984` | [PR 21](https://github.com/iokaio/munarium-platform/pull/21) |
| Gate | `074bcf3071a5dc91953b6d334bf05cfb944b5721` | [PR 5](https://github.com/iokaio/munarium-gate/pull/5) |
| Warden | `1ace7767087472b7f9ed451e105b755f600c8fa8` | [PR 6](https://github.com/iokaio/munarium-warden/pull/6) |
| Council | `8eeca60146aa33e1bfcd679e3074c29991910a08` | [PR 3](https://github.com/iokaio/munarium-council/pull/3) |
| Harness | `67ba9cfb270df08a0353f3b1eda4d37f4843a987` | [PR 5](https://github.com/iokaio/munarium-harness/pull/5) |

Pin the actual hub, Registry and Server bases at each packet intake. Existing
foundation, Registry v2, Stage 1 and Stage 2 v1 candidates/vectors remain immutable.
New wire semantics require a new version and documented export/re-vendoring. Keep
historical acceptance pins; merging does not accept contracts or advance catalogs.

## Linux evaluator choice

Keep OPA/Rego as the single experimental engine. Pin Linux amd64 OPA 1.21.1 by
its independently verified SHA-256; record binary, worker, capabilities and policy
digests. Linux adds a separate profile; Windows Job Object controls stay enabled.

Use a delegated cgroup v2 subtree owned by the evaluator service, with a fresh
child per invocation. Before executing OPA enforce 64 MiB aggregate resident memory,
zero swap and a bounded process count. Preserve the 100 ms evaluation deadline,
bounded input/output, strict built-in errors and the existing pure built-in allowlist.
Bound supervisor lifetime and kill all invocation descendants on timeout/error,
then remove only that child. Missing controllers, delegation, cleanup or verified
bounds refuse. Agent data cannot configure executables, workers, cgroups or limits.

The supervisor is trusted Gate infrastructure. Resource bounds do not sandbox a
malicious substituted executable or establish agent isolation. Verify both worker
and binary pins. An address-space limit alone neither bounds aggregate resident
memory nor accommodates Go's virtual-memory reservations. An unbounded subprocess
discards existing guarantees; per-evaluation container startup adds lifecycle cost.
Cgroup v2 supplies hierarchical accounting and whole-group cleanup through the
[kernel interface](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html).

Native allow/deny and small-work positive controls must pass. Negative controls
cover missing/type-invalid inputs, forbidden network/clock built-ins, substitution,
excessive work, memory pressure, missing delegation and descendant cleanup. Check
actual configured bounds and kernel counters; arbitrary process failure cannot
prove a particular resource limit.

## Dynamic admission and physical isolation

Keep prepared requests compatible. The new experimental dynamic adapter resolves
current identity, activated Registry manifest/policy and authoritative evidence
independently, validates intent and computes hashes in Gate. Callers cannot supply
authoritative context, endpoints, lineage, consequence, hashes or approval.
Evaluation errors and unsupported obligations refuse. Bind immutable request and
decision to Council approval and the existing claim/consumption/final-send path.
Current authority, retirement, epochs, exact custody, cancellation, expiry and worker
fencing still apply. A permit alone cannot send. Version any required new wire bytes
before consumers; do not hand-edit vendor contracts.

Use the [single-cell local profile](../architecture/reference-profile.md), synthetic
identities/target and immutable runtime inputs. Agent containers have no checkout,
home, container-socket or production-secret mounts; permit only declared network
edges. Owner storage and migration roles stay separate; the connector has no journal
write credentials. Harness probes target mutation, broker, databases, active authority,
host/metadata and secret mounts from the actual agent environment. API refusal
supplements physical denial. A shared container network alone is insufficient.
The observer has separate read-only target access. Host administrators remain trusted;
distinct synthetic accounts do not prove independent human oversight.

## Recovery design boundary

Record the concrete recovery/cutoff protocol before owner implementation. Restores
default to quarantine. External recovery generation, retained Server custody and
target floor survive the journal snapshot. Startup refuses stale/incomplete state;
an undisclosed rollback cannot regain a send opportunity from a consistent old store.

Governed reopening requires old-dispatcher exclusion, independently retained Server
cutoff, relevant consumption/cancellation/reservation/outcome facts, target observations,
new recovery epoch and floor acknowledgement. Reconciliation is durable/resumable;
missing/conflicting facts keep dispatch closed. Historical outbox delivery retains
original evidence without new execution authority. Boolean resume and timers are
insufficient. No-effect settlement/attempt closure need separate explicit evidence
rules; unresolved capacity is never silently refunded and uncertain sends never repeat.

## Bounded packets and acceptance

The founder is accountable owner/reviewer; independent human review remains pending.
One owner edits hub/Server at a time; at most two implementation tasks await review.
Re-estimate each subpacket after eight focused implementation hours or a failed
critical oracle. This ceiling is a review boundary, not a completion estimate.
No external model calls or paid resources are authorized.

| Packet / owner | Permitted files/work | Exit and evidence |
|---|---|---|
| LINUX-01 / Gate | Linux worker/controls, relevant OPA adapter, docs and additive test workflow | Pinned native positives, built-in/resource/substitution controls and cleanup; component PR and hub evidence update; preserve Windows tests. |
| ISOLATION-01 / Harness | Disposable Linux recipe, exact artifact preparation, agent probes, observer and additive composition workflow | Actual denied edges/mounts and retained activation/execution histories; component run records identify omissions. |
| DYNAMIC-01 / Gate and Harness | Recorded dynamic adapter and synthetic request-to-effect tests | Policy/evidence refusals and approved dynamic effect through existing transactions; independent target counts. |
| RECOVERY-01 / hub then owners | Concrete protocol first; additive persistence/adapters and restore histories | Real pre/post-effect restores, missing-evidence refusal, stale-worker exclusion and reconciled reopening. |
| CLOSE-02 / Harness and hub | Remaining H03/REF matrix and installation/investigation/teardown docs | Pinned reproducible results, failed/unavailable cases and separate human dispositions. |

Each intake records full base SHA, contract/vector/evaluator digests, exact commands,
environment, owner/availability, cost authority, resource ceiling, expiry, teardown
and evidence destination before live qualification. Existing local/CI hosts may run
disposable synthetic tests. Report unavailable local Linux coverage and exercise
exact-head hosted CI. Preserve signing policy, ownership, release workflows, scanner
rules and all existing gates. Candidate acceptance and qualification remain pending
until their exact evidence and human dispositions are supplied.

After Stage 2's exit gate continue Gateway/S8, Sentinel/S6 and Console, then Assure/S5
in the [build sequence](../build-plan.md#dependency-sequence-and-exit-evidence).
