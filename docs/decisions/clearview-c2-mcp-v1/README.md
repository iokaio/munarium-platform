# ClearView C2 and MCP allowance candidate v1

This candidate captures the 21 November refinements to [C2](../0022-build-job-failure-codes.md)
and [A2, A8 and A9](../0026-mcp-generation-token-allowances.md). Acceptance of the
decision records and review of these exact contract bytes are separate. The candidate
has no runtime authority, production policy or qualification status.

The [schema](schema.json) contains named definitions for the version 1 trusted
generation configuration and for the failure-member projection of a Server build
job. Validate the projection by selecting only the listed members from the DTO.
The [profile](profile.json) records all eight current producer failure codes and
their display messages, the REST and gRPC extraction-deferred classification, and
the reservation, settlement and heartbeat rules. Consumers preserve the optional
code as a string so a future additive code remains readable.

The [vectors](vectors.json) cover configuration shape, complete index overrides,
optional members, historical and classified failures, disagreement across live
replicas, estimate rounding, request and daily refusals, shared payer rules and
settlement of above-estimate usage. The offline checks validate only the selected
shape and reference cases. The corresponding Server tests exercise transport,
storage, live policy disagreement and provider accounting.

From the hub root:

    python scripts/generate_clearview_candidate.py --check
    python -m unittest discover -s scripts -p "test_clearview_candidate.py"
    python scripts/check_clearview_jsonschema.py

After committing the candidate, reproduce an export in an empty rehearsal directory:

    python scripts/vendor_clearview.py --destination <new-directory>

The [bundle lock](bundle-lock.json) pins the four source artifacts. The export adds
the exact committed revision. The exporter refuses modified source bytes and
conflicting destination content. This versioned namespace leaves all earlier hub
bundles and the Matrix-owned consumer export intact. Adoption in Server uses a
separate decision on the exact bundle digest.
