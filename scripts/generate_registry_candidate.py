#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Create a NEW review candidate; never replace an existing fixture baseline."""
import base64
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs/decisions/registry-v2"
IDENTIFIER = dict(type="string", minLength=1, maxLength=128,
                  pattern="^[a-zA-Z0-9][a-zA-Z0-9:._/-]*$")
DIGEST = dict(type="string", pattern="^sha256:[0-9a-f]{64}$", minLength=71, maxLength=71)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def digest(domain, raw):
    return "sha256:" + hashlib.sha256(domain.encode() + b"\0" + raw).hexdigest()


def array(items, maximum=32, minimum=0, unique=False):
    return dict(type="array", items=items, maxItems=maximum, minItems=minimum, uniqueItems=unique)


def closed(properties):
    return dict(type="object", properties=properties, required=list(properties), additionalProperties=False)


def b64(raw):
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def capability_definition():
    """Shape assertions; graph/node and cross-field limits are profile semantics."""
    ref = {"$ref": "#/$defs/node"}
    variants = []
    for kind, props in [
        ("boolean", {}),
        ("integer", dict(minimum=dict(type="integer", minimum=-9007199254740991, maximum=9007199254740991),
                         maximum=dict(type="integer", minimum=-9007199254740991, maximum=9007199254740991))),
        ("string", dict(minLength=dict(type="integer", minimum=0, maximum=4096),
                        maxLength=dict(type="integer", minimum=0, maximum=4096))),
        ("array", dict(items=ref, minItems=dict(type="integer", minimum=0, maximum=256),
                       maxItems=dict(type="integer", minimum=0, maximum=256))),
        ("object", dict(properties=dict(type="object", maxProperties=32, propertyNames=IDENTIFIER,
                                        additionalProperties=ref),
                        required=array(IDENTIFIER, unique=True),
                        additionalProperties=dict(type="boolean", const=False))),
    ]:
        variants.append(closed(dict(type=dict(type="string", const=kind), **props)))
    roots = copy.deepcopy(variants)
    for root in roots:
        root["properties"]["$schema"] = dict(type="string", const="https://json-schema.org/draft/2020-12/schema")
        root["required"].append("$schema")
    return {"$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": {"node": {"anyOf": variants}}, "anyOf": roots}


def main():
    # Generation is an explicit operation. Existing data never changes on rerun.
    if (DEST / "bundle-lock.json").exists():
        raise SystemExit("candidate already exists; a new candidate needs a new reviewed destination")
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    old = json.loads((ROOT / "docs/decisions/candidates/foundation.schema.json").read_text())
    manifest = copy.deepcopy(old["$defs"]["manifest"])
    props = manifest["properties"]
    props["schema_version"]["const"] = 2
    props.update(profile=dict(type="string", const="registry-manifest-v2"),
                 tenant=IDENTIFIER, publisher_id=IDENTIFIER, owner_id=IDENTIFIER,
                 operation_id=IDENTIFIER,
                 data_classifications=array(IDENTIFIER, minimum=1, unique=True),
                 required_obligations=array(dict(type="string", enum=["distinct-approval"]), unique=True))
    manifest["required"] = list(props)
    operation = closed({name: IDENTIFIER for name in
                        ("target_id", "environment", "operation_id", "credential_audience", "capability_id")})
    operation["properties"].update(parameter_schema_digest=DIGEST, result_schema_digest=DIGEST)
    operation["required"] = list(operation["properties"])
    owner = closed(dict(id=IDENTIFIER, kind=dict(type="string", enum=["human", "organization"])))
    publisher = closed(dict(id=IDENTIFIER, kid=IDENTIFIER,
                            public_key=dict(type="string", minLength=43, maxLength=43),
                            enabled=dict(type="boolean"),
                            owner_ids=array(IDENTIFIER, minimum=1, unique=True),
                            operations=array(operation, minimum=1, unique=True)))
    schema_ref = closed(dict(digest=DIGEST, canonical=dict(type="string", minLength=1, maxLength=65536)))
    tenant = closed(dict(id=IDENTIFIER, owners=array(owner, minimum=1),
                         classifications=array(IDENTIFIER, minimum=1, unique=True),
                         operations=array(operation, minimum=1, unique=True),
                         publishers=array(publisher, minimum=1), schemas=array(schema_ref, minimum=1)))
    bundle_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": dict(manifest=manifest, modifier=old["$defs"]["modifier"],
                      required_input=old["$defs"]["required_input"],
                      header=closed(dict(alg=dict(type="string", const="Ed25519"),
                                         typ=dict(type="string", const="munarium-manifest+jws"),
                                         kid=IDENTIFIER)),
                      trust=closed(dict(schema_version=dict(type="integer", const=2),
                                        revision=dict(type="integer", minimum=1, maximum=9007199254740991),
                                        tenants=array(tenant, minimum=1)))),
    }
    key = Ed25519PrivateKey.generate()  # Memory only; no private key serialization.
    public = b64(key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw))
    parameter = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
                 "properties": {"key": {"type": "string", "minLength": 1, "maxLength": 64}},
                 "required": ["key"], "additionalProperties": False}
    result = copy.deepcopy(parameter)
    result["properties"] = {"value": {"type": "string", "minLength": 0, "maxLength": 256}}
    result["required"] = ["value"]
    schemas = [dict(digest=digest("munarium:capability-schema:v1", canonical(s)),
                    canonical=canonical(s).decode()) for s in (parameter, result)]
    operation_value = dict(target_id="fixture-target", environment="test", operation_id="get-item",
                           credential_audience="none", capability_id="read-item",
                           parameter_schema_digest=schemas[0]["digest"], result_schema_digest=schemas[1]["digest"])
    tenants = []
    for tenant_id in ("alpha", "beta"):
        tenants.append(dict(id=tenant_id, owners=[dict(id="owner", kind="human")],
                            classifications=["public"], operations=[operation_value], schemas=schemas,
                            publishers=[dict(id="publisher", kid=kid, public_key=public, enabled=True,
                                             owner_ids=["owner"], operations=[operation_value])
                                        for kid in ("key-1", "key-2")]))
    trust = dict(schema_version=2, revision=1, tenants=tenants)
    manifest_value = dict(schema_version=2, profile="registry-manifest-v2", tenant="alpha",
                          publisher_id="publisher", owner_id="owner", id="read-item", version="1",
                          **operation_value, base_consequence="C0", modifiers=[], required_inputs=[],
                          effect="observation", idempotency="none", compensation="none",
                          data_classifications=["public"], required_obligations=[])
    header = dict(alg="Ed25519", typ="munarium-manifest+jws", kid="key-1")
    cases = []

    def signed(payload, head=None, raw=None):
        payload_bytes = canonical(payload) if raw is None else raw
        signing = (b64(canonical(head or header)) + "." + b64(payload_bytes)).encode()
        return signing.decode() + "." + b64(key.sign(signing))

    def case(name, expected="accept", patch=None, head=None, raw=None, context="alpha"):
        payload = {**manifest_value, **(patch or {})}
        envelope = signed(payload, head, raw)
        item = dict(id=name, tenant=context, envelope=envelope, expected=expected)
        if expected == "accept":
            item.update(payload=canonical(payload).decode(),
                        manifest_digest=digest("munarium:manifest:v2", canonical(payload)),
                        artifact_digest=digest("munarium:manifest-artifact:v2", envelope.encode()))
        cases.append(item)
        return envelope

    valid = case("alpha")
    case("beta", patch=dict(tenant="beta"), context="beta")
    case("changed-bytes", patch=dict(effect="internal-change"))
    case("new-version", patch=dict(version="2"))
    case("resigned", head={**header, "kid": "key-2"})
    case("approval", patch=dict(required_obligations=["distinct-approval"]))
    case("wrong-tenant", "Unauthorized", context="beta")
    for name, patch in [
        ("old-profile", dict(schema_version=1)),
        ("active-flag", dict(active=True)),
        ("unknown-field", dict(extension="ignored")),
        ("unknown-obligation", dict(required_obligations=["allow"])),
        ("empty-classification", dict(data_classifications=[])),
        ("lowering-modifier", dict(base_consequence="C2", modifiers=[
            dict(field_path="amount", predicate_digest="sha256:" + "a" * 64, raise_to="C1")])),
        ("duplicate-classification", dict(data_classifications=["public", "public"])),
    ]:
        case(name, "InvalidManifest", patch)
    missing = dict(manifest_value)
    del missing["owner_id"]
    case("missing-owner", "InvalidManifest", raw=canonical(missing))
    case("noncanonical", "InvalidArtifact", raw=json.dumps(manifest_value, sort_keys=True).encode())
    case("duplicate-key", "InvalidArtifact", raw=b'{"id":"extra",' + canonical(manifest_value)[1:])
    case("bad-number", "InvalidArtifact", raw=canonical(manifest_value).replace(b'"schema_version":2', b'"schema_version":2.0'))
    for name, head in [("principal-token", {**header, "typ": "munarium-principal+jws"}),
                       ("wrong-algorithm", {**header, "alg": "EdDSA"}),
                       ("remote-key", {**header, "jku": "https://invalid.example/key"})]:
        case(name, "InvalidArtifact", head=head)
    case("unknown-key", "UntrustedPublisher", head={**header, "kid": "missing"})
    for name, patch in [("unknown-owner", dict(owner_id="missing")),
                        ("unknown-publisher", dict(publisher_id="missing"))]:
        case(name, "UntrustedPublisher", patch)
    for name, patch in [("unknown-classification", dict(data_classifications=["missing"])),
                        ("wrong-operation", dict(operation_id="delete-item")),
                        ("wrong-audience", dict(credential_audience="admin")),
                        ("missing-schema", dict(parameter_schema_digest="sha256:" + "f" * 64))]:
        case(name, "MissingReference", patch)
    parts = valid.split(".")
    corrupt = bytearray(base64.urlsafe_b64decode(parts[2] + "=="))
    corrupt[0] ^= 1
    for name, envelope in [
        ("unsigned", ".".join(parts[:2]) + "."),
        ("corrupt-signature", ".".join(parts[:2]) + "." + b64(corrupt)),
        ("padded-base64", parts[0] + "=." + ".".join(parts[1:])),
        ("trailing-newline", valid + "\n"),
    ]:
        cases.append(dict(id=name, tenant="alpha", envelope=envelope, expected="InvalidArtifact"))
    DEST.mkdir(parents=True, exist_ok=True)
    for name, value in [("registry.schema.json", bundle_schema),
                        ("capability.schema.json", capability_definition()), ("trust.json", trust),
                        ("signed-vectors.json", dict(status="candidate", cases=cases))]:
        (DEST / name).write_bytes(json.dumps(value, indent=2, ensure_ascii=False).encode() + b"\n")
    files = {name: hashlib.sha256((DEST / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
             for name in ("README.md", "registry.schema.json", "capability.schema.json", "signed-vectors.json", "trust.json")}
    aggregate = "".join(name + "\0" + h + "\n" for name, h in sorted(files.items()))
    lock = dict(status="candidate-not-released", source_base="c46f86400732223a6a7c23f5d186250ab4a144eb",
                files=files, bundle_sha256=hashlib.sha256(aggregate.encode()).hexdigest())
    (DEST / "bundle-lock.json").write_bytes(json.dumps(lock, indent=2).encode() + b"\n")
    print(f"Created {len(cases)} signed-artifact cases; bundle {lock['bundle_sha256']}")


if __name__ == "__main__":
    main()
