# ADR 0016: bounded dynamic release admission

**13 October 2026; experimental implementation directed; acceptance pending.**
This refines DYNAMIC-01 under [ADR 0015](0015-stage2-linux-qualification.md).
Baseline: merged Gate `d030c5e8b3f94974972e2a02c459886647e86a59`; hub's recorded
[Linux evidence](../stage2-implementation.md#linux-evaluator-worker-13-october-2026).
The agent-isolation packet is independently reviewed and does not establish dynamic
evaluation. Keep candidate bytes, golden vectors and historical acceptance pins.

## First supported input boundary

Add an experimental `propose` action to Gate's existing authenticated action adapter.
It accepts tenant, enrolled operation/attempt IDs and proposed parameters only.
The first capability remains `release.publish_approved_artifact` against a disposable
target. Exact actor/origin/task/delegation, target/precondition, validity window,
activation/recovery and evidence context come from current signed owner enrollment.
Callers cannot supply any of those authoritative fields, URLs, hashes or credentials.
Keep the existing prepared-request API compatible and separately identifiable.

This profile supports dynamic parameter/policy evaluation within pre-enrolled task
slots. It does not admit arbitrary task creation, evidence derivations, destinations,
attachments, identities or consequence modifiers. Narrow unsupported semantics
explicitly instead of synthesizing missing authority. A broader proposal surface
requires its own recorded profile and qualification evidence.

## Independent resolution and evaluation

Gate verifies the actual mTLS peer's current signed enrollment, not a principal in
caller parameters. The enrolled qualified actor/origin and requester chain retain
their Stage 2 meaning. It obtains a current Warden assertion for Registry resolution,
fetches the Registry-verified exact manifest and independently checks Registry's
installed head against Gate's activated artifact set. Candidate inventory access
alone cannot establish activation. Retirement, incompatibility and missing heads refuse.

Resolve the exact policy artifact from Registry's current Server-signed artifact
registration, verify its existing decision-policy digest and match the activated set.
The policy pins native engine/version/binary, worker/capabilities, parameter schema
and supported determining-rule mappings. Gate's actual evaluator must match those
pins. A pure policy cannot obtain additional authority through network/time built-ins.

The first evidence adapter reads immutable canonical test-result source bytes from
current Server-signed source enrollment. Verify their content hash against the
context's scoped source/revision/verifier/trust/freshness metadata. Derivation is
`test-result` version 1, field `tests.passed`, requiring a boolean and an artifact
digest matching the proposed artifact. Only this explicitly enrolled source profile
is supported; neither agent assertions nor arbitrary retrieved memory become proof.
Unknown/missing/stale lineage refuses. The record must disclose this authority-bound
source profile and cannot claim general Server/Matrix evidence integration.

Validate parameters against the Registry-admitted immutable schema and its digest.
The first release manifest must name the exact operation, tenant, disposable
environment, target, credential audience, consequence and required approval. Reject
unsupported modifiers or obligations rather than dropping them. The native input
includes the validated intent/context and independently derived evidence values.

Validate the complete closed evaluator result: boolean allow/forbid, admitted unique
determining rules, exact supported predicate keys and empty diagnostics. Any forbid
wins. Policy errors, substitution and unsupported output cannot become permission.
Retain the mandatory distinct-approval, recording, capacity and credential-custody
obligations in an approval-required decision; a denied decision has no executable
obligations. Policy cannot reduce required controls or the manifest's consequence.

## Durable source and current-use admission

Gate computes canonical intent/context/request/decision digests. Recheck the same
current authority after resolution/evaluation and before immutable recording. Archive
request and decision through authenticated Server action records, then persist the
exact source in Gate's journal. Exact retries recover original bytes; changed
parameters or context conflict. A denial can be retained/explained without a grant.

Council, Warden and connector obtain the retained owner source through the existing
authenticated lookup path. Claims, consumption and final send compare that source
with current enrolled identity/context/policy/evidence, active artifacts and epochs.
They cannot replace it by reevaluating a changed proposal, silently renew expiry or
accept a caller-provided result. Preserve exact approvals/custody, cancellation,
capacity/fencing, one-shot send and unresolved outcomes. Historical lookup/replay
does not create execution authority.

No distributed transaction is invented: archive success followed by journal failure
remains recoverable only through exact immutable retries. No uncertain target action
is repeated to recover a missing decision or source response.

## Packets and evidence

1. Gate: immutable source lookup and bounded dynamic materialization/resolution,
   focused tests, docs and additive native coverage. Existing prepared routes,
   Windows worker, native Linux controls and PostgreSQL suites remain enabled.
2. Harness: real Linux evaluator/service integration and agent-originated parameters,
   exact approval-to-effect chain, replay/restart/conflict histories and independent
   target observations. Preserve the existing activation and isolation histories.

Intake uses actual full base/source/vector/evaluator pins and the owner/availability,
resource/expiry/cleanup fields in ADR 0015. Founder remains accountable reviewer;
independent human acceptance is pending. Stop each bounded subpacket for review/
re-estimation at the existing eight-hour ceiling. Component evidence must distinguish
portable unit checks from native evaluation and full real-service effects.

Negative cases include substituted parameters/identity/context, wrong or inactive
manifest, retired artifacts, source digest/derivation/type/freshness failures, policy
deny/forbid/diagnostics, unknown obligations/rules, worker/binary substitution,
missing custody and unavailable dependencies. Adjacent valid controls require one
native dynamically evaluated approval-required proposal and one approved effect.
An API success without the expected independent effect count fails the oracle.

This implements the bounded dynamic reference profile, not general production
execution, independent human oversight or safe restored-store reopening. Recovery
still requires its own concrete cutoff protocol before consumers implement it.
