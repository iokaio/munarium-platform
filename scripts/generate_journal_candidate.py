#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reproduce a separate, inert journal candidate; never replace a locked version."""
import argparse
import hashlib
import json
from pathlib import Path

from generate_stage2_candidate import (
    HASH,
    ID,
    POSITIVE,
    UINT,
    arr,
    canonical,
    const,
    digest,
    enum,
    nullable,
    obj,
    ref,
)
from generate_stage2_candidate import fixtures as action_fixtures

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/decisions/journal-v1"
PROFILE = "stage2-journal-checkpoint-v1"
TEXT = {"type": "string", "minLength": 1, "maxLength": 65536}
BOOL = {"type": "boolean"}
# Complete owner columns and primary keys from Gate migrations 0001 through 0005.
TABLES = {
    "gate_activation_cells": (["scope"], {"scope": TEXT, "initial_epoch": POSITIVE,
        "initial_digest": HASH, "epoch": POSITIVE, "digest": HASH, "paused": BOOL, "transition_id": nullable(TEXT)}),
    "gate_activation_transitions": (["scope", "id"], {"scope": TEXT, "id": TEXT, "record": TEXT,
        "pause": TEXT, "applied": nullable(TEXT), "resumed": BOOL}),
    "gate_activation_outbox": (["sequence"], {"sequence": POSITIVE, "scope": TEXT, "id": TEXT,
        "phase": TEXT, "record": TEXT}),
    "gate_activation_delivery": (["scope", "id"], {"scope": TEXT, "id": TEXT, "sequence": POSITIVE,
        "event": TEXT, "acknowledgement": nullable(TEXT)}),
    "gate_action_enrollment": (["scope"], {"scope": TEXT, "registration": TEXT}),
    "gate_action_claims": (["scope", "operation"], {"scope": TEXT, "operation": TEXT,
        "binding": TEXT, "claim": TEXT, "consumption": nullable(TEXT)}),
    "gate_action_cancellations": (["scope", "operation", "attempt", "approval"],
        {"scope": TEXT, "operation": TEXT, "attempt": TEXT, "approval": TEXT, "withdrawal": TEXT, "receipt": TEXT}),
    "gate_action_grants": (["scope", "grant_id"], {"scope": TEXT, "grant_id": TEXT, "operation": TEXT}),
    "gate_action_reservations": (["scope", "operation", "bucket"], {"scope": TEXT,
        "operation": TEXT, "bucket": TEXT, "window_start": UINT, "unresolved": BOOL}),
    "gate_action_outbox": (["scope", "sequence"], {"scope": TEXT, "sequence": POSITIVE,
        "event": TEXT, "acknowledgement": nullable(TEXT)}),
    "gate_action_sources": (["scope", "operation"], {"scope": TEXT, "operation": TEXT, "source": TEXT}),
    "gate_action_dispatch": (["scope", "operation"], {"scope": TEXT, "operation": TEXT,
        "admission": TEXT, "outcome": nullable(TEXT)}),
    "gate_execution_generation": (["scope"], {"scope": TEXT, "generation": POSITIVE}),
    "gate_action_reconciliations": (["scope", "operation"], {"scope": TEXT, "operation": TEXT,
        "receipt": TEXT, "event": TEXT}),
}
KINDS = ["activation", "enrollment", "source", "claim", "cancel", "consume", "send",
         "outcome", "reconcile", "acknowledgement"]


def record(kind, **fields):
    return obj(schema_version=const(1), profile=const(PROFILE), type=const(kind), **fields)


def schema():
    defs = {"scope": obj(domain=ID, tenant=ID, deployment=ID, cell=ID)}
    for kind in ("journal", "ledger", "operation", "attempt", "target", "grant", "invocation"):
        defs[kind + "-ref"] = obj(scope=ref("scope"), kind=const(kind), id=ID)
    defs["audit"] = obj(ledger=ref("ledger-ref"), cutoff=UINT, checkpoint_digest=HASH)
    delta_shapes = []
    for table, (keys, columns) in sorted(TABLES.items()):
        defs[table + "-row"] = obj(**columns)
        delta_shapes.append(obj(table=const(table), key=obj(**{k: columns[k] for k in keys}),
            before=nullable(ref(table + "-row")), after=nullable(ref(table + "-row"))))
    defs["delta"] = {"anyOf": delta_shapes}
    defs["operation"] = obj(operation=ref("operation-ref"), attempt=ref("attempt-ref"))
    defs["bucket"] = obj(bucket=TEXT, window_start=UINT, units=const(1), limit=POSITIVE)
    defs["exposure"] = obj(operation=ref("operation-ref"), attempt=ref("attempt-ref"),
        target=ref("target-ref"), grant=ref("grant-ref"), worker=ID, worker_fence=POSITIVE,
        invocation=nullable(ref("invocation-ref")), send_spent=BOOL,
        buckets=arr(ref("bucket"), minimum=1, maximum=32))
    defs["journal-enrollment"] = record("journal-enrollment", journal=ref("journal-ref"),
        owner=ID, source_generation=POSITIVE, initial_state_digest=HASH, audit=ref("audit"),
        baseline=obj(empty_journal={"type": "boolean", "const": True},
                     empty_target={"type": "boolean", "const": True}, evidence_digest=HASH))
    common = {"journal": ref("journal-ref"), "source_generation": POSITIVE, "enrollment_digest": HASH}
    defs["journal-intent"] = record("journal-intent", **common, sequence=POSITIVE,
        prior_checkpoint_digest=HASH, before_state_digest=HASH, after_state_digest=HASH,
        delta_digest=HASH, proposed_delta=arr(ref("delta"), minimum=1, maximum=256),
        mutation_kinds=arr(enum(*KINDS), minimum=1, maximum=len(KINDS)),
        operations=arr(ref("operation"), maximum=32), audit=ref("audit"),
        exposure=arr(ref("exposure"), maximum=32))
    defs["journal-commit"] = record("journal-commit", **common, sequence=POSITIVE,
        intent_digest=HASH, after_state_digest=HASH,
        delta=arr(ref("delta"), minimum=1, maximum=256))
    defs["journal-receipt"] = record("journal-receipt", **common,
        record_type=enum("journal-enrollment", "journal-intent", "journal-commit"),
        record_digest=HASH, ledger=ref("ledger-ref"), ledger_position=POSITIVE, received_at=UINT)
    defs["journal-head"] = record("journal-head", **common, sequence=UINT,
        checkpoint_digest=HASH, state_digest=HASH,
        pending_intent=nullable(ref("journal-intent")), latest_receipt=ref("journal-receipt"))
    defs["journal-policy"] = record("journal-policy", enrollment=ref("journal-enrollment"),
        readers=arr(ID, maximum=32))
    defs["head-request"] = obj(kind=const("journal-head"), journal=ref("journal-ref"))
    defs["record-request"] = obj(kind=const("journal-record"), record={"anyOf": [
        ref(k) for k in ("journal-enrollment", "journal-intent", "journal-commit")]})
    defs["lookup-request"] = obj(kind=const("journal-lookup"), journal=ref("journal-ref"), record_digest=HASH)
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$defs": defs,
            "anyOf": [ref(k) for k in ("journal-enrollment", "journal-intent", "journal-commit",
                                      "journal-receipt", "journal-head", "journal-policy")]}


def state_digest(scope, rows):
    result = hashlib.sha256(b"munarium:stage2:journal-state:v1\0")
    result.update(canonical({"scope": scope, "tables": sorted(TABLES)}) + b"\0")
    for row in rows:
        result.update(canonical(row) + b"\0")
    return "sha256:" + result.hexdigest()


def fixtures():
    _, actions, _ = action_fixtures()
    scope = actions["request"]["operation"]["scope"]
    journal = {"scope": scope, "kind": "journal", "id": "fixture-gate-journal"}
    ledger = {"scope": scope, "kind": "ledger", "id": "fixture-journal-ledger"}
    audit = {"ledger": ledger, "cutoff": 0, "checkpoint_digest": digest("fixture-audit", {"empty": True})}
    base = {"schema_version": 1, "profile": PROFILE}
    enrollment = dict(base, type="journal-enrollment", journal=journal, owner="fixture-gate",
        source_generation=1, initial_state_digest=state_digest(scope, []), audit=audit,
        baseline={"empty_journal": True, "empty_target": True, "evidence_digest": digest("fixture-baseline", {"empty": True})})
    row = {"scope": canonical(scope).decode(), "initial_epoch": 1, "initial_digest": "sha256:" + "1" * 64,
        "epoch": 1, "digest": "sha256:" + "1" * 64, "paused": True, "transition_id": None}
    delta = [{"table": "gate_activation_cells", "key": {"scope": row["scope"]}, "before": None, "after": row}]
    after = state_digest(scope, [{"table": delta[0]["table"], "key": delta[0]["key"], "row": row}])
    common = {"journal": journal, "source_generation": 1, "enrollment_digest": digest("journal-enrollment", enrollment)}
    intent = dict(base, type="journal-intent", **common, sequence=1,
        prior_checkpoint_digest=common["enrollment_digest"], before_state_digest=enrollment["initial_state_digest"],
        after_state_digest=after, delta_digest=digest("journal-delta", {"rows": delta}),
        proposed_delta=delta, mutation_kinds=["activation"], operations=[], audit=audit, exposure=[])
    commit = dict(base, type="journal-commit", **common, sequence=1,
        intent_digest=digest("journal-intent", intent), after_state_digest=after, delta=delta)
    receipt = dict(base, type="journal-receipt", **common, record_type="journal-commit",
        record_digest=digest("journal-commit", commit), ledger=ledger, ledger_position=3, received_at=1000)
    head = dict(base, type="journal-head", **common, sequence=1,
        checkpoint_digest=receipt["record_digest"], state_digest=after, pending_intent=None, latest_receipt=receipt)
    records = {"enrollment": enrollment, "intent": intent, "commit": commit, "receipt": receipt,
                   "head": head, "policy": dict(base, type="journal-policy", enrollment=enrollment, readers=["fixture-reader"])}
    cases = []
    for name, path, replacement, expected in [
        ("foreign-scope", "journal.scope.tenant", "other-tenant", "Unauthorized"),
        ("changed-generation", "source_generation", 2, "Unauthorized"),
        ("stale-prior", "prior_checkpoint_digest", "sha256:" + "0" * 64, "InvalidSequence"),
        ("sequence-gap", "sequence", 2, "InvalidSequence"),
        ("wrong-delta-digest", "delta_digest", "sha256:" + "0" * 64, "InvalidBinding"),
        ("wrong-after-state", "after_state_digest", "sha256:" + "0" * 64, "InvalidBinding"),
        ("unknown-kind", "mutation_kinds.0", "refund", "InvalidShape"),
        ("unknown-table", "proposed_delta.0.table", "uncovered_table", "InvalidShape"),
        ("wrong-row-scope", "proposed_delta.0.after.scope", "{}", "InvalidBinding"),
        ("wrong-row-key", "proposed_delta.0.after.scope", canonical(dict(scope, cell="other-cell")).decode(), "InvalidBinding"),
    ]:
        cases.append({"id": name, "record": "intent", "changes": {path: replacement}, "expected": expected})
    return {"profile": PROFILE, "records": records, "initial_rows": [], "cases": cases,
        "canonical": {k: canonical(v).decode() for k, v in records.items()},
        "digests": {k: digest(v["type"], v) for k, v in records.items()}}


def generated_files(readme):
    profile = {"schema_version": 1, "profile": PROFILE, "status": "candidate-not-qualified",
        "executable_authority": False, "canonicalization": "decision-json-v1", "max_record_bytes": 65536,
        "max_delta_rows": 256, "max_pending_intents": 1, "custody_seconds": 5, "clock_uncertainty_seconds": 2,
        "state_digest": "domain + canonical(scope,tables) NUL + sorted canonical(table,key,row) NUL",
        "tables": {name: {"keys": keys, "columns": columns} for name, (keys, columns) in sorted(TABLES.items())}}
    def pretty(value):
        return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
    contents = {"README.md": readme.replace(b"\r\n", b"\n"), "schema.json": pretty(schema()),
                "profile.json": pretty(profile), "vectors.json": pretty(fixtures())}
    hashes = {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(contents.items())}
    aggregate = "".join(name + "\0" + sha + "\n" for name, sha in hashes.items()).encode()
    contents["bundle-lock.json"] = pretty({"status": "candidate-not-accepted-not-released",
        "profile": PROFILE, "files": hashes, "bundle_sha256": hashlib.sha256(aggregate).hexdigest()})
    return contents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contents = generated_files((DIRECTORY / "README.md").read_bytes())
    if args.check:
        for name, raw in contents.items():
            if (DIRECTORY / name).read_bytes().replace(b"\r\n", b"\n") != raw:
                raise SystemExit("candidate differs from generator: " + name)
        print("Journal candidate reproduction passed; no files changed.")
        return
    if any((DIRECTORY / name).exists() for name in contents if name != "README.md"):
        raise SystemExit("refusing existing candidate artifact; use a new reviewed namespace")
    for name, raw in contents.items():
        if name != "README.md":
            (DIRECTORY / name).write_bytes(raw)
    print("Created inert journal candidate; no activation or accepted contract.")


if __name__ == "__main__":
    main()
