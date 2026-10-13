#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent offline journal oracle; supplied fixture trust is not authentication."""
import hashlib
import json

from stage2_contract import Oracle, digest, encoded, refuse

MUTABLE = {
    "gate_activation_cells": {"epoch", "digest", "paused", "transition_id"},
    "gate_activation_transitions": {"applied", "resumed"},
    "gate_activation_delivery": {"acknowledgement"},
    "gate_action_claims": {"consumption"},
    "gate_action_reservations": {"unresolved"},
    "gate_action_outbox": {"acknowledgement"},
    "gate_action_dispatch": {"outcome"},
}


class JournalOracle(Oracle):
    def __init__(self, schema, profile):
        super().__init__(schema, profile, {})
        self.tables = profile["tables"]

    def identity(self, table, key):
        if table not in self.tables:
            refuse("InvalidShape")
        return table, encoded(key)

    def scope(self, value, trusted):
        if isinstance(value, dict):
            # Qualified references carry objects; SQL rows carry canonical TEXT.
            # SQL scope is checked separately against the complete row/key shape.
            if isinstance(value.get("scope"), dict) and value["scope"] != trusted["scope"]:
                refuse("Unauthorized")
            for child in value.values():
                self.scope(child, trusted)
        elif isinstance(value, list):
            for child in value:
                self.scope(child, trusted)

    def row(self, table, key, row, scope):
        self.shape(row, self.schema["$defs"][table + "-row"])
        expected = {k: row[k] for k in self.tables[table]["keys"]}
        if key != expected or row["scope"] != encoded(scope).decode():
            refuse("InvalidBinding")
        # SQL TEXT columns holding producer records remain exact canonical JSON.
        for name in ("record", "pause", "applied", "registration", "binding", "claim",
                     "consumption", "receipt", "event", "acknowledgement", "source", "admission", "outcome"):
            if name in row and row[name] is not None:
                self.scope(self.embedded(row[name]), {"scope": scope})

    @staticmethod
    def embedded(raw):
        from test_decision_json_vectors import canonical
        try:
            if canonical(raw.encode()) != raw.encode():
                refuse("InvalidBinding")
            return json.loads(raw)
        except (ValueError, UnicodeError, RecursionError):
            refuse("InvalidBinding")

    def snapshot(self, rows, scope):
        result, previous = {}, None
        for entry in rows:
            if set(entry) != {"table", "key", "row"}:
                refuse("InvalidShape")
            table, key, row = entry["table"], entry["key"], entry["row"]
            identity = self.identity(table, key)
            if previous is not None and identity <= previous:
                refuse("InvalidBinding")
            self.row(table, key, row, scope)
            result[identity], previous = entry, identity
        return result

    def state_digest(self, rows, scope):
        self.snapshot(rows, scope)
        result = hashlib.sha256(b"munarium:stage2:journal-state:v1\0")
        result.update(encoded({"scope": scope, "tables": sorted(self.tables)}) + b"\0")
        for entry in rows:
            result.update(encoded(entry) + b"\0")
        return "sha256:" + result.hexdigest()

    def replay(self, rows, delta, scope):
        state, previous = self.snapshot(rows, scope), None
        for change in delta:
            self.shape(change, self.schema["$defs"]["delta"])
            table, key = change["table"], change["key"]
            identity = self.identity(table, key)
            if previous is not None and identity <= previous:
                refuse("InvalidBinding")
            previous = identity
            before, after = change["before"], change["after"]
            if after is None or before == after:
                refuse("InvalidBinding")  # no tombstone deletion or no-op mutation
            for row in (before, after):
                if row is not None:
                    self.row(table, key, row, scope)
            if state.get(identity, {}).get("row") != before:
                refuse("InvalidBinding")
            if before is not None:
                changed = {k for k in after if before[k] != after[k]}
                if changed - MUTABLE.get(table, set()):
                    refuse("InvalidBinding")
                for column in changed - {"epoch", "digest", "paused", "transition_id"}:
                    if column == "unresolved":
                        valid = before[column] is True and after[column] is False
                    elif column == "resumed":
                        valid = before[column] is False and after[column] is True
                    else:
                        valid = before[column] is None and after[column] is not None
                    if not valid:
                        refuse("InvalidBinding")
                if table == "gate_activation_cells" and after["epoch"] < before["epoch"]:
                    refuse("InvalidBinding")
            state[identity] = {"table": table, "key": key, "row": after}
        return [state[k] for k in sorted(state)]

    def footprints(self, intent, after):
        by_operation = {}
        for entry in after:
            row = entry["row"]
            if "operation" in row:
                by_operation.setdefault(row["operation"], {})[entry["table"]] = row
        required = {}
        for change in intent["proposed_delta"]:
            row, before, table = change["after"], change["before"], change["table"]
            consume = table == "gate_action_claims" and row["consumption"] is not None and (
                before is None or before["consumption"] is None)
            send = table == "gate_action_dispatch" and before is None
            if not (consume or send):
                continue
            operation = row["operation"]
            owned = by_operation[operation]
            consumption = self.embedded(owned["gate_action_claims"]["consumption"])
            payload, binding = consumption["consumption"]["payload"], consumption["binding"]
            reservations = [e["row"] for e in after if e["table"] == "gate_action_reservations"
                            and e["row"]["operation"] == operation]
            if any(not r["unresolved"] for r in reservations):
                refuse("InvalidBinding")
            targets = payload["reservations"]
            target = targets[0]["target"]
            limits = {"target:" + encoded(target).decode(): 2}
            limits.update({"policy:" + k: v for k, v in binding["limits"].items()})
            if (len(targets) != len(reservations) or any(t["target"] != target or t["units"] != 1 for t in targets)
                    or payload["worker"] != binding["worker"] or payload["operation"]["id"] != operation
                    or payload["grant"] != binding["grant_event"]["payload"]["grant"]
                    or owned["gate_action_grants"]["grant_id"] != payload["grant"]["id"]):
                refuse("InvalidBinding")
            invocation = None
            if send:
                send_payload = self.embedded(row["admission"])["payload"]
                for field in ("operation", "attempt", "grant", "worker", "worker_fence"):
                    if send_payload[field] != payload[field]:
                        refuse("InvalidBinding")
                if send_payload["target"] != target:
                    refuse("InvalidBinding")
                invocation = send_payload["invocation"]
            buckets = [{"bucket": r["bucket"], "window_start": r["window_start"], "units": 1,
                            "limit": limits[r["bucket"]]} for r in sorted(reservations, key=lambda r: r["bucket"])]
            if (set(limits) != {r["bucket"] for r in reservations}
                    or sorted(t["window_start"] for t in targets) != sorted(r["window_start"] for r in reservations)):
                refuse("InvalidBinding")
            required[operation] = {"operation": payload["operation"], "attempt": payload["attempt"],
                "target": target, "grant": payload["grant"], "worker": payload["worker"], "worker_fence": payload["worker_fence"],
                "invocation": invocation, "send_spent": send, "buckets": buckets}
            if ("send" if send else "consume") not in intent["mutation_kinds"]:
                refuse("InvalidBinding")
        if intent["exposure"] != [required[k] for k in sorted(required)]:
            refuse("InvalidBinding")
        for change in intent["proposed_delta"]:
            if (change["table"] in {"gate_action_grants", "gate_action_reservations"} and change["before"] is None
                    and (change["after"]["operation"] not in required or "consume" not in intent["mutation_kinds"])):
                refuse("InvalidBinding")
            if change["table"] == "gate_action_outbox" and change["before"] is None:
                payload = self.embedded(change["after"]["event"])["payload"]
                if payload["kind"] in {"consumption-reserved", "send-intent"}:
                    if payload["operation"]["id"] not in required:
                        refuse("InvalidBinding")
                    if payload["kind"] == "send-intent" and not required[payload["operation"]["id"]]["send_spent"]:
                        refuse("InvalidBinding")
        for footprint in required.values():
            if {"operation": footprint["operation"], "attempt": footprint["attempt"]} not in intent["operations"]:
                refuse("InvalidBinding")

    def verify(self, value, trusted):
        try:
            self._verify(value, trusted)
        except (KeyError, TypeError, IndexError):
            refuse("InvalidBinding")

    def _verify(self, value, trusted):
        encoded(value)
        self.shape(value)
        self.scope(value, trusted)
        if not trusted["authorized"]:
            refuse("Unauthorized")
        kind, enrollment = value["type"], trusted["enrollment"]
        write = kind in {"journal-enrollment", "journal-intent", "journal-commit"}
        admitted = trusted["service"] == enrollment["owner"] if write else trusted["service"] in trusted["readers"]
        if not admitted:
            refuse("Unauthorized")
        if kind == "journal-enrollment":
            if value != enrollment or value["initial_state_digest"] != self.state_digest([], trusted["scope"]):
                refuse("InvalidBinding")
            return
        if kind == "journal-policy":
            if value["enrollment"] != enrollment or value["readers"] != trusted["readers"]:
                refuse("InvalidBinding")
            return
        if (value["journal"] != enrollment["journal"] or value["source_generation"] != enrollment["source_generation"]
                or value["enrollment_digest"] != digest("journal-enrollment", enrollment)):
            refuse("Unauthorized")
        if kind == "journal-intent":
            if trusted["pending"] is not None:
                if value != trusted["pending"]:
                    refuse("InvalidSequence")
                return  # factual retry only; no permission is returned
            if value["sequence"] != trusted["sequence"] + 1 or value["prior_checkpoint_digest"] != trusted["checkpoint"]:
                refuse("InvalidSequence")
            rows = self.replay(trusted["rows"], value["proposed_delta"], trusted["scope"])
            if (value["before_state_digest"] != self.state_digest(trusted["rows"], trusted["scope"])
                    or value["after_state_digest"] != self.state_digest(rows, trusted["scope"])
                    or value["delta_digest"] != digest("journal-delta", {"rows": value["proposed_delta"]})
                    or value["audit"] != trusted["audit"]):
                refuse("InvalidBinding")
            self.footprints(value, rows)
        elif kind == "journal-commit":
            intent = trusted["pending"]
            if intent is None or value["sequence"] != intent["sequence"] or value["intent_digest"] != digest("journal-intent", intent):
                refuse("InvalidSequence")
            if value["delta"] != intent["proposed_delta"] or value["after_state_digest"] != intent["after_state_digest"]:
                refuse("InvalidBinding")
        elif kind == "journal-receipt":
            if value != trusted["receipt"]:
                refuse("InvalidBinding")
        elif kind == "journal-head":
            if (value["checkpoint_digest"] != trusted["checkpoint"] or value["sequence"] != trusted["sequence"]
                    or value["state_digest"] != self.state_digest(trusted["rows"], trusted["scope"])
                    or value["pending_intent"] != trusted["pending"] or value["latest_receipt"] != trusted["receipt"]):
                refuse("InvalidBinding")

    def wire(self, raw, trusted):
        from test_decision_json_vectors import canonical
        try:
            if canonical(raw) != raw:
                refuse("InvalidShape")
            value = json.loads(raw)
        except (ValueError, UnicodeError, RecursionError):
            refuse("InvalidShape")
        self.verify(value, trusted)
        return value
