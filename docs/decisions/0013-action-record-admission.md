# 0013: Server action-record admission and custody

**Experimental implementation directed, 7 October 2026; qualification pending.**
This adapter consumes the unchanged [Stage 2 candidate](stage2-v1/README.md) under
the [implementation direction](../stage2-implementation.md). It preserves the
existing Stage 1 path and uses Server's protected tenant store and append/head CAS.

## Admission and storage

Add action archive, append, operation/transition lookup and source-head operations to the existing
authenticated records endpoint/RPC. Both transports dispatch to the same handler.
A current recipient-bound service identity and the actual enrolled mTLS peer are
required, with separate `action-records:<tenant>` resources. Agent/human origins
cannot impersonate an action recorder. Ordinary writers cannot select the reserved
physical tenant or mutate its facts. No acknowledgement confers dispatch authority.

The independently ratified governing artifact supplies a closed
`action-records:<audience>` binding: profile version, qualified domain/tenant/
deployment/cell, producer stream registrations with current generations and
permitted kinds, read-service allowlist and bounded historical recovery permits.
Missing/unknown bindings refuse. Server holds its current authority/checkpoint
fence through the append, as for Stage 1. Source generation, authority revision,
activation and recovery epochs remain separate.

Gate archives immutable request/decision records; Council archives approval and
activation records. Archive returns an artifact digest and ledger position, never
an event acknowledgement. A request fixes intent for its operation and context
for its attempt. Reusing an artifact identity with changed bytes conflicts.
Server checks canonical bytes, schema, scope, digest and cross-record bindings;
the owning service still verifies policy/evidence, human eligibility and current
execution authority. An archive is a recorded producer assertion, not proof that
an external fact is true or a target effect occurred.

Each event must match its admitted producer/kind, stream, generation and archived
operation/attempt bindings. Distinct lifecycle facts may share an operation.
Approval references an archived Council approval; claims follow the recorded
approval; grants refer to claims; consumption refers to grants; predispatch names
consumption; send intent names the exact predispatch acknowledgement; outcome and
reconciliation retain their prior send/outcome references. Activation events bind
the archived transition and its exact participant/artifact set. Unknown or missing
prerequisites refuse rather than receiving a pending acceptance acknowledgement.

Append reads one ledger head, checks immutable event identity and per-stream
continuity, then commits with that expected head. CAS losers reread and revalidate.
Receipt time is stored with the event so exact retries return the same full
acknowledgement. Read authorization is current; lookup never submits work. Source
head is per qualified registered stream/generation. Stage 1 records and action
records use separate subjects/conflict rules within the protected store.

The first action profile records one immutable claim, grant, consumption,
predispatch, send intent and initial outcome per attempt. A changed initial
outcome is a reconciliation event referring to retained prior evidence. It does
not overwrite the original outcome. This adapter does not implement worker lease
takeover or infer permission to repeat a send from a newly recorded event.

## Historical recovery

Current recording normally requires the current registered generation. An old
generation additionally needs a separately ratified recovery permit naming the
current recorder service, original producer/stream/generation, exact event digest,
kind, original claim ID/digest and occurrence cutoff. Source registration remains
retained. The permit is an operator/governance attestation based on retained
committed producer evidence; it is not an assertion accepted from the append caller.
The first adapter does not claim autonomous verification of a remote Gate journal.

Recovery is bounded to claim-created, grant-issued, consumption-reserved,
predispatch, send-intent, outcome and reconciliation facts. Claim-created must
match the exact attested original claim digest; subsequent facts require that
claim already recorded with matching operation/attempt/request/context. Deliver
missing predecessors first. Original bytes and original source generation remain
unchanged; audit evidence separately identifies the current recovery recorder.
Incomplete proof, missing original claim, wrong source or a generation at/above
the current generation refuses. Recording these facts never creates a grant,
worker ownership or a new final-send permission.

Recovery permits must be prepared from independently retained committed receipts
before reopening a restored cell; this mechanism alone does not establish REF-15.
Real-store restart/concurrency and authenticated transport tests cover this adapter.
Independent target reconciliation and credential/dispatcher exclusion remain
Gate/Warden/Harness obligations under ADR 0010/0011.
