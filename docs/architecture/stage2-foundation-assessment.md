# Stage 2 foundation assessment: S7, S9 and action records

**7 October 2026; read-only assessment, not qualification.** Inspected Server
`7cc0c97fe124d446064bb8cf0dfcb6d868d04987`, clean `main`, against
[ADR 0002](../decisions/0002-action-execution-protocol.md) and REF-02–19.
The [Stage 1 acceptance packet](stage1-acceptance.md) pins the other inputs.
No foundation source was edited and no live test resources were created for this
assessment. The checks below are additional analysis, not independent human review.

## S7: preserve direct authentication; qualify the effect topology

Server already has direct REST/gRPC client-certificate verification and enrolled
peer admission in
[platform_tls.rs](https://github.com/iokaio/munarium/blob/7cc0c97fe124d446064bb8cf0dfcb6d868d04987/server/src/munarium-server/src/platform_tls.rs#L30).
[Principal admission](https://github.com/iokaio/munarium/blob/7cc0c97fe124d446064bb8cf0dfcb6d868d04987/server/src/munarium-server/src/platform_identity.rs#L15)
binds the actual presenter, recipient, tenant and installed identity policy.
Record admission retains the checkpoint lock through recording. Forwarding
headers do not establish identity. The platform profile rejects multiple replicas.

The existing
[live authority tests](https://github.com/iokaio/munarium/blob/7cc0c97fe124d446064bb8cf0dfcb6d868d04987/clients/python/tests/test_platform_authority_live.py#L451)
cover both stores/transports, certificate refusal, spoofed identity, concurrent
retry and bootstrap retirement. These are authentication tests; they do not prove
that an agent cannot reach a target, mount a secret or access a service database.

**S7-01 / deployment and Harness:** select and test the complete Stage 2 graph:
Council, broker, connector, target, datastore roles, permitted egress and denied
agent routes/mounts. Retain one replica and direct TLS unless a separately reviewed
profile requires more. REF-07 must test from the actual agent boundary. No rewrite
of Server's TLS layer is justified by this assessment.

## S9: reuse semantics and failure fixtures, not an incompatible adapter

[guarded-v1 command recovery](https://github.com/iokaio/munarium/blob/7cc0c97fe124d446064bb8cf0dfcb6d868d04987/server/src/munarium-server/src/command_recovery.rs#L40)
persists an unresolved claim before a keyed command. Tenant/key advisory locks,
immutable bindings, completed replay and refusal of unresolved repetition are
useful existing behavior. Underlying command mutation and receipt completion are
separate; the
[guide](https://github.com/iokaio/munarium/blob/7cc0c97fe124d446064bb8cf0dfcb6d868d04987/server/docs/ops/command-recovery.md#L42)
states the limit. Successful command claims can expire under idempotency TTL.

[Process-death tests](https://github.com/iokaio/munarium/blob/7cc0c97fe124d446064bb8cf0dfcb6d868d04987/server/src/munarium-server/src/command_recovery_tests.rs#L34)
exercise pre-command, post-effect/pre-receipt and completed-receipt barriers with
independent SQL effect counts. These fixtures inform the Stage 2 crash oracle.

**S9-01 / Gate and Warden:** provide atomic consumption, worker acquisition,
reservations, final-send fencing and an outcome outbox under one Gate transaction
owner. Server's command adapter supplies none of those action guarantees. Do not
reuse command TTL as consumption-tombstone or unresolved-reservation expiry.
Factor owner-maintained logic only after the selected contract shows an actual
shared seam; preserve legacy command behavior and avoid a copied Server subsystem.

## S2: a confirmed blocker beyond the original S7/S9 headings

The existing
[event ledger](https://github.com/iokaio/munarium/blob/7cc0c97fe124d446064bb8cf0dfcb6d868d04987/server/src/munarium-core/src/platform.rs#L206)
already checks canonical bytes, exact digests, tenant, source epoch/sequence,
predecessor and idempotent acknowledgements. It accepts only proposal, decision
and refusal. Its
[conflict rule](https://github.com/iokaio/munarium/blob/7cc0c97fe124d446064bb8cf0dfcb6d868d04987/server/src/munarium-core/src/platform.rs#L245)
also rejects different non-proposal payloads for the same operation. Widening only
the event-kind enum would still reject an action's lifecycle progression.

**S2-01 / Server and hub:** prepare the common envelope and new versioned action
payload family from [ADR 0011](../decisions/0011-platform-contract-evolution.md),
with a compatible ledger/validator path for approval, claim, grant, consumption,
predispatch, send-intent, outcome and reconciliation references. Preserve all
Stage 1 candidate bytes and conflict semantics. Test exact retry, changed-event
conflict, legitimate progression, missing/wrong acknowledgements, gaps,
reconnect persistence and cross-tenant refusal on memory and PostgreSQL.
The [HUB-03 proposal](../decisions/0010-stage2-authority-durability.md) specifies
the action bindings; other families must not invent action IDs. Each authoritative
producer needs durable outbox semantics. No implementation is authorized by this
audit alone.

**S2-02 / Server and Gate:** define authenticated historical outbox delivery.
Current [record admission](https://github.com/iokaio/munarium/blob/7cc0c97fe124d446064bb8cf0dfcb6d868d04987/server/src/munarium-server/src/platform_records.rs#L137)
uses the current authority epoch and append rejects an event with another source
epoch. Audit events queued before activation/restore therefore need a new recovery
path that verifies the original committed claim/source/epoch with current recorder
authority. Include committed send-intent and other required predecessor facts,
not only outcomes, so the original sequence can drain in order. Preserve event
bytes, reject invented historical facts and never reactivate execution rights.
Test pending send-intent/outcome delivery across epoch changes.

## Restore is a cross-component gate

Server's external prepared checkpoint fences inconsistent or restored authority
state and has
[crash/recovery tests](https://github.com/iokaio/munarium/blob/7cc0c97fe124d446064bb8cf0dfcb6d868d04987/server/src/munarium-server/src/platform_api_tests.rs#L100).
Restoring the checkpoint and database together to an older state remains locally
undetectable. That mechanism does not establish REF-15 for action execution.

**S9-02 / Gate, Warden, Server and target:** quarantine issuance and dispatch,
reconcile through a known cutoff, retain consumed grants and unresolved exposure,
establish a fresh external recovery epoch and obtain the target's floor
acknowledgement before reopening. Missing evidence leaves the cell quarantined.
No restored database can declare its own recovery safe.

## Checks and next bounded validation

From `server/`, Cargo/rustc 1.98.1, on 7 October:

```console
cargo test --offline --locked -p munarium-store-mem --test platform --test platform_authority
git diff --check
```

Both exited 0. The Rust run passed four tests, with none failed or ignored.
Cargo was invoked from the installed toolchain because it was absent from PATH.
Server remained clean. No PostgreSQL, process-death or live transport test was
rerun in this assessment. Some guarded-command tests return early without a
database; that is not a passed database qualification.

After accepted contracts and an owned disposable database, select the documented
PostgreSQL platform/authority tests, guarded-command process recovery/race tests
and live Python authority tests. Add the missing action-specific tests rather
than interpreting legacy successes as REF-08–19 coverage. The next packet must
record environment owner, availability, expiry and cost authority before scheduling
live qualification; no paid environment has been commissioned.
