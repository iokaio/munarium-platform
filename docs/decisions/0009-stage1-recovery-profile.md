# 0009: Stage 1 source derivation and recovery profile

Implementation directed, 6 October 2026; human acceptance pending. This narrows
[0008](0008-stage1-service-boundary.md) without changing foundation golden vectors.

The operator artifact's `decisions` map binds targets to complete immutable Gate
snapshots. Gate resolves the signed manifest independently through Registry and
checks current authority again before recording. The first source derivation is
`test-result` version `1`: canonical JSON containing an `artifact_digest` matching
the request parameter and a boolean literal key `tests.passed`. Gate derives this
value from exact source bytes, verifies their content digest and required lineage,
and refuses unsupported derivations. Operator admission is the provenance root
for these snapshots; this is not an arbitrary evidence ingestion API.

Gate persists immutable decision, request and exact sequenced event bytes to its
SQLite journal before recording them to Server. One process owns each journal;
pending recording blocks new evaluations until exact resubmission completes it.
Lookup never submits or repairs writes. Recovery requires current authorization
and the original verified origin, actor and origin kind, allowing fresh assertions
without changing the original request digest. Archived decisions in Server survive
a restored local journal. Old unattributed archives remain available to offline
replay tooling but cannot be retrieved through authenticated live recovery.

Harness transports send once, use HTTPS with certificate validation, refuse
redirects, bound responses, and report ambiguous submissions as unresolved. They
retain the canonical original proposal for read-only lookup. These client checks
are conveniences; receiving services independently enforce every boundary.

Deferred alternatives: arbitrary derivation programs, active manifest promotion,
execution grants and distributed Gate writers. This profile adds no such authority.
Future extensions require a reviewed versioned profile and new acceptance evidence.
