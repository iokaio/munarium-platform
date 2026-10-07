#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline Stage 2 candidate oracle; fixture state is NOT production authority."""
import hashlib
import json
import re

from test_decision_json_vectors import canonical

KEYWORDS = {"$schema", "$defs", "$ref", "type", "const", "enum", "anyOf", "properties", "required",
            "additionalProperties", "items", "minItems", "maxItems", "uniqueItems", "minLength", "maxLength",
            "pattern", "minimum", "maximum"}


def refuse(code):
    raise ValueError(code)


def encoded(value):
    try:
        return canonical(json.dumps(value, ensure_ascii=False, allow_nan=False).encode())
    except (ValueError, UnicodeError, RecursionError):
        refuse("InvalidShape")


def digest(domain, value):
    return "sha256:" + hashlib.sha256(f"munarium:stage2:{domain}:v1\0".encode() + encoded(value)).hexdigest()


class Oracle:
    """Narrow closed-schema subset plus separately supplied fictional trusted state."""
    def __init__(self, schema, profile, records):
        self.schema, self.profile, self.records = schema, profile, records
        self.check_schema(schema)

    def check_schema(self, node):
        if not isinstance(node, dict) or set(node) - KEYWORDS:
            refuse("UnsupportedSchema")
        if "$ref" in node and (set(node) != {"$ref"} or node["$ref"] not in {
                "#/$defs/" + name for name in self.schema["$defs"]}):
            refuse("UnsupportedSchema")
        for group in ("properties", "$defs"):
            for child in node.get(group, {}).values():
                self.check_schema(child)
        for child in node.get("anyOf", []):
            self.check_schema(child)
        if "items" in node:
            self.check_schema(node["items"])

    def shape(self, value, node=None, depth=0):
        if depth > 64:
            refuse("InvalidShape")
        node = self.schema if node is None else node
        if "$ref" in node:
            return self.shape(value, self.schema["$defs"][node["$ref"].split("/")[-1]], depth + 1)
        types = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool, "null": type(None)}
        if "type" in node and type(value) is not types.get(node["type"]):
            refuse("InvalidShape")
        if "const" in node and value != node["const"]:
            refuse("InvalidShape")
        if "enum" in node and value not in node["enum"]:
            refuse("InvalidShape")
        if "anyOf" in node:
            for option in node["anyOf"]:
                try:
                    self.shape(value, option, depth + 1)
                    break
                except ValueError:
                    pass
            else:
                refuse("InvalidShape")
        if isinstance(value, dict):
            props = node.get("properties", {})
            if set(node.get("required", [])) - value.keys():
                refuse("InvalidShape")
            if node.get("additionalProperties") is False and value.keys() - props.keys():
                refuse("InvalidShape")
            for key in value.keys() & props.keys():
                self.shape(value[key], props[key], depth + 1)
        if isinstance(value, list):
            if not node.get("minItems", 0) <= len(value) <= node.get("maxItems", 65536):
                refuse("InvalidShape")
            if node.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
                refuse("InvalidShape")
            if "items" in node:
                for child in value:
                    self.shape(child, node["items"], depth + 1)
        if isinstance(value, str):
            if not node.get("minLength", 0) <= len(value) <= node.get("maxLength", 65536):
                refuse("InvalidShape")
            if "pattern" in node and re.search(node["pattern"], value) is None:
                refuse("InvalidShape")
        if type(value) is int and not node.get("minimum", -9007199254740991) <= value <= node.get("maximum", 9007199254740991):
            refuse("InvalidShape")

    def wire(self, raw, trusted):
        try:
            if canonical(raw) != raw:
                refuse("InvalidShape")
            value = json.loads(raw)
        except (ValueError, UnicodeError, RecursionError):
            refuse("InvalidShape")
        self.verify(value, trusted)
        return value

    def scope(self, value, trusted):
        if isinstance(value, dict):
            if "scope" in value and value["scope"] != trusted["scope"]:
                refuse("Unauthorized")
            for child in value.values():
                self.scope(child, trusted)
        elif isinstance(value, list):
            for child in value:
                self.scope(child, trusted)

    def verify(self, value, trusted):
        encoded(value)
        self.shape(value)
        self.scope(value, trusted)
        handlers = {"action-request": self.request, "action-decision": self.decision,
                    "action-approval": self.approval, "activation": self.activation,
                    "activation-receipt": self.receipt, "accountability-event": self.event, "event-ack": self.ack}
        handlers[value["type"]](value, trusted)
        if value["type"] == "accountability-event":
            current = value["source_generation"] == trusted["streams"][value["stream"]["id"]]["generation"]
            if current and digest("accountability-event", value) not in trusted["authenticated_event_digests"]:
                refuse("Unauthorized")
        if value["type"] == "event-ack" and digest("event-ack", value) not in trusted["authenticated_ack_digests"]:
            refuse("Unauthorized")

    def request(self, value, trusted):
        intent, context, now = value["intent"], value["context"], trusted["now"]
        if any(intent[k] != trusted[k] for k in ("actor", "origin", "task", "delegation_digest")):
            refuse("Unauthorized")
        if intent["actor"]["kind"] == "agent" and (intent["task"]["agent_release"] is None or intent["task"]["agent_instance"] is None):
            refuse("Unauthorized")
        if context["evidence"] != trusted["evidence"] or any(
                e["trust"] != "verified" or e["observed_at"] > now - 2 or now + 2 >= e["expires_at"]
                for e in context["evidence"]):
            refuse("UnavailableEvidence")
        if context != trusted["context"] or any(intent[k] != trusted[k] for k in ("target", "target_precondition", "parameter_schema_digest")):
            refuse("StaleContext")
        if not context["valid_from"] <= now - 2 < now + 2 < context["expires_at"]:
            refuse("Expired")
        if any(value[k + "_digest"] != digest(k, value[k]) for k in ("intent", "context")):
            refuse("InvalidBinding")
        if intent["parameters"]["artifact_digest"] != context["evidence"][0]["content_digest"]:
            refuse("UnavailableEvidence")
        if sum(a["bytes"] for a in intent["attachments"]) > 1048576:
            refuse("InvalidShape")

    def common(self, value):
        request = self.records["request"]
        expected = dict(operation=request["operation"], attempt=request["attempt"],
                        request_digest=digest("action-request", request), context_digest=request["context_digest"])
        if any(value[k] != v for k, v in expected.items()):
            refuse("InvalidBinding")

    def decision(self, value, trusted):
        self.common(value)
        self.request(self.records["request"], trusted)
        if value["outcome"] == "approval-required" and value["obligations"] != trusted["obligations"]:
            refuse("InvalidBinding")
        if value["outcome"] == "denied" and value["obligations"]:
            refuse("InvalidBinding")

    def approval(self, value, trusted):
        self.common(value)
        decision = self.records["decision"]
        self.decision(decision, trusted)
        if decision["outcome"] != "approval-required" or value["decision_digest"] != digest("action-decision", decision):
            refuse("InvalidBinding")
        approver = value["approver"]
        if (approver != trusted["approver"] or approver["kind"] != "human" or
                approver in (trusted["actor"], trusted["origin"]) or approver in trusted["requester_chain"] or
                value["eligibility_revision"] != trusted["eligible_revision"]):
            refuse("Unauthorized")
        if trusted["approval_status"] != "approved":
            refuse("Denied")
        if not value["issued_at"] <= trusted["now"] - 2 < trusted["now"] + 2 < value["expires_at"]:
            refuse("Expired")
        if not 0 < value["expires_at"] - value["issued_at"] <= self.profile["approval_lifetime_seconds"]:
            refuse("Expired")
        if digest("action-approval", value) != trusted["approval_digest"]:
            refuse("InvalidBinding")

    def activation(self, value, trusted):
        if (value["prior_epoch"] != trusted["prior_epoch"] or value["successor_epoch"] <= value["prior_epoch"] or
                value["prior_artifact_set_digest"] != trusted["prior_artifact_set_digest"]):
            refuse("StaleContext")
        if not value["not_before"] <= trusted["now"] - 2 < trusted["now"] + 2 < value["expires_at"]:
            refuse("Expired")
        if value["participants"] != self.profile["participants"] or value["profile_digest"] != digest("profile", self.profile):
            refuse("InvalidBinding")
        if (value["artifact_set_digest"] != digest("artifact-set", {"artifacts": value["artifacts"]}) or
                value["participant_set_digest"] != digest("participants", {"participants": value["participants"]}) or
                len({a["kind"] for a in value["artifacts"]}) != len(value["artifacts"])):
            refuse("InvalidBinding")
        if value["ratification"] != trusted["ratification"] or digest("activation", value) != trusted["ratified_transition_digest"]:
            refuse("Unauthorized")

    def receipt(self, value, trusted):
        activation = self.records["activation"]
        expected = {k: activation[k] for k in ("transition", "prior_epoch", "successor_epoch", "artifact_set_digest", "participant_set_digest")}
        expected["transition_digest"] = digest("activation", activation)
        if any(value[k] != v for k, v in expected.items()):
            refuse("InvalidBinding")
        if value["participant"] not in trusted["authenticated_producers"] or (value["phase"] == "paused" and value["participant"] != "gate"):
            refuse("Unauthorized")
        if digest("activation-receipt", value) not in trusted["authenticated_receipt_digests"]:
            refuse("Unauthorized")

    def completion(self, activation, pause, receipts, trusted):
        """Only checks supplied authenticated receipts; this does not resume Gate."""
        self.verify(activation, trusted)
        if activation != self.records["activation"] or digest("activation", activation) != trusted["paused_transition_digest"]:
            refuse("StaleContext")
        self.verify(pause, trusted)
        if pause["phase"] != "paused" or pause["participant"] != "gate":
            refuse("InvalidBinding")
        if not isinstance(receipts, list):
            refuse("InvalidShape")
        for receipt in receipts:
            self.verify(receipt, trusted)
        if len(receipts) != len(self.profile["participants"]) or sorted(r["participant"] for r in receipts) != self.profile["participants"]:
            refuse("IncompleteActivation")
        for receipt in receipts:
            if receipt["phase"] != "applied":
                refuse("IncompleteActivation")

    def event(self, value, trusted):
        payload, kind = value["payload"], value["kind"]
        if value["payload_digest"] != digest("event-payload", payload) or kind != payload["kind"]:
            refuse("InvalidBinding")
        family = "activation" if kind == "activation-applied" else "action"
        if value["family"] != family:
            refuse("InvalidBinding")
        owner = payload["receipt"]["participant"] if family == "activation" else self.profile["action_event_owners"][kind]
        if value["producer"] != owner:
            refuse("Unauthorized")
        stream_id = value["stream"]["id"]
        cursor = trusted["streams"].get(stream_id)
        if cursor is None or cursor["producer"] != owner:
            refuse("Unauthorized")
        if value["source_generation"] != cursor["generation"]:
            historical = trusted["historical_cursors"].get(stream_id)
            if (not trusted["recovery_recorder_authorized"] or digest("accountability-event", value) not in trusted["historical_events"] or
                    value["source_generation"] >= cursor["generation"] or
                    historical is None or historical["generation"] != value["source_generation"] or
                    historical["producer"] != owner or value["occurred_at"] > trusted["recovery_cutoff"]):
                refuse("Unauthorized")
            cursor = historical
        elif owner not in trusted["authenticated_producers"]:
            refuse("Unauthorized")
        if value["sequence"] != cursor["last_sequence"] + 1 or value["predecessor"] != cursor["last_digest"]:
            refuse("InvalidSequence")
        if family == "activation":
            self.receipt(payload["receipt"], trusted)
            if payload["receipt"]["phase"] != "applied":
                refuse("InvalidBinding")
            return
        self.common(payload)
        request = self.records["request"]
        if (payload["activation_epoch"] != request["context"]["activation"]["revision"] or
                payload["recovery_epoch"] != request["context"]["recovery"]["revision"]):
            refuse("InvalidBinding")
        if "claim" in payload and payload["claim"] != self.records["claim-created"]["payload"]["claim"]:
            refuse("InvalidBinding")
        if "grant" in payload and payload["grant"] != self.records["grant-issued"]["payload"]["grant"]:
            refuse("InvalidBinding")
        if "effect_key" in payload and payload["effect_key"] != request["operation"]["id"]:
            refuse("InvalidBinding")
        if kind == "approval-recorded" and (payload["approval"] != self.records["approval"]["approval"] or
                payload["approval_digest"] != digest("action-approval", self.records["approval"])):
            refuse("InvalidBinding")
        if kind == "claim-created" and payload["grant_binding_digest"] != payload["request_digest"]:
            refuse("InvalidBinding")
        if kind == "consumption-reserved":
            reservations = payload["reservations"]
            if len({r["reservation"]["id"] for r in reservations}) != len(reservations) or any(
                    r["target"] != request["intent"]["target"] or r["root"] != request["intent"]["task"]["root"] or
                    r["window_start"] % self.profile["action_window_seconds"] for r in reservations):
                refuse("InvalidBinding")
        if kind == "predispatch" and payload["consumption_event_digest"] != digest("accountability-event", self.records["consumption-reserved"]):
            refuse("InvalidBinding")
        if kind == "send-intent" and (payload["predispatch_ack_digest"] != digest("event-ack", self.records["ack"]) or
                payload["target"] != request["intent"]["target"]):
            refuse("InvalidBinding")
        if kind in ("outcome", "reconciliation"):
            if payload["effect_status"] != "unresolved" and (not payload["evidence"] or any(
                    e not in trusted["effect_evidence"] for e in payload["evidence"])):
                refuse("UnavailableEvidence")
        if kind == "reconciliation" and payload["prior_outcome_digest"] != digest("accountability-event", self.records["outcome"]):
            refuse("InvalidBinding")

    def ack(self, value, trusted):
        event = next((r for r in self.records.values() if r["type"] == "accountability-event" and r["event_id"] == value["event_id"]), None)
        if event is None or value["ledger"] != trusted["ledger"]:
            refuse("InvalidBinding")
        if value["event_digest"] != digest("accountability-event", event) or value["payload_digest"] != event["payload_digest"]:
            refuse("InvalidBinding")
