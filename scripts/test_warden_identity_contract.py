#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Warden consumer expectations against unchanged hub candidates, not a runtime."""
import base64
import copy
import json
import unittest
from unittest.mock import patch

from candidate_contract import FIXTURES, openssl_path, token_digest, verify_chain


class WardenIdentityContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vectors = json.loads(
            (FIXTURES / "identity-vectors.json").read_text(encoding="utf-8")
        )
        cls.case = next(
            case for case in cls.vectors["cases"] if case["id"] == "valid-delegation"
        )
        cls.openssl = openssl_path()

    def setUp(self):
        self.tokens = copy.deepcopy(self.case["tokens"])
        self.context = copy.deepcopy(self.case["context"])
        self.keys = copy.deepcopy(self.vectors["keys"])

    def verify(self):
        return verify_chain(self.tokens, self.context, self.keys, self.openssl)

    def test_exact_narrowed_principal_without_human_attribution(self):
        self.context["enrolled_humans"] = []
        self.assertEqual(self.verify(), {
            "schema_version": 1,
            "deployment": "fixture",
            "tenant": "alpha",
            "issuer": "fixture-issuer",
            "audience": "svc-server",
            "origin": "agent-a",
            "actor": "agent-b",
            "origin_kind": "agent",
            "service": "svc-harness",
            "purpose": "decision",
            "scopes": ["evaluate"],
            "resources": ["item-a"],
            "iat": 980,
            "nbf": 980,
            "exp": 1030,
            "parent_digest": "sha256:9c55ee330ae7a4c1ed700a7e8e800bd04c593fc58368f10b81dba8b8bdefd11a",
            "bootstrap": None,
        })

    def test_decision_context_cannot_be_substituted(self):
        for field in ("deployment", "tenant", "audience", "peer_service"):
            with self.subTest(field=field):
                self.context = {**self.case["context"], field: "different"}
                with self.assertRaises(ValueError):
                    self.verify()

    def test_decision_requires_current_authority(self):
        for patch in ({"authority_available": False}, {"restore_quarantined": True},
                      {"retired_keys": list(self.keys)}):
            with self.subTest(state=patch):
                self.context = {**self.case["context"], **patch}
                with self.assertRaises(ValueError):
                    self.verify()

    def test_issuer_and_purpose_come_from_trusted_key_registration(self):
        for field, value in (("issuer", "different"), ("purposes", ["bootstrap"])):
            with self.subTest(field=field):
                self.keys = copy.deepcopy(self.vectors["keys"])
                for key in self.keys.values():
                    key[field] = value
                with self.assertRaises(ValueError):
                    self.verify()

    def test_time_uncertainty_boundaries(self):
        for now, accepted in ((981, False), (982, True), (1027, True), (1028, False)):
            with self.subTest(now=now):
                self.context["now"] = now
                if accepted:
                    self.assertEqual(self.verify()["exp"], 1030)
                else:
                    with self.assertRaises(ValueError):
                        self.verify()

    def test_ancestry_cannot_be_omitted_or_reordered(self):
        for tokens in ([], self.case["tokens"][1:], list(reversed(self.case["tokens"]))):
            with self.subTest(length=len(tokens), reversed=tokens == list(reversed(self.case["tokens"]))):
                self.tokens = copy.deepcopy(tokens)
                with self.assertRaises(ValueError):
                    self.verify()

    def test_every_chain_member_needs_its_signature(self):
        for index in range(len(self.case["tokens"])):
            for missing in (False, True):
                with self.subTest(index=index, missing=missing):
                    self.tokens = copy.deepcopy(self.case["tokens"])
                    if missing:
                        del self.tokens[index]["signature"]
                    else:
                        self.tokens[index]["signature"] = ""
                    with self.assertRaises(ValueError):
                        self.verify()

    def test_parent_digest_is_the_complete_signed_assertion(self):
        self.assertEqual(token_digest(self.tokens[0]),
                         "sha256:9c55ee330ae7a4c1ed700a7e8e800bd04c593fc58368f10b81dba8b8bdefd11a")

    def test_request_binding_uses_the_leaf_not_the_parent_digest(self):
        self.verify()
        leaf_digest = token_digest(self.tokens[-1])
        self.assertEqual(leaf_digest,
                         "sha256:8de8dfda4af31660de102b9ce84390ef6ea670d38fdcdd7e6cd82a2015cbddd9")
        self.assertNotEqual(leaf_digest, token_digest(self.tokens[0]))

    def test_noncanonical_base64url_refuses_at_each_hop(self):
        for index in range(len(self.case["tokens"])):
            for field in ("protected", "payload", "signature"):
                for suffix in ("=", "+", "\n"):
                    with self.subTest(index=index, field=field, suffix=repr(suffix)):
                        self.tokens = copy.deepcopy(self.case["tokens"])
                        self.tokens[index][field] += suffix
                        with self.assertRaises(ValueError):
                            self.verify()

    def test_signature_encoding_alias_refuses(self):
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        signature = self.tokens[0]["signature"]
        alias = signature[:-1] + alphabet[alphabet.index(signature[-1]) + 1]
        # The bytes agree, but unused padding bits make the spelling noncanonical.
        self.assertEqual(base64.urlsafe_b64decode(signature + "=="),
                         base64.urlsafe_b64decode(alias + "=="))
        self.tokens[0]["signature"] = alias
        with self.assertRaises(ValueError):
            self.verify()

    def test_ambiguous_or_noncanonical_json_refuses_before_crypto(self):
        for field in ("protected", "payload"):
            encoded = self.case["tokens"][0][field]
            raw = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
            member = b'"alg":"Ed25519",' if field == "protected" else b'"tenant":"alpha",'
            cases = {
                "whitespace": b" " + raw,
                "duplicate-member": b"{" + member + raw[1:],
                "bom": b"\xef\xbb\xbf" + raw,
                "invalid-utf8": b'{"value":"\xff"}',
                "non-object": b"[]",
                "oversize": b" " * 65537,
            }
            for name, altered in cases.items():
                with self.subTest(field=field, case=name):
                    self.tokens = copy.deepcopy(self.case["tokens"])
                    self.tokens[0][field] = base64.urlsafe_b64encode(altered).decode().rstrip("=")
                    with patch("candidate_contract.subprocess.run",
                               side_effect=AssertionError("malformed JSON reached crypto")):
                        with self.assertRaises(ValueError):
                            self.verify()

    def test_signature_byte_length_refuses_at_each_hop(self):
        for index in range(len(self.case["tokens"])):
            for size in (63, 65):
                with self.subTest(index=index, size=size):
                    self.tokens = copy.deepcopy(self.case["tokens"])
                    self.tokens[index]["signature"] = base64.urlsafe_b64encode(
                        bytes(size)
                    ).decode().rstrip("=")
                    with self.assertRaises(ValueError):
                        self.verify()


if __name__ == "__main__":
    unittest.main()
