#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generate a separate inert Stage 2 candidate; existing locks are immutable."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs/decisions/stage2-v1"
PROFILE = "stage2-single-cell-v1"
MAX_INT = 9007199254740991
ID = dict(type="string", minLength=1, maxLength=128, pattern="^[a-zA-Z0-9][a-zA-Z0-9:._/-]*(?![\\s\\S])")
HASH = dict(type="string", minLength=71, maxLength=71, pattern="^sha256:[0-9a-f]{64}$")
UINT = dict(type="integer", minimum=0, maximum=MAX_INT)
POSITIVE = dict(type="integer", minimum=1, maximum=MAX_INT)
PARTICIPANTS = ["gate", "registry", "server", "warden"]
OWNERS = {"approval-recorded": "council", "claim-created": "gate", "grant-issued": "warden",
          "consumption-reserved": "gate", "predispatch": "gate", "send-intent": "gate",
          "outcome": "gate", "reconciliation": "gate"}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


def digest(domain, value):
    return "sha256:" + hashlib.sha256(f"munarium:stage2:{domain}:v1\0".encode() + canonical(value)).hexdigest()


def obj(**properties):
    return dict(type="object", properties=properties, required=list(properties), additionalProperties=False)


def arr(items, minimum=0, maximum=32):
    return dict(type="array", items=items, minItems=minimum, maxItems=maximum, uniqueItems=True)


def enum(*values):
    return dict(type="string", enum=list(values))


def const(value):
    return {"type": "string" if isinstance(value, str) else "integer", "const": value}


def ref(name):
    return {"$ref": f"#/$defs/{name}"}


def nullable(value):
    return {"anyOf": [value, {"type": "null"}]}


def record(record_type, **properties):
    return obj(schema_version=const(1), type=const(record_type), profile=const(PROFILE), **properties)


def schema():
    defs = {"scope": obj(domain=ID, tenant=ID, deployment=ID, cell=ID)}
    for kind in ("operation", "attempt", "task", "target", "approval", "transition", "claim", "grant",
                 "invocation", "reservation", "stream", "ledger", "event", "evidence", "authority"):
        defs[kind + "-ref"] = obj(scope=ref("scope"), kind=const(kind), id=ID)
    defs["principal"] = obj(scope=ref("scope"), subject=ID, subject_generation=POSITIVE,
                            kind=enum("human", "agent", "service"))
    defs["task"] = obj(root=ref("task-ref"), parent=nullable(ref("task-ref")),
                       agent_release=nullable(HASH), agent_instance=nullable(ID))
    defs["evidence"] = obj(source=ref("evidence-ref"), revision=POSITIVE, content_digest=HASH,
                           field=ID, derivation=ID, derivation_version=POSITIVE, observed_at=UINT,
                           expires_at=UINT, trust=enum("verified", "untrusted", "unknown"),
                           verifier=ref("authority-ref"))
    defs["intent"] = obj(actor=ref("principal"), origin=ref("principal"), delegation_digest=HASH,
                         task=ref("task"), target=ref("target-ref"), environment=const("disposable"),
                         capability_operation=const("release.publish_approved_artifact"),
                         parameter_schema_digest=HASH,
                         parameters=obj(artifact_digest=HASH, destination=const("synthetic-release")),
                         attachments=arr(obj(digest=HASH, bytes=UINT, media_type=ID), maximum=8),
                         target_precondition=obj(version=POSITIVE, content_digest=HASH))
    defs["context"] = obj(activation=obj(owner=const("registry"), scope=ref("scope"), revision=POSITIVE),
                          recovery=obj(scope=ref("scope"), revision=POSITIVE),
                          authority_pins=arr(obj(owner=ref("authority-ref"), revision=POSITIVE), minimum=1),
                          manifest_digest=HASH, policy_digest=HASH, evaluator_profile_digest=HASH,
                          mode=const("enforce"), evidence=arr(ref("evidence"), minimum=1),
                          valid_from=UINT, expires_at=UINT)
    defs["action-request"] = record("action-request", operation=ref("operation-ref"), attempt=ref("attempt-ref"),
                                     intent=ref("intent"), intent_digest=HASH,
                                     context=ref("context"), context_digest=HASH)
    obligations = [obj(kind=const("distinct-approval"), owner=const("council"), policy_digest=HASH),
                   obj(kind=const("mandatory-recording"), owner=const("server"), phase=const("before-send")),
                   obj(kind=const("action-capacity"), owner=const("gate"), target=ref("target-ref"),
                       limit=const(2), window_seconds=const(3600)),
                   obj(kind=const("credential-custody"), owner=const("warden"), audience=ref("target-ref"))]
    defs["obligation"] = {"anyOf": obligations}
    common = dict(operation=ref("operation-ref"), attempt=ref("attempt-ref"), request_digest=HASH, context_digest=HASH)
    defs["action-decision"] = record("action-decision", **common,
                                      outcome=enum("approval-required", "denied"),
                                      obligations=arr(ref("obligation"), maximum=4), reason_codes=arr(ID, minimum=1))
    defs["action-approval"] = record("action-approval", **common, approval=ref("approval-ref"),
                                      decision_digest=HASH, approver=ref("principal"), eligibility_revision=POSITIVE,
                                      issued_at=UINT, expires_at=UINT, prior=nullable(ref("approval-ref")))
    defs["activation"] = record("activation", transition=ref("transition-ref"), scope=ref("scope"),
                                 profile_digest=HASH, prior_epoch=POSITIVE, successor_epoch=POSITIVE,
                                 prior_artifact_set_digest=HASH,
                                 artifacts=arr(obj(kind=ID, digest=HASH), minimum=1), artifact_set_digest=HASH,
                                 participants=arr(enum(*PARTICIPANTS), minimum=4, maximum=4),
                                 participant_set_digest=HASH, ratification=ref("approval-ref"),
                                 not_before=UINT, expires_at=UINT)
    defs["activation-receipt"] = record("activation-receipt", transition=ref("transition-ref"),
                                         transition_digest=HASH, participant=enum(*PARTICIPANTS),
                                         phase=enum("paused", "applied"), prior_epoch=POSITIVE,
                                         successor_epoch=POSITIVE, artifact_set_digest=HASH,
                                         participant_set_digest=HASH)
    payloads = {
        "approval-recorded": dict(approval=ref("approval-ref"), approval_digest=HASH),
        "claim-created": dict(claim=ref("claim-ref"), grant_binding_digest=HASH),
        "grant-issued": dict(claim=ref("claim-ref"), grant=ref("grant-ref"), expires_at=UINT),
        "consumption-reserved": dict(claim=ref("claim-ref"), grant=ref("grant-ref"), worker=ID, worker_fence=POSITIVE,
                                     reservations=arr(obj(reservation=ref("reservation-ref"), target=ref("target-ref"),
                                                          root=ref("task-ref"), window_start=UINT, units=const(1)), minimum=1)),
        "predispatch": dict(claim=ref("claim-ref"), grant=ref("grant-ref"), consumption_event_digest=HASH),
        "send-intent": dict(claim=ref("claim-ref"), grant=ref("grant-ref"), invocation=ref("invocation-ref"),
                            worker=ID, worker_fence=POSITIVE, predispatch_ack_digest=HASH,
                            effect_key=ID, target=ref("target-ref")),
        "outcome": dict(claim=ref("claim-ref"), invocation=ref("invocation-ref"), effect_key=ID,
                        effect_status=enum("completed", "proven-no-effect", "unresolved"),
                        evidence=arr(ref("evidence-ref"))),
        "reconciliation": dict(claim=ref("claim-ref"), effect_key=ID, prior_outcome_digest=HASH,
                               effect_status=enum("completed", "proven-no-effect", "unresolved"),
                               evidence=arr(ref("evidence-ref"))),
    }
    for kind, fields in payloads.items():
        defs[kind + "-payload"] = obj(kind=const(kind), **common, activation_epoch=POSITIVE,
                                      recovery_epoch=POSITIVE, **fields)
    defs["activation-applied-payload"] = obj(kind=const("activation-applied"), receipt=ref("activation-receipt"))
    defs["accountability-event"] = record("accountability-event", scope=ref("scope"), event_id=ID,
                                          producer=enum("council", *PARTICIPANTS), stream=ref("stream-ref"),
                                          source_generation=POSITIVE, sequence=POSITIVE, predecessor=nullable(HASH),
                                          occurred_at=UINT, clock=const("bounded-utc-2s"),
                                          family=enum("action", "activation"), kind=enum(*payloads, "activation-applied"),
                                          payload_digest=HASH, causal_parents=arr(HASH),
                                          payload={"anyOf": [ref(k + "-payload") for k in (*payloads, "activation-applied")]})
    defs["event-ack"] = record("event-ack", scope=ref("scope"), event_id=ID, event_digest=HASH,
                                payload_digest=HASH, ledger=ref("ledger-ref"), position=POSITIVE, received_at=UINT)
    roots = ["action-request", "action-decision", "action-approval", "activation", "activation-receipt",
             "accountability-event", "event-ack"]
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$defs": defs,
            "anyOf": [ref(name) for name in roots]}


def fixtures():
    scope = dict(domain="fixture-domain", tenant="tenant-a", deployment="fixture-deployment", cell="cell-a")
    def q(kind, name):
        return dict(scope=copy.deepcopy(scope), kind=kind, id=name)
    def principal(name, kind):
        return dict(scope=copy.deepcopy(scope), subject=name, subject_generation=1, kind=kind)
    def h(name):
        return "sha256:" + hashlib.sha256(name.encode()).hexdigest()
    profile = dict(schema_version=1, profile=PROFILE, status="candidate-not-qualified", canonicalization="decision-json-v1",
                   digest_prefix="munarium:stage2:", participants=PARTICIPANTS, action_event_owners=OWNERS,
                   approval_lifetime_seconds=300, clock_uncertainty_seconds=2, action_cap=2, action_window_seconds=3600,
                   capability_operation="release.publish_approved_artifact", runtime_direction="linux-postgresql-single-cell",
                   runtime_dependency_pins="pending-intake", executable_authority=False)
    actor, approver = principal("requesting-agent", "agent"), principal("reviewing-human", "human")
    task = dict(root=q("task", "root-task"), parent=None, agent_release=h("agent-release"), agent_instance="instance-a")
    evidence = dict(source=q("evidence", "artifact-inventory"), revision=1, content_digest=h("verified-artifact"),
                    field="artifact.digest", derivation="inventory", derivation_version=1, observed_at=990,
                    expires_at=1300, trust="verified", verifier=q("authority", "inventory-verifier"))
    intent = dict(actor=actor, origin=copy.deepcopy(actor), delegation_digest=h("registered-delegation"), task=task,
                  target=q("target", "synthetic-target"), environment="disposable", capability_operation=profile["capability_operation"],
                  parameter_schema_digest=h("synthetic-parameters"),
                  parameters=dict(artifact_digest=h("verified-artifact"), destination="synthetic-release"),
                  attachments=[], target_precondition=dict(version=1, content_digest=h("target-before")))
    context = dict(activation=dict(owner="registry", scope=copy.deepcopy(scope), revision=2),
                   recovery=dict(scope=copy.deepcopy(scope), revision=1),
                   authority_pins=[dict(owner=q("authority", "warden"), revision=1)],
                   manifest_digest=h("manifest"), policy_digest=h("policy"), evaluator_profile_digest=h("evaluator"),
                   mode="enforce", evidence=[evidence], valid_from=990, expires_at=1300)
    def rec(record_type, **fields):
        return dict(schema_version=1, type=record_type, profile=PROFILE, **fields)
    records = {}
    request = records["request"] = rec("action-request", operation=q("operation", "publish-artifact"),
                                       attempt=q("attempt", "attempt-a"), intent=intent, intent_digest=digest("intent", intent),
                                       context=context, context_digest=digest("context", context))
    common = dict(operation=request["operation"], attempt=request["attempt"], request_digest=digest("action-request", request),
                  context_digest=request["context_digest"])
    obligations = [dict(kind="distinct-approval", owner="council", policy_digest=context["policy_digest"]),
                   dict(kind="mandatory-recording", owner="server", phase="before-send"),
                   dict(kind="action-capacity", owner="gate", target=intent["target"], limit=2, window_seconds=3600),
                   dict(kind="credential-custody", owner="warden", audience=intent["target"])]
    decision = records["decision"] = rec("action-decision", **common, outcome="approval-required",
                                         obligations=obligations, reason_codes=["distinct-human-required"])
    approval = records["approval"] = rec("action-approval", **common, approval=q("approval", "approval-a"),
                                         decision_digest=digest("action-decision", decision), approver=approver,
                                         eligibility_revision=1, issued_at=990, expires_at=1290, prior=None)
    artifacts = [dict(kind="manifest", digest=context["manifest_digest"]), dict(kind="policy", digest=context["policy_digest"])]
    activation = records["activation"] = rec("activation", transition=q("transition", "transition-a"), scope=scope,
                                             profile_digest=digest("profile", profile), prior_epoch=1, successor_epoch=2,
                                             prior_artifact_set_digest=h("prior-set"), artifacts=artifacts,
                                             artifact_set_digest=digest("artifact-set", {"artifacts": artifacts}),
                                             participants=PARTICIPANTS,
                                             participant_set_digest=digest("participants", {"participants": PARTICIPANTS}),
                                             ratification=q("approval", "activation-ratification"), not_before=990, expires_at=1300)
    for owner in PARTICIPANTS:
        records[owner + "-receipt"] = rec("activation-receipt", transition=activation["transition"],
                                           transition_digest=digest("activation", activation), participant=owner, phase="applied",
                                           prior_epoch=1, successor_epoch=2, artifact_set_digest=activation["artifact_set_digest"],
                                           participant_set_digest=activation["participant_set_digest"])
    records["pause"] = copy.deepcopy(records["gate-receipt"])
    records["pause"]["phase"] = "paused"
    claim, grant = q("claim", "claim-a"), q("grant", "grant-a")
    details = {
        "approval-recorded": dict(approval=approval["approval"], approval_digest=digest("action-approval", approval)),
        "claim-created": dict(claim=claim, grant_binding_digest=common["request_digest"]),
        "grant-issued": dict(claim=claim, grant=grant, expires_at=1020),
        "consumption-reserved": dict(claim=claim, grant=grant, worker="worker-a", worker_fence=1,
                                     reservations=[dict(reservation=q("reservation", "reservation-a"), target=intent["target"],
                                                        root=task["root"], window_start=0, units=1)]),
        "predispatch": dict(claim=claim, grant=grant, consumption_event_digest=h("consumption-record")),
        "send-intent": dict(claim=claim, grant=grant, invocation=q("invocation", "invocation-a"), worker="worker-a",
                            worker_fence=1, predispatch_ack_digest=h("predispatch-ack"), effect_key="publish-artifact",
                            target=intent["target"]),
        "outcome": dict(claim=claim, invocation=q("invocation", "invocation-a"), effect_key="publish-artifact",
                        effect_status="unresolved", evidence=[]),
        "reconciliation": dict(claim=claim, effect_key="publish-artifact", prior_outcome_digest=h("outcome-record"),
                               effect_status="completed", evidence=[q("evidence", "target-receipt")]),
    }
    streams = {}
    ledger = q("ledger", "server-ledger")
    def acknowledge(event):
        return rec("event-ack", scope=scope, event_id=event["event_id"], event_digest=digest("accountability-event", event),
                   payload_digest=event["payload_digest"], ledger=ledger, position=1, received_at=1001)
    for kind, detail in details.items():
        if kind == "predispatch":
            detail["consumption_event_digest"] = digest("accountability-event", records["consumption-reserved"])
        if kind == "send-intent":
            records["ack"] = acknowledge(records["predispatch"])
            detail["predispatch_ack_digest"] = digest("event-ack", records["ack"])
        if kind == "reconciliation":
            detail["prior_outcome_digest"] = digest("accountability-event", records["outcome"])
        payload = dict(kind=kind, **common, activation_epoch=2, recovery_epoch=1, **detail)
        stream_id = "fixture-" + kind
        streams[stream_id] = dict(producer=OWNERS[kind], generation=1, last_sequence=0, last_digest=None)
        records[kind] = rec("accountability-event", scope=scope, event_id="event-" + kind, producer=OWNERS[kind],
                            stream=q("stream", stream_id), source_generation=1, sequence=1, predecessor=None,
                            occurred_at=1000, clock="bounded-utc-2s", family="action", kind=kind,
                            payload_digest=digest("event-payload", payload), causal_parents=[], payload=payload)
    payload = dict(kind="activation-applied", receipt=records["registry-receipt"])
    records["activation-event"] = rec("accountability-event", scope=scope, event_id="event-activation", producer="registry",
                                      stream=q("stream", "fixture-activation"), source_generation=1, sequence=1, predecessor=None,
                                      occurred_at=1000, clock="bounded-utc-2s", family="activation", kind="activation-applied",
                                      payload_digest=digest("event-payload", payload), causal_parents=[], payload=payload)
    streams["fixture-activation"] = dict(producer="registry", generation=1, last_sequence=0, last_digest=None)
    trusted = dict(scope=scope, now=1000, actor=actor, origin=actor, task=task, approver=approver,
                   delegation_digest=intent["delegation_digest"], context=context, evidence=[evidence],
                   eligible_revision=1, approval_status="approved", approval_digest=digest("action-approval", approval),
                   obligations=obligations, streams=streams, authenticated_producers=["gate", "registry", "server", "warden", "council"],
                   authenticated_event_digests=[digest("accountability-event", r) for r in records.values() if r["type"] == "accountability-event"],
                   authenticated_receipt_digests=[digest("activation-receipt", r) for r in records.values() if r["type"] == "activation-receipt"],
                   authenticated_ack_digests=[digest("event-ack", records["ack"])],
                   ledger=ledger, prior_epoch=1, prior_artifact_set_digest=activation["prior_artifact_set_digest"],
                   ratification=activation["ratification"], paused_transition_digest=digest("activation", activation),
                   ratified_transition_digest=digest("activation", activation), requester_chain=[actor],
                   historical_events=[], historical_cursors=copy.deepcopy(streams),
                   recovery_recorder_authorized=False, recovery_cutoff=1000,
                   effect_evidence=[q("evidence", "target-receipt")],
                   target=intent["target"], target_precondition=intent["target_precondition"],
                   parameter_schema_digest=intent["parameter_schema_digest"])
    return profile, records, trusted


def vectors(records, trusted):
    cases = []
    def case(name, record_name, changes, expected, context_changes=None, rehash=True):
        value = copy.deepcopy(records[record_name])
        for path, replacement in changes.items():
            target = value
            pieces = path.split(".")
            for piece in pieces[:-1]:
                target = target[int(piece)] if isinstance(target, list) else target[piece]
            target[int(pieces[-1]) if isinstance(target, list) else pieces[-1]] = replacement
        changes = copy.deepcopy(changes)
        if rehash and value["type"] == "action-request":
            for key in ("intent", "context"):
                changes[key + "_digest"] = digest(key, value[key])
        if rehash and value["type"] == "accountability-event":
            changes["payload_digest"] = digest("event-payload", value["payload"])
        cases.append(dict(id=name, record=record_name, changes=changes,
                          context_changes=context_changes or {}, expected=expected))
    case("foreign-tenant", "request", {"operation.scope.tenant": "tenant-b"}, "Unauthorized")
    case("foreign-cell", "request", {"intent.target.scope.cell": "cell-b"}, "Unauthorized")
    case("subject-generation", "request", {"intent.actor.subject_generation": 2}, "Unauthorized")
    case("forged-root", "request", {"intent.task.root.id": "new-root"}, "Unauthorized")
    case("omitted-parent", "request", {"intent.task.parent": None}, "Unauthorized",
         {"task.parent": dict(trusted["task"]["root"], id="required-parent")})
    case("refreshed-proof", "request", {}, "accept", {"now": 1001})
    case("stale-activation", "request", {"context.activation.revision": 1}, "StaleContext")
    case("untrusted-evidence", "request", {"context.evidence.0.trust": "untrusted"}, "UnavailableEvidence")
    case("forged-verified-evidence", "request", {"context.evidence.0.content_digest": "sha256:" + "0" * 64}, "UnavailableEvidence")
    case("expired-evidence", "request", {}, "UnavailableEvidence", {"now": 1300})
    case("wrong-intent-digest", "request", {"intent_digest": "sha256:" + "0" * 64}, "InvalidBinding", rehash=False)
    case("shadow-mode", "request", {"context.mode": "observe"}, "InvalidShape")
    case("unknown-version", "request", {"schema_version": 2}, "InvalidShape")
    case("unknown-profile", "request", {"profile": "future-profile"}, "InvalidShape")
    case("extra-authority", "request", {"grant_authority": True}, "InvalidShape")
    case("manifest-operation-confusion", "request", {"operation.kind": "capability"}, "InvalidShape")
    case("unknown-obligation", "decision", {"obligations.0.kind": "future-allow"}, "InvalidShape")
    case("missing-obligation", "decision", {"obligations": []}, "InvalidBinding")
    case("self-approval", "approval", {"approver": records["request"]["intent"]["actor"]}, "Unauthorized")
    case("approver-in-requester-chain", "approval", {}, "Unauthorized", {"requester_chain": [records["approval"]["approver"]]})
    case("changed-decision", "approval", {"decision_digest": "sha256:" + "0" * 64}, "InvalidBinding")
    case("withdrawn-approval", "approval", {}, "Denied", {"approval_status": "cancelled"})
    case("expired-approval", "approval", {}, "Expired", {"now": 1289})
    case("stale-eligibility", "approval", {"eligibility_revision": 2}, "Unauthorized")
    case("missing-participant", "activation", {"participants": ["gate", "registry", "warden"]}, "InvalidShape")
    case("unknown-participant", "activation", {"participants.0": "gateway"}, "InvalidShape")
    case("reused-epoch", "activation", {"successor_epoch": 1}, "StaleContext")
    case("stale-prior-head", "activation", {"prior_artifact_set_digest": "sha256:" + "0" * 64}, "StaleContext")
    case("unratified-transition", "activation", {}, "Unauthorized", {"ratified_transition_digest": "sha256:" + "0" * 64})
    case("early-activation", "activation", {}, "Expired", {"now": 991})
    case("receipt-wrong-transition", "registry-receipt", {"transition_digest": "sha256:" + "0" * 64}, "InvalidBinding")
    case("non-gate-pause", "registry-receipt", {"phase": "paused"}, "Unauthorized")
    case("unattested-receipt", "registry-receipt", {}, "Unauthorized", {"authenticated_receipt_digests": []})
    case("wrong-event-owner", "outcome", {"producer": "council"}, "Unauthorized")
    case("unattested-event", "outcome", {}, "Unauthorized", {"authenticated_event_digests": []})
    case("sequence-gap", "outcome", {"sequence": 3}, "InvalidSequence")
    case("invented-predecessor", "outcome", {"predecessor": "sha256:" + "0" * 64}, "InvalidSequence")
    case("wrong-payload-digest", "outcome", {"payload_digest": "sha256:" + "0" * 64}, "InvalidBinding", rehash=False)
    case("outcome-without-evidence", "outcome", {"payload.effect_status": "completed"}, "UnavailableEvidence")
    case("unknown-event-kind", "outcome", {"kind": "model-call"}, "InvalidShape")
    case("activation-not-action", "activation-event", {"family": "action"}, "InvalidBinding")
    case("wrong-ack-digest", "ack", {"event_digest": "sha256:" + "0" * 64}, "InvalidBinding")
    case("foreign-ledger", "ack", {"ledger.scope.tenant": "tenant-b"}, "Unauthorized")
    case("unattested-ack", "ack", {}, "Unauthorized", {"authenticated_ack_digests": []})
    case("historical-without-proof", "outcome", {}, "Unauthorized", {"streams.fixture-outcome.generation": 2})
    case("historical-audit-only", "outcome", {}, "accept",
         {"streams.fixture-outcome.generation": 2, "recovery_recorder_authorized": True,
          "historical_events": [digest("accountability-event", records["outcome"])]})
    case("historical-missing-cursor", "outcome", {}, "Unauthorized",
         {"streams.fixture-outcome.generation": 2, "recovery_recorder_authorized": True, "historical_cursors": {},
          "historical_events": [digest("accountability-event", records["outcome"])]})
    return dict(profile=PROFILE, records=records, trusted=trusted, cases=cases,
                canonical={name: canonical(value).decode() for name, value in records.items()},
                digests={name: digest(value["type"], value) for name, value in records.items()})


def generated_files(readme):
    profile, records, trusted = fixtures()
    def pretty(value):
        return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
    contents = {"README.md": readme.replace(b"\r\n", b"\n"), "schema.json": pretty(schema()),
                "profile.json": pretty(profile), "vectors.json": pretty(vectors(records, trusted))}
    hashes = {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(contents.items())}
    aggregate = "".join(name + "\0" + sha + "\n" for name, sha in hashes.items()).encode()
    contents["bundle-lock.json"] = pretty(dict(status="candidate-not-accepted-not-released", profile=PROFILE,
                                               files=hashes, bundle_sha256=hashlib.sha256(aggregate).hexdigest()))
    return contents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check and (DEST / "bundle-lock.json").exists():
        raise SystemExit("locked candidate exists; use a new reviewed version/destination")
    contents = generated_files((DEST / "README.md").read_bytes())
    if args.check:
        for name, raw in contents.items():
            if (DEST / name).read_bytes().replace(b"\r\n", b"\n") != raw:
                raise SystemExit("candidate differs from generator: " + name)
        print("Stage 2 candidate reproduction passed; no files changed.")
    else:
        for name in contents:
            if name != "README.md" and (DEST / name).exists():
                raise SystemExit("refusing existing candidate artifact: " + name)
        for name, raw in contents.items():
            if name != "README.md":
                (DEST / name).write_bytes(raw)
        print("Created inert Stage 2 candidate; no accepted wire contract or execution authority.")


if __name__ == "__main__":
    main()
