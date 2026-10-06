#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline ADR-0005 review oracle; trusted fixture facts are not authentication.

Never import this into a runtime. Provider, registry and transport verification are
absent. Delegation cases alone use the existing signed principal corpus/OpenSSL.
"""
import copy
import hashlib
import json
import unittest

from candidate_contract import (FIXTURES, check_schema, openssl_path, unb64,
                                validate, verify_chain)


SCHEMA = json.loads((FIXTURES / "warden-admission.schema.json").read_text(encoding="utf-8"))
VECTORS = json.loads((FIXTURES / "warden-admission-vectors.json").read_text(encoding="utf-8"))
SIGNED = json.loads((FIXTURES / "identity-vectors.json").read_text(encoding="utf-8"))


def expanded(value, stack=()):
    """Resolve only this review schema's acyclic local definitions for the old checker."""
    if isinstance(value, list):
        return [expanded(item, stack) for item in value]
    if not isinstance(value, dict):
        return value
    if "$ref" in value:
        reference = value["$ref"]
        name = reference.removeprefix("#/$defs/")
        if (set(value) != {"$ref"} or not reference.startswith("#/$defs/")
                or name not in SCHEMA["$defs"] or name in stack):
            raise ValueError("unsupported schema reference")
        return expanded(SCHEMA["$defs"][name], (*stack, name))
    return {key: expanded(item, stack) for key, item in value.items()}


DEFINITIONS = {name: expanded(value) for name, value in SCHEMA["$defs"].items()}


def record(name, value):
    validate(value, DEFINITIONS[name])


def current(value, now):
    for field in ("nbf", "exp"):
        record("timestamp", value[field])
    if not value["nbf"] <= now - 2 < now + 2 < value["exp"]:
        raise ValueError("unavailable interval")


def authority(context):
    if context["authority_available"] is not True or context["restore_quarantined"] is not False:
        raise ValueError("authority unavailable")


def capped(request, *caps):
    for field in ("scopes", "resources"):
        record(field, request[field])
        for cap in caps:
            record(field, cap[field])
            if not set(request[field]) <= set(cap[field]):
                raise ValueError("authority widening")


def mapping(data):
    context, upstream, request = data["context"], data["upstream"], data["request"]
    authority(context)
    if upstream["audience"] != context["upstream_audience"]:
        raise ValueError("upstream audience")
    record("kind", upstream["subject_kind"])
    for binding in data["bindings"]:
        record("provider_binding", binding)
    matches = [binding for binding in data["bindings"]
               if binding["deployment"] == context["deployment"]
               and binding["tenant"] == context["tenant"]
               and binding["provider_issuer"] == upstream["issuer"]
               and binding["provider_subject"] == upstream["subject"]]
    if len(matches) != 1:
        raise ValueError("missing or ambiguous binding")
    binding = matches[0]
    if (binding["origin_kind"] != upstream["subject_kind"]
            or binding["peer_service"] != context["peer_service"]
            or request["audience"] not in binding["audiences"]):
        raise ValueError("identity binding")
    for item in (upstream, binding, data["task"], data["policy"]):
        current(item, context["now"])
    capped(request, binding, data["task"], data["policy"])
    return dict(origin=binding["origin"], origin_kind=binding["origin_kind"],
                actor=binding["origin"], service=context["peer_service"],
                scopes=sorted(request["scopes"]), resources=sorted(request["resources"]))


def delegation(data, openssl):
    authority(data["context"])
    case = next(case for case in SIGNED["cases"] if case["id"] == data["signed_case"])
    leaf = verify_chain(case["tokens"], case["context"], SIGNED["keys"], openssl)
    chain = [json.loads(unb64(token["payload"])) for token in case["tokens"]]
    depth = len(chain) - 1
    if not 1 <= depth <= data["context"]["max_depth"] <= 4:
        raise ValueError("task depth")
    identifiers = []
    for registration in data["registrations"]:
        record("delegation_registration", registration)
        identifiers.append(registration["registration_id"])
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate registration identity")
    admitted = []
    for parent, child in zip(chain, chain[1:]):
        matches = [r for r in data["registrations"]
                   if all(r[field] == child[field] for field in
                          ("deployment", "tenant", "origin", "origin_kind", "audience"))
                   and r["from_actor"] == parent["actor"] and r["to_actor"] == child["actor"]
                   and r["presenter_service"] == child["service"]]
        if len(matches) != 1:
            raise ValueError("missing or ambiguous edge")
        registration = matches[0]
        if depth > registration["max_depth"] or any(
                registration[field] != data["context"][field]
                for field in ("task_digest", "policy_digest")):
            raise ValueError("registration context")
        capped(child, registration, data["task"], data["policy"])
        for cap in (registration, data["task"], data["policy"]):
            current(cap, case["context"]["now"])
            if child["nbf"] < cap["nbf"] or child["exp"] > cap["exp"]:
                raise ValueError("delegation interval")
        admitted.append(registration["registration_id"])
    return {**{field: leaf[field] for field in ("actor", "origin", "origin_kind")},
            "registrations": admitted}


def forwarding(data):
    value, context = data["record"], data["context"]
    record("forwarded_attribution", value)
    if (context["evidence_available"] is not True or context["sender_admitted"] is not True
            or context["requires_original_authority"] is not False):
        raise ValueError("attribution cannot authorize")
    for field in ("deployment", "tenant", "principal_digest", "request_digest"):
        if value[field] != context[field]:
            raise ValueError("evidence binding")
    if (value["sender_service"] != context["peer_service"]
            or value["recipient_service"] != context["audience"]):
        raise ValueError("service binding")
    return dict(caller=context["peer_service"], attribution_only=True,
                original_actor_authority=False)


class WardenAdmission(unittest.TestCase):
    def test_additive_candidate_lock(self):
        lock = json.loads((FIXTURES / "warden-admission-lock.json").read_text(encoding="utf-8"))
        foundation = json.loads((FIXTURES / "candidate-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["status"], "proposed-not-released")
        self.assertEqual(lock["foundation_bundle_sha256"], foundation["bundle_sha256"])
        self.assertEqual(set(lock["files"]),
                         {"warden-admission.schema.json", "warden-admission-vectors.json"})
        lines = []
        for name, expected in sorted(lock["files"].items()):
            actual = hashlib.sha256((FIXTURES / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            self.assertEqual(actual, expected, name)
            lines.append(name + "\0" + actual + "\n")
        self.assertEqual(lock["bundle_sha256"], hashlib.sha256("".join(lines).encode()).hexdigest())

    def test_schema_and_closed_records(self):
        for definition in DEFINITIONS.values():
            check_schema(definition)
        examples = {
            "provider_binding": VECTORS["bases"]["mapping"]["bindings"][0],
            "delegation_registration": VECTORS["bases"]["delegation"]["registrations"][0],
            "forwarded_attribution": VECTORS["bases"]["forwarding"]["record"],
        }
        for name, value in examples.items():
            record(name, value)
            for field in value:
                with self.subTest(record=name, missing=field):
                    altered = {key: item for key, item in value.items() if key != field}
                    with self.assertRaises(ValueError):
                        record(name, altered)
            for altered in ({**value, "active": True}, {**value, "schema_version": True}):
                with self.subTest(record=name, malformed=altered):
                    with self.assertRaises(ValueError):
                        record(name, altered)

    def test_admission_vectors(self):
        self.assertEqual(VECTORS["status"], "proposed-not-released")
        self.assertEqual(VECTORS["format"], "warden-admission-review-v1")
        ids = [case["id"] for case in VECTORS["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        openssl = openssl_path()
        operations = {"mapping": mapping, "delegation": lambda data: delegation(data, openssl),
                      "forwarding": forwarding}
        for case in VECTORS["cases"]:
            with self.subTest(case=case["id"]):
                data = copy.deepcopy(VECTORS["bases"][case["operation"]])
                for path, value in case["changes"].items():
                    parent = data
                    parts = [int(part) if part.isdigit() else part for part in path.split(".")]
                    for part in parts[:-1]:
                        parent = parent[part]
                    self.assertIn(parts[-1], range(len(parent)) if isinstance(parent, list) else parent)
                    parent[parts[-1]] = copy.deepcopy(value)
                if "duplicate" in case:
                    values = data[case["duplicate"]]
                    values.append(copy.deepcopy(values[0]))
                self.assertIn(case["expected"], ("accept", "reject"))
                if case["expected"] == "accept":
                    self.assertEqual(operations[case["operation"]](data), data["expected"])
                else:
                    with self.assertRaises(ValueError):
                        operations[case["operation"]](data)

    def test_distinct_registration_ids_do_not_resolve_ambiguous_matches(self):
        openssl = openssl_path()
        for operation, records, identifier, check in (
                ("mapping", "bindings", "binding_id", mapping),
                ("delegation", "registrations", "registration_id",
                 lambda data: delegation(data, openssl))):
            with self.subTest(operation=operation):
                data = copy.deepcopy(VECTORS["bases"][operation])
                duplicate = {**data[records][0], identifier: "different-registration"}
                data[records].append(duplicate)
                with self.assertRaises(ValueError):
                    check(data)

    def test_registration_cannot_rescue_a_rejected_signed_chain(self):
        openssl = openssl_path()
        for signed_case in ("wider-scope", "cycle", "delegated-ratifier", "parent-substitution"):
            with self.subTest(signed_case=signed_case):
                data = copy.deepcopy(VECTORS["bases"]["delegation"])
                data["signed_case"] = signed_case
                with self.assertRaises(ValueError):
                    delegation(data, openssl)


if __name__ == "__main__":
    unittest.main()
