#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded offline schema/vector oracle; never import into a deployed verifier."""
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from test_decision_json_vectors import canonical

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs/decisions/candidates"
SCHEMA = json.loads((FIXTURES / "foundation.schema.json").read_text(encoding="utf-8"))
KEYWORDS = {"$schema", "$id", "$defs", "$ref", "title", "description", "type",
            "properties", "required", "additionalProperties", "items", "minItems",
            "maxItems", "uniqueItems", "minLength", "maxLength", "pattern", "minimum",
            "maximum", "const", "enum", "anyOf"}


def check_schema(schema):
    """Reject unsupported vocabulary instead of silently ignoring a new constraint."""
    if not isinstance(schema, dict) or set(schema) - KEYWORDS:
        raise ValueError("unsupported schema vocabulary")
    if "anyOf" in schema and set(schema) != {"anyOf"}:
        raise ValueError("anyOf siblings are outside this checker subset")
    for keyword in ("properties", "$defs"):
        for child in schema.get(keyword, {}).values():
            check_schema(child)
    for child in schema.get("anyOf", []):
        check_schema(child)
    if "items" in schema:
        check_schema(schema["items"])
    if "$ref" in schema:
        if set(schema) != {"$ref"} or schema["$ref"] not in {
                "#/$defs/" + name for name in SCHEMA["$defs"]}:
            raise ValueError("only local definition references are supported")


def validate(value, schema):
    """Only the explicitly checked Draft 2020-12 subset used by these fixtures."""
    if "$ref" in schema:
        return validate(value, SCHEMA["$defs"][schema["$ref"].split("/")[-1]])
    if "anyOf" in schema:
        for option in schema["anyOf"]:
            try:
                validate(value, option)
                return
            except ValueError:
                pass
        raise ValueError("no schema alternative")
    types = {"object": dict, "array": list, "string": str, "integer": int,
             "boolean": bool, "null": type(None)}
    if "type" in schema and type(value) is not types[schema["type"]]:
        raise ValueError("type")
    if "const" in schema and value != schema["const"]:
        raise ValueError("constant")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError("enum")
    if isinstance(value, dict):
        if set(schema.get("required", [])) - value.keys():
            raise ValueError("required field")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False and value.keys() - properties.keys():
            raise ValueError("unknown field")
        for key in value.keys() & properties.keys():
            validate(value[key], properties[key])
    if isinstance(value, (list, str)):
        lower, upper = ("minItems", "maxItems") if isinstance(value, list) else ("minLength", "maxLength")
        if len(value) < schema.get(lower, 0) or len(value) > schema.get(upper, 65536):
            raise ValueError("length")
    if isinstance(value, str) and "pattern" in schema and not re.search(schema["pattern"], value):
        raise ValueError("pattern")
    if type(value) is int and not schema.get("minimum", -9007199254740991) <= value <= schema.get("maximum", 9007199254740991):
        raise ValueError("range")
    if isinstance(value, list):
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise ValueError("duplicates")
        for child in value:
            validate(child, schema.get("items", {}))


def validate_record(name, value):
    canonical(json.dumps(value, ensure_ascii=False).encode())
    validate(value, SCHEMA["$defs"][name])
    if name == "manifest" and any(m["raise_to"] <= value["base_consequence"] for m in value["modifiers"]):
        raise ValueError("consequence modifier must raise")
    if name == "lineage" and value["trust"] == "verified" and any(v is None for v in value.values()):
        raise ValueError("verified lineage needs every binding")
    if name == "decision":
        if (value["outcome"] == "approval-required") != bool(value["obligations"]):
            raise ValueError("approval obligations")
        for obligation in value["obligations"]:
            if any(obligation[k] != value[k] for k in ("request_digest", "policy_digest")):
                raise ValueError("obligation binding")
        for lineage in value["lineage"]:
            validate_record("lineage", lineage)
            if lineage["tenant"] != value["tenant"] or (value["outcome"] != "denied" and lineage["trust"] != "verified"):
                raise ValueError("lineage unavailable or outside tenant")
    if name == "request" and sum(a["bytes"] for a in value["attachments"]) > 1048576:
        raise ValueError("aggregate attachments")
    if name == "event":
        payload_name = {"proposal": "request", "decision": "decision", "refusal": "refusal"}[value["kind"]]
        validate_record(payload_name, value["payload"])
        payload = value["payload"]
        request_digest = record_digest("decision-request", payload) if payload_name == "request" else payload["request_digest"]
        if (value["tenant"] != payload["tenant"] or value["request_digest"] != request_digest or
                value["operation_id"] != payload["operation_id"]):
            raise ValueError("event context")
        if (value["sequence"] == 1) != (value["prior_event_digest"] is None):
            raise ValueError("event predecessor")
        if value["payload_digest"] != record_digest("decision-event-payload", payload):
            raise ValueError("event payload digest")


def record_digest(domain, value):
    return "sha256:" + hashlib.sha256(("munarium:" + domain + ":v1\0").encode() +
        canonical(json.dumps(value, ensure_ascii=False).encode())).hexdigest()


def verify_ack(event, ack):
    validate_record("event", event)
    validate_record("ack", ack)
    if any(event[key] != ack[key] for key in ("tenant", "event_id", "payload_digest")) or ack["event_digest"] != record_digest("decision-event", event):
        raise ValueError("acknowledgement binding")


def b64(raw):
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def unb64(text):
    if not isinstance(text, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", text):
        raise ValueError("base64url")
    raw = base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
    if b64(raw) != text:
        raise ValueError("noncanonical base64url")
    return raw


def token_digest(token):
    return "sha256:" + hashlib.sha256(".".join(token[k] for k in ("protected", "payload", "signature")).encode()).hexdigest()


def verify_chain(tokens, context, keys, openssl):
    """Use independently supplied fixture state; neither tokens nor schemas grant authority."""
    if not context["authority_available"] or context["restore_quarantined"]:
        raise ValueError("authority unavailable")
    if not 1 <= len(tokens) <= 5:
        raise ValueError("delegation depth")
    parent = None
    seen = set()
    for index, token in enumerate(tokens):
        if set(token) != {"protected", "payload", "signature"}:
            raise ValueError("JWS fields")
        header_raw, payload_raw = unb64(token["protected"]), unb64(token["payload"])
        if canonical(header_raw) != header_raw or canonical(payload_raw) != payload_raw:
            raise ValueError("noncanonical signed JSON")
        header, payload = json.loads(header_raw), json.loads(payload_raw)
        if set(header) != {"alg", "kid", "typ"} or header["alg"] != "Ed25519" or header["typ"] != "munarium-principal+jws":
            raise ValueError("protected header")
        key = keys.get(header["kid"])
        if key is None or header["kid"] in context["retired_keys"]:
            raise ValueError("unknown or retired key")
        public, signature = unb64(key["public_key"]), unb64(token["signature"])
        if len(public) != 32 or len(signature) != 64:
            raise ValueError("key/signature size")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "public.der").write_bytes(bytes.fromhex("302a300506032b6570032100") + public)
            (path / "signature").write_bytes(signature)
            (path / "input").write_bytes((token["protected"] + "." + token["payload"]).encode())
            result = subprocess.run([openssl, "pkeyutl", "-verify", "-pubin", "-keyform", "DER",
                                     "-inkey", str(path / "public.der"), "-rawin", "-in", str(path / "input"),
                                     "-sigfile", str(path / "signature")], capture_output=True, timeout=5)
            if result.returncode:
                raise ValueError("signature")
        validate_record("principal", payload)
        if payload["issuer"] != key["issuer"] or payload["purpose"] not in key["purposes"]:
            raise ValueError("issuer/purpose")
        for name in ("deployment", "tenant", "audience"):
            if payload[name] != context[name]:
                raise ValueError("context binding")
        if not payload["iat"] <= payload["nbf"] <= context["now"] - 2 or context["now"] + 2 >= payload["exp"]:
            raise ValueError("validity")
        if payload["exp"] - payload["iat"] > (300 if payload["purpose"] == "bootstrap" else 60):
            raise ValueError("lifetime")
        if payload["actor"] in seen:
            raise ValueError("cycle")
        seen.add(payload["actor"])
        if parent is None:
            if payload["parent_digest"] is not None or payload["origin"] != payload["actor"]:
                raise ValueError("root origin")
        else:
            if payload["parent_digest"] != token_digest(tokens[index - 1]):
                raise ValueError("parent binding")
            if any(payload[k] != parent[k] for k in ("origin", "origin_kind", "purpose")):
                raise ValueError("origin/purpose changed")
            if (not set(payload["scopes"]) <= set(parent["scopes"]) or
                    not set(payload["resources"]) <= set(parent["resources"]) or
                    payload["nbf"] < parent["nbf"] or payload["exp"] > parent["exp"]):
                raise ValueError("attenuation")
            if {"govern", "ratify"} & set(payload["scopes"]):
                raise ValueError("delegated authority")
        if payload["origin_kind"] == "agent" and {"govern", "ratify"} & set(payload["scopes"]):
            raise ValueError("agent authority")
        if payload["purpose"] == "bootstrap":
            if len(tokens) != 1 or payload["origin_kind"] != "human" or payload["origin"] not in context["enrolled_humans"]:
                raise ValueError("bootstrap enrollment")
            if payload["bootstrap"] != context["expected_bootstrap"] or context["bootstrap_retired"]:
                raise ValueError("bootstrap state")
        elif payload["bootstrap"] is not None:
            raise ValueError("unexpected bootstrap")
        parent = payload
    if parent["service"] != context["peer_service"]:
        raise ValueError("service peer")
    return parent


def openssl_path():
    found = shutil.which("openssl")
    if not found:
        fallback = Path("C:/Program Files/Git/usr/bin/openssl.exe")
        found = str(fallback) if fallback.is_file() else None
    if not found:
        raise RuntimeError("OpenSSL 3+ is required for signed-vector tests")
    return found
