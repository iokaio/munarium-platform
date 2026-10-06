#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Explicitly regenerate a proposed fixture revision; signing keys exist only in memory.

Generation needs the contributor's cryptography package. Verification uses OpenSSL,
Python's standard library and public fixtures, and never runs this generator in CI.
"""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from test_decision_json_vectors import canonical

DEST = Path(__file__).resolve().parents[1] / "docs/decisions/candidates"


def write(name, value):
    (DEST / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def obj(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def ref(name):
    return {"$ref": "#/$defs/" + name}


def nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def array(item, maximum=32, minimum=0, unique=False):
    return dict(type="array", items=item, minItems=minimum, maxItems=maximum, uniqueItems=unique)


def enum(*values):
    return {"type": "string", "enum": list(values)}


def b64(raw):
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def generate():
    DEST.mkdir(exist_ok=True)
    identifier = {"type": "string", "minLength": 1, "maxLength": 128, "pattern": "^[a-zA-Z0-9][a-zA-Z0-9:._/-]*$"}
    text = {"type": "string", "minLength": 1, "maxLength": 1024}
    digest = {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$", "minLength": 71, "maxLength": 71}
    integer = {"type": "integer", "minimum": 0, "maximum": 9007199254740991}
    version = {"type": "integer", "const": 1}
    refs = array(identifier, unique=True)
    definitions = {"bootstrap": obj(dict(epoch=integer, nonce=identifier, action=enum("install-governance"),
        artifact_digest=digest, expected_revision=digest, expected_head=integer))}
    definitions["principal"] = obj(dict(schema_version=version, deployment=identifier, tenant=identifier,
        issuer=identifier, audience=identifier, origin=identifier, actor=identifier,
        origin_kind=enum("human", "agent", "service"), service=identifier,
        purpose=enum("bootstrap", "decision"), scopes=array(enum("read", "evaluate", "propose", "govern", "ratify"), 5, 1, True),
        resources=array(identifier, 32, 1, True), iat=integer, nbf=integer, exp=integer,
        parent_digest=nullable(digest), bootstrap=nullable(ref("bootstrap"))))
    definitions["attachment"] = obj(dict(digest=digest, media_type=text, bytes={**integer, "maximum": 1048576}))
    definitions["request"] = obj(dict(schema_version=version, profile=enum("decision-json-v1"), tenant=identifier,
        operation_id=identifier, principal_digest=digest, target_id=identifier, environment=identifier,
        capability_id=identifier, manifest_digest=digest, policy_digest=digest, activation_epoch=integer,
        mode=enum("observe", "advise", "guard", "enforce", "assure"), parameters={"type": "object"},
        attachments=array(ref("attachment"), 8)))
    definitions["required_input"] = obj(dict(field_path=identifier, source_id=identifier,
        derivation_id=identifier, derivation_version=identifier, permitted_use=enum("decision")))
    definitions["modifier"] = obj(dict(field_path=identifier, predicate_digest=digest,
        raise_to=enum("C1", "C2", "C3", "C4")))
    definitions["manifest"] = obj(dict(schema_version=version, id=identifier, version=identifier,
        capability_id=identifier, target_id=identifier, environment=identifier, credential_audience=identifier,
        parameter_schema_digest=digest, result_schema_digest=digest, base_consequence=enum("C0", "C1", "C2", "C3", "C4"),
        modifiers=array(ref("modifier")), required_inputs=array(ref("required_input")),
        effect=enum("observation", "internal-change", "external-effect"),
        idempotency=enum("none", "operation-key"), compensation=enum("none", "separate-action")))
    definitions["lineage"] = obj(dict(tenant=identifier, source_id=nullable(identifier),
        revision=nullable(identifier), content_digest=nullable(digest), derivation_id=nullable(identifier),
        derivation_version=nullable(identifier), field_path=identifier, observed_at=nullable(integer),
        evidence_ref=nullable(identifier), trust=enum("unknown", "untrusted", "verified"),
        verifier_ref=nullable(identifier), policy_digest=nullable(digest)))
    definitions["obligation"] = obj(dict(kind=enum("distinct-approval"), policy_digest=digest,
        request_digest=digest, approver_scope=identifier))
    definitions["decision"] = obj(dict(schema_version=version, tenant=identifier, operation_id=identifier, request_digest=digest,
        principal_digest=digest, manifest_digest=digest, policy_digest=digest, evaluator=enum("cedar", "opa"),
        evaluator_version=identifier, evaluator_digest=digest, activation_epoch=integer,
        mode=enum("observe", "advise", "guard", "enforce", "assure"), lineage=array(ref("lineage")),
        consequence=enum("C0", "C1", "C2", "C3", "C4"),
        outcome=enum("denied", "approval-required", "decision-only-allow"), reasons=refs,
        obligations=array(ref("obligation"))))
    definitions["refusal"] = obj(dict(schema_version=version, tenant=identifier, operation_id=identifier,
        request_digest=digest, reasons=array(identifier, 32, 1, True)))
    definitions["event"] = obj(dict(schema_version=version, convention=enum("decision-events-v1"),
        tenant=identifier, source_service=identifier, source_epoch=integer, event_id=identifier,
        sequence={**integer, "minimum": 1}, prior_event_digest=nullable(digest), operation_id=identifier,
        request_digest=digest, kind=enum("proposal", "decision", "refusal"), recorded_at=integer,
        payload_digest=digest, causation=refs, correlation=refs,
        payload={"anyOf": [ref("request"), ref("decision"), ref("refusal")]}))
    definitions["ack"] = obj(dict(schema_version=version, tenant=identifier, event_id=identifier,
        payload_digest=digest, event_digest=digest, ledger_id=identifier, ledger_position={**integer, "minimum": 1}))
    write("foundation.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:munarium:candidate:foundation:v1", "title": "Proposed foundation records; not published",
        "$defs": definitions})

    digest_a, digest_b = "sha256:" + "a" * 64, "sha256:" + "b" * 64
    bootstrap = dict(epoch=1, nonce="enrollment-1", action="install-governance", artifact_digest=digest_a,
                     expected_revision=digest_b, expected_head=0)
    principal = dict(schema_version=1, deployment="fixture", tenant="alpha", issuer="fixture-issuer",
        audience="svc-server", origin="human-a", actor="human-a", origin_kind="human", service="svc-bootstrap",
        purpose="bootstrap", scopes=["govern"], resources=["governance"], iat=900, nbf=900, exp=1100,
        parent_digest=None, bootstrap=bootstrap)
    context = dict(deployment="fixture", tenant="alpha", audience="svc-server", peer_service="svc-bootstrap",
        now=1000, retired_keys=[], authority_available=True, restore_quarantined=False,
        enrolled_humans=["human-a"], expected_bootstrap=bootstrap, bootstrap_retired=False)
    secret = Ed25519PrivateKey.generate()
    keys = {"fixture-key": dict(issuer="fixture-issuer", purposes=["bootstrap", "decision"],
        public_key=b64(secret.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)))}

    def sign(payload, header=None):
        head = b64(canonical(json.dumps(header or dict(alg="Ed25519", kid="fixture-key", typ="munarium-principal+jws")).encode()))
        body = b64(canonical(json.dumps(payload).encode()))
        return dict(protected=head, payload=body, signature=b64(secret.sign((head + "." + body).encode())))

    cases = []

    def case(name, payload=None, changes=None, expected="reject", tokens=None):
        state = {**copy.deepcopy(context), **(changes or {})}
        cases.append(dict(id=name, tokens=tokens or [sign(payload or principal)], context=state, expected=expected))

    case("valid-bootstrap", expected="accept")
    for name, changes in [("retired-key", {"retired_keys": ["fixture-key"]}),
        ("wrong-tenant", {"tenant": "beta"}), ("wrong-audience", {"audience": "svc-gate"}),
        ("wrong-peer", {"peer_service": "svc-harness"}), ("expired", {"now": 1100}),
        ("future", {"now": 899}), ("expiry-uncertainty", {"now": 1098}),
        ("retired-bootstrap", {"bootstrap_retired": True}), ("unavailable", {"authority_available": False}),
        ("restore", {"restore_quarantined": True}), ("unenrolled-human", {"enrolled_humans": []}),
        ("stale-head", {"expected_bootstrap": {**bootstrap, "expected_head": 1}})]:
        case(name, changes=changes)
    for name, patch in [("agent-bootstrap", dict(origin_kind="agent")), ("long-lifetime", dict(exp=1301)),
                         ("wrong-issuer", dict(issuer="other-issuer")), ("false-root", dict(origin="someone-else"))]:
        case(name, {**principal, **patch})
    corrupt = sign(principal); corrupt["signature"] = b64(bytes(64))
    case("forged", tokens=[corrupt])
    forged_payload = sign(principal); forged_payload["payload"] = b64(canonical(json.dumps({**principal, "tenant": "beta"}).encode()))
    case("substituted-payload", changes={"tenant": "beta"}, tokens=[forged_payload])
    case("algorithm-confusion", tokens=[sign(principal, dict(alg="EdDSA", kid="fixture-key", typ="munarium-principal+jws"))])
    root = {**principal, "purpose": "decision", "origin": "agent-a", "actor": "agent-a", "origin_kind": "agent",
            "service": "svc-harness", "scopes": ["read", "evaluate"], "resources": ["item-a", "item-b"],
            "iat": 980, "nbf": 980, "exp": 1040, "bootstrap": None}
    first = sign(root)
    parent_digest = "sha256:" + hashlib.sha256(".".join(first[k] for k in ("protected", "payload", "signature")).encode()).hexdigest()
    child = {**root, "actor": "agent-b", "scopes": ["evaluate"], "resources": ["item-a"],
             "exp": 1030, "parent_digest": parent_digest}
    changes = {"peer_service": "svc-harness"}
    case("valid-delegation", changes=changes, expected="accept", tokens=[first, sign(child)])
    for name, patch in [("wider-scope", {"scopes": ["propose"]}), ("wider-resource", {"resources": ["item-c"]}),
        ("longer-delegation", {"exp": 1041}), ("changed-origin", {"origin": "human-a"}),
        ("cycle", {"actor": "agent-a"}), ("parent-substitution", {"parent_digest": digest_a}),
        ("delegated-ratifier", {"scopes": ["ratify"]})]:
        case(name, changes=changes, tokens=[first, sign({**child, **patch})])
    for name, header in [("unknown-key", dict(alg="Ed25519", kid="other-key", typ="munarium-principal+jws")),
                         ("header-key-url", dict(alg="Ed25519", kid="fixture-key", typ="munarium-principal+jws", jku="https://example.invalid/key"))]:
        case(name, tokens=[sign(principal, header)])
    chain = [first]
    for i in range(1, 6):
        previous = "sha256:" + hashlib.sha256(".".join(chain[-1][k] for k in ("protected", "payload", "signature")).encode()).hexdigest()
        chain.append(sign({**child, "actor": "agent-" + str(i), "parent_digest": previous}))
    case("four-edges", changes=changes, expected="accept", tokens=chain[:5])
    case("fifth-edge", changes=changes, tokens=chain)
    write("identity-vectors.json", dict(status="proposed", keys=keys, cases=cases))
    request = dict(schema_version=1, profile="decision-json-v1", tenant="alpha", operation_id="op-1",
        principal_digest=digest_a, target_id="fixture-target", environment="test", capability_id="read-item",
        manifest_digest=digest_b, policy_digest=digest_a, activation_epoch=1, mode="guard", parameters={}, attachments=[])
    manifest = dict(schema_version=1, id="read-item", version="1", capability_id="read-item", target_id="fixture-target",
        environment="test", credential_audience="none", parameter_schema_digest=digest_a, result_schema_digest=digest_b,
        base_consequence="C0", modifiers=[], required_inputs=[], effect="observation", idempotency="none", compensation="none")
    lineage = dict(tenant="alpha", source_id=None, revision=None, content_digest=None, derivation_id=None,
        derivation_version=None, field_path="item", observed_at=None, evidence_ref=None, trust="unknown", verifier_ref=None, policy_digest=None)
    decision = dict(schema_version=1, tenant="alpha", operation_id="op-1", request_digest=digest_a, principal_digest=digest_a,
        manifest_digest=digest_b, policy_digest=digest_a, evaluator="cedar", evaluator_version="4.13.0",
        evaluator_digest=digest_b, activation_epoch=1, mode="guard", lineage=[lineage], consequence="C0",
        outcome="denied", reasons=["lineage-unknown"], obligations=[])
    event = dict(schema_version=1, convention="decision-events-v1", tenant="alpha", source_service="svc-gate",
        source_epoch=1, event_id="event-1", sequence=1, prior_event_digest=None, operation_id="op-1",
        request_digest=digest_a, kind="decision", recorded_at=1000, payload_digest=digest_b,
        causation=[], correlation=[], payload=decision)
    ack = dict(schema_version=1, tenant="alpha", event_id="event-1", payload_digest=digest_b,
        event_digest=digest_a, ledger_id="ledger-a", ledger_position=1)
    def digest_record(domain, value):
        return "sha256:" + hashlib.sha256(("munarium:" + domain + ":v1\0").encode() + canonical(json.dumps(value).encode())).hexdigest()
    request["manifest_digest"] = digest_record("manifest", manifest)
    request["principal_digest"] = "sha256:" + hashlib.sha256(".".join(first[k] for k in ("protected", "payload", "signature")).encode()).hexdigest()
    decision["principal_digest"] = request["principal_digest"]
    decision["manifest_digest"] = request["manifest_digest"]
    decision["request_digest"] = digest_record("decision-request", request)
    event["request_digest"] = decision["request_digest"]
    event["payload_digest"] = digest_record("decision-event-payload", decision)
    ack["payload_digest"] = event["payload_digest"]
    ack["event_digest"] = digest_record("decision-event", event)
    examples = dict(principal=principal, request=request, manifest=manifest, lineage=lineage, decision=decision,
                    event=event, ack=ack, refusal=dict(schema_version=1, tenant="alpha", operation_id="op-1", request_digest=decision["request_digest"], reasons=["input-unavailable"]))
    write("record-vectors.json", {"status": "proposed", "examples": examples})
    files = {name: hashlib.sha256((DEST / name).read_bytes()).hexdigest() for name in
             ("foundation.schema.json", "identity-vectors.json", "record-vectors.json")}
    bundle = hashlib.sha256("".join(name + "\0" + value + "\n" for name, value in sorted(files.items())).encode()).hexdigest()
    write("candidate-lock.json", dict(status="proposed-not-released", schema_version=1, files=files, bundle_sha256=bundle))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--new-candidate", action="store_true", required=True)
    parser.parse_args()
    generate()
