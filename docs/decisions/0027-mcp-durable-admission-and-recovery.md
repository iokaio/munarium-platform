# ADR 0027: MCP durable audit admission and interrupted-call recovery

**Proposed, 20 November 2026; open choices listed.** This records the shared
semantics of Server v1.5 "ClearView" decision A6 and the proposed additive
interrupted-call recovery contract that the Server design couples to it (open item
"MCP interrupted calls (A5/A6)"). It does not accept a contract, advance a catalog
state or publish a version. The accountable owner is the founder under
[governance](../../GOVERNANCE.md).

Normative source: the Server design at
`ef32276d593c190b5a25234a85604564769d0e60` (Server `feat/clearview`), sections
[A6](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#a6),
[5.2](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#52-tool-results),
[5.3](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#53-recovering-an-interrupted-call)
and acceptance cases A6-T1 to A6-T3 and
[A5-T5](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#a5-t5).
The Server design records A6 as a maintainer design decision and the recovery
contract as a proposal; this hub record proposes both as shared semantics and does
not record their acceptance.

## Context

The v1.4 interaction writer enqueues best-effort records, counts drops and failed
inserts, and the memory store discards them. That is not adequate attribution for
agent-initiated tool calls. Separately, an MCP JSON-RPC request ID correlates only a
single exchange and may change on reconnection, so a client that loses a reply has no
way to learn what happened without risking a second execution or charge. Report
readers, MCP clients and the planned shared contract need one meaning for admission,
duplicates and recovery.

## Decision (proposed)

### A6: durable admission before execution

1. Before executing any authorized `tools/call`, Server must receive confirmation that
   the shared durable audit store has committed the admission record. Verify the
   credential, scopes, tool and bounded arguments first.
2. The record holds a server-assigned invocation ID, `plane = "mcp"`, the fixed tool
   name, tenant, uid, token ID, request ID and time. It excludes credentials, argument
   bodies, retrieved text and evidence rows.
3. If the store is unavailable or the commit acknowledgement is missing by the
   deadline, a content-free typed refusal ends the call. No handler runs, reads
   application data, mutates state, reserves provider spend or contacts any provider.
   A memory-only deployment without a durable audit store refuses tool execution.
4. The gate applies to all eleven tools, including both listing tools. Authenticated
   protocol discovery, the legacy handshake and the scope-filtered `tools/list` are
   protocol operations and execute no tool.
5. Each admitted call, including duplicates and recovery reads, gets a fresh invocation
   ID. Physical attempts, session changes and spend are attributed to the original
   execution's ID. Admission alone leaves execution unknown after a crash; a missing
   outcome never triggers replay.
6. Reports add `mcp` to the plane filter, count each admitted invocation once and
   report known outcomes separately. Native REST and gRPC capture is unchanged.

### Recovery of an interrupted call (proposed additive MCP contract)

1. Before sending `open_session`, `ask_session`, `close_session`, `ask_collections` or
   `search_collection`, the client chooses and retains an operation key. Each of these
   tools accepts an execution request (key plus arguments) or a recovery request (key
   only). Recovery reads a bounded receipt and never starts the operation. The other
   six tools repeat their bounded reads.
2. The key binds the verified tenant, uid and tool. For new work, Server atomically
   claims the key, stores the canonical argument digest and commits the A6 admission;
   only the confirmed claimant dispatches. Distinct keys are distinct calls even with
   identical arguments.
3. Every duplicate or recovery request needs its own confirmed A6 admission and a
   recheck of current credential, original resource authority and retention before
   revealing receipt existence, a conflict, an outcome or a reference. A matching
   authorized duplicate receives the receipt; changed arguments receive a typed
   conflict. An absent and an inaccessible receipt yield the same response.
4. Receipts report pending, completed, refused or unknown, are bounded and exclude
   request bodies, transcripts, answers and evidence. After the execution deadline,
   effects lacking a durable outcome are unknown. Provider usage is reported separately
   from reserved capacity.
5. The key carries an immutable UTC expiry and a caller-generated random identifier.
   Server enforces the maximum validity window and the work deadline against the shared
   store clock when claiming, after any lock wait, and rechecks expiry before dispatch.
   Claims are retained through expiry across restarts; a late request with a pruned key
   is refused. Clients never extend expiry or mint a fresh key automatically after
   interruption. Expiry leaves unresolved reservations and audit retention intact.
6. Recovery stays available to authorized callers after new execution, generation or
   inference is disabled or a budget is exhausted, and incurs no model work or new
   reservation. Native v1.4 calls keep their signatures and behavior.

## Open choices

The Server design names what the contract must pin but supplies no values. Its
closing evidence: "record and export the caller-known recovery key, its scope and
validity window, receipt retention and bounded recovery response", and prove
attribution across concurrent identical calls and an interrupted enrolled search.

| Choice | Constraint already stated | Not yet specified |
|---|---|---|
| Key format | Immutable UTC expiry plus a caller-generated random identifier | Encoding (a single opaque token or separate fields), identifier length and character set, maximum size |
| Key scope | Verified tenant, uid and tool; recovery must work after token renewal (A5-T5) | Whether any further binding is required |
| Maximum validity window | Enforced against the shared store clock | The value |
| Receipt retention | At least through key expiry, across restarts | Duration beyond expiry; relation to audit retention |
| Result discriminator and receipt shape | Namespaced result `_meta` field distinguishing native results, projections and receipts; present in both structured and text forms | Field names and status encoding |
| Scoped refusal shapes | Typed conflict, pruned-key refusal, absent-or-inaccessible equivalence | Problem types and their registry entries |
| Admission store and linkage | Shared durable store, additive storage changes | Schema of admission and outcome linkage |

This record does not choose these values.

## Alternatives

- **Best-effort capture as for native traffic.** Rejected for MCP: a confirmed durable
  commit is required even when the interaction writer is healthy.
- **Use the JSON-RPC request ID for recovery.** Rejected: it correlates one exchange.
- **Replay on reconnection or missing outcome.** Rejected: no automatic replay.
- **Recovery without its own admission.** Rejected: every lookup is admitted.

## Evidence

No implementation evidence. The [implementation ledger](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/implementation-ledger.md)
records A6 and A5-T5 as planned, both waiting for the exported contract.

## Owners and affected consumers

| Owner | Responsibility |
|---|---|
| Founder | Accountable design owner and acceptance authority |
| Server MCP maintainers | Admission gate, key claims, receipts and recovery handler |
| Server audit and reporting maintainers | Durable store, plane filter and report readers |
| Hub contract owners | Exported recovery contract and refusal vectors |

Affected consumers: MCP clients on both qualified protocol revisions, the four
Server SDK families' report decoders and older binaries reading mixed rows, the
console's activity views and operators relying on per-user audit.

## Version policy

Additive: MCP is off by default; native routes and REST/gRPC capture keep v1.4
behavior; storage changes are additive migrations. The recovery argument forms,
receipt and refusal shapes are exported through the owning contract process and
re-vendored before reliance, and qualified on both MCP revisions. This record adds no
hub schema or vector.

## Consequences

- An audit outage stops MCP tool execution rather than allowing unrecorded agent
  activity; this is a deliberate availability cost.
- A client that loses a reply can learn the outcome without a second execution or
  charge, within the key's validity window.
- An interrupted call can remain "unknown" permanently; reports must not present it
  as completed or failed.
