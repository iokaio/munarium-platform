#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline candidate fixture oracle, not a deployable canonicalization library."""
import hashlib
import json
from pathlib import Path
import unittest

VECTORS = Path(__file__).resolve().parents[1] / "docs/decisions/decision-json-v1-vectors.json"
DOMAIN = b"munarium:decision-request:v1\0"


def reject(_):
    raise ValueError("unsupported number")


def integer(token):
    value = int(token)
    if token == "-0" or abs(value) > 9007199254740991:
        raise ValueError("integer outside profile")
    return value


def members(pairs):
    result = {}
    for key, value in pairs:
        if not key.isascii() or key in result:
            raise ValueError("non-ASCII or duplicate member")
        result[key] = value
    return result


def canonical(raw):
    if len(raw) > 65536 or raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("size or BOM")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=members,
                       parse_int=integer, parse_float=reject, parse_constant=reject)
    if not isinstance(value, dict):
        raise ValueError("object required")

    def check(item, depth=0):
        if isinstance(item, (dict, list)):
            depth += 1
            if depth > 16:
                raise ValueError("container depth")
            for child in item.values() if isinstance(item, dict) else item:
                check(child, depth)
        elif isinstance(item, str):
            item.encode("utf-8", errors="strict")

    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


class CandidateVectors(unittest.TestCase):
    def test_fixed_vectors(self):
        vectors = json.loads(VECTORS.read_text(encoding="utf-8"))
        self.assertEqual(vectors["profile"], "decision-json-v1")
        for vector in vectors["cases"]:
            with self.subTest(case=vector["id"]):
                raw = vector["input"].encode("utf-8")
                if vector["result"] == "reject":
                    with self.assertRaises((ValueError, UnicodeError)):
                        canonical(raw)
                else:
                    output = canonical(raw)
                    self.assertEqual(output, vector["canonical"].encode("utf-8"))
                    self.assertEqual("sha256:" + hashlib.sha256(DOMAIN + output).hexdigest(),
                                     vector["digest"])

    def test_encoding_and_resource_boundaries(self):
        for raw in (b'{"a":"\xff"}', b'\xef\xbb\xbf{}',
                    b'{"a":"' + b'x' * 65529 + b'"}',
                    b'{"a":' + b'[' * 16 + b'0' + b']' * 16 + b'}'):
            with self.subTest(size=len(raw)):
                with self.assertRaises((ValueError, UnicodeError)):
                    canonical(raw)
        self.assertEqual(len(canonical(b'{"a":"' + b'x' * 65528 + b'"}')), 65536)
        canonical(b'{"a":' + b'[' * 15 + b'0' + b']' * 15 + b'}')


if __name__ == "__main__":
    unittest.main()
