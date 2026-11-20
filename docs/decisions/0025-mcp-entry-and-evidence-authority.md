# ADR 0025: MCP entry scope and the read-only evidence capability

**Accepted (20 November 2026).** This records the shared semantics of Server v1.5
"ClearView" decisions A1 and A4. A4 applies A1 at each evidence-reader call, so the
two are recorded together. The maintainer accepted it as written; see
[Disposition](#disposition-20-november-2026). Acceptance does not publish a contract
version, advance a catalog state or set a release label. The accountable owner is the
founder under [governance](../../GOVERNANCE.md).

Normative source: the Server design at
`ef32276d593c190b5a25234a85604564769d0e60` (Server `feat/clearview`), sections
[A1](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#a1),
[5.1](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#51-query-tools),
[A4](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#a4)
and the acceptance cases A1-T1 and A4-T1 in
[section 8](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#8-qualification-and-rollback).
The Server design records A1 and A4 as maintainer design decisions; this hub record
records them as shared semantics, and its disposition records their acceptance.

## Context

Server v1.5 adds an opt-in `POST /mcp` endpoint for agents acting for an individual
user. Capability tokens are issued by deployment brokers and verified by every Server
replica, and the scope vocabulary is read by the four Server SDKs and the console.
Adding an endpoint must not widen any existing token, and the two sealed-evidence
reader tools need a grant that cannot seal or write.

## Decision

### A1: entry and tool authority

1. The issuer must explicitly grant `mcp` on a tenant-bound capability JWT before the
   caller can enter the endpoint. `mcp` admits authenticated protocol discovery and a
   filtered tool listing only.
2. Each tool invocation also requires its normal data-plane scope, including `query`
   for the collection and runbook listing tools, plus the operation's tenant,
   clearance, compartment, resource and runbook checks.

   | Scopes on a valid capability JWT | Discovery and `tools/list` | MCP query tool | Native v1.4 query |
   |---|---|---|---|
   | `query` only | Entry refused, 403 `scope-missing` | Refused before dispatch | Allowed within existing authority |
   | `mcp` only | Succeeds; list is empty | Refused before dispatch | Refused |
   | `mcp` and `query` | Succeeds; enabled query tools visible | Allowed subject to operation checks | Same as `query` alone |

3. Enabling the listener grants no new authority to existing application tokens.
   Additional scopes on the same token keep their v1.4 meaning on native routes.
4. Check an asserted uid against the verified subject when present. Refuse static
   role credentials even where they could call the native operation. Return 401 with a
   Bearer challenge for invalid or expired credentials and 403 for insufficient entry
   scope, using the existing authentication slugs.
5. `mcp` is a transport-entry scope, not a confinement. A deployment needing MCP-only
   access or a cross-transport spend limit enforces it at every applicable entry point.
   `mcp` tokens are issued, and the route enabled, only after all intended replicas
   understand the profile; v1.4 issuance, default lifetime and verification keep working
   across a rolling upgrade.

### A4: read-only evidence capability

1. Both evidence readers (`get_evidence`, `read_evidence_rows`) work with an additive
   read-only evidence capability before the MCP endpoint ships.
2. Over MCP each call requires `mcp` and the read-only grant. On the native manifest and
   row handlers, the read-only grant suffices for an authorized read.
3. Every resolution enforces tenant, clearance, compartments and retention, and records
   the caller and outcome without copying evidence into the access audit.
4. The read-only grant cannot seal, upload or commit evidence. Existing native
   `evidence` tokens retain their v1.4 read and sealing permissions.
5. A token with `mcp` and `query` but without the evidence grant can neither list nor
   invoke either reader.

## Open choices

| Choice | State in the Server design | Closing evidence named by Server |
|---|---|---|
| Wire spelling of the read-only evidence scope | Explicitly left to "the shared decision process"; no spelling is proposed | Additive contract with issuance, wire shapes and rejection vectors, re-vendored, with native and MCP conformance |
| Representation | Not specified. The classes for review are a new, distinct scope value, or an attenuated form of the existing `evidence` grant. Either must be additive, unable to seal and not implied by `query` | Same |
| Whether `mcp` plus a v1.4 `evidence` token admits the MCP readers | Not stated; A4-T1 exercises only the read-only grant over MCP and replays `evidence` natively | Same |
| Issuance path for the new grant | "Issuance" is named as part of the export; the broker and token routes are not otherwise specified | Same |

As drafted, this record did not select a spelling or representation. The
[disposition](#disposition-20-november-2026) records the resolution.

## Disposition (20 November 2026)

**Accepted by the maintainer on 20 November 2026, as written**, reviewing hub
revision `dc3aa258b0bde8b82a1ad676a4727204264997db` (`dc3aa25`, this record as
drafted). The Server implementation ledger records the acceptance as
[maintainer decision 5](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/design/implementation-ledger.md#maintainer-decisions-20-november-2026)
at Server `89e1bc2019c80d697d2d8adc9237a9ce577cf3d7`. This disposition changes the
record's state only. It publishes no contract version, composition manifest or
release label, advances no catalog state or invariant evidence field, and activates
nothing.

The open choices are resolved as the Server implemented them on `feat/clearview`
(Server `0483db1c4d605c3e22f8c291ddd2b273b70378e5` and
`43d38c0ec7c36e9b68509467429671d6d558be44`, ledger rows A1 and A4, and the Server
[MCP operator guide](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/ops/mcp.md)):

| Choice | Resolution |
|---|---|
| Wire spelling of the read-only evidence scope | `evidence_read`. |
| Representation | A new, distinct scope value, not an attenuated form of `evidence`. It opens `GET /v1/evidence/{id}` and `GET /v1/evidence/{id}/rows` natively and, with `mcp`, the two MCP readers. It cannot seal, upload or commit, and `query` does not imply it. |
| Whether `mcp` plus a v1.4 `evidence` token admits the MCP readers | No. Only `evidence_read` opens the MCP readers; a v1.4 `evidence` token keeps its native read and sealing permissions. |
| Issuance path for the new grant | The existing token issuance route, `POST /v1/access-tokens`, or the typed gRPC issuer, like any other scope. Static role credentials never carry `mcp`. |

Maintainer decisions of 20 November 2026 that bear on this record:

- **Decision 6.** The MCP wire additions, including the `mcp` and `evidence_read`
  scope values, are accepted as release ready. The hub contract export with its
  rejection vectors, named in the version policy, remains a separate step; this
  disposition does not perform it.
- **Decision 1.** Binary rollback across v1.5 migrations is by backup restore. The
  rolling-upgrade rule in A1 item 5 is unchanged.

## Alternatives

- **Admit MCP with existing data-plane scopes.** Rejected: enabling the listener must
  grant nothing to existing tokens.
- **Treat `mcp` as sufficient for tool execution.** Rejected: each tool also needs its
  operation scope.
- **Serve the readers under the existing `evidence` scope only.** Not adopted: that
  scope can seal, and A4 requires a read-only capability.
- **Accept static role credentials over MCP.** Rejected.

## Evidence

No implementation evidence at drafting. The implementation since is cited in the
[disposition](#disposition-20-november-2026). At drafting, the [implementation ledger](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/implementation-ledger.md)
records A1 and A4 as planned. The A5 release gate treats an A4 authority failure as
blocking.

## Owners and affected consumers

| Owner | Responsibility |
|---|---|
| Founder | Accountable design owner and acceptance authority |
| Server API and access maintainers | Scope verification, native evidence handlers and token issuance |
| Server MCP maintainers | Entry checks, filtered listing and direct-call denial |
| Hub contract owners | The exported scope contract and rejection vectors |

Affected consumers: deployment token brokers, the four Server SDK families' token
and scope handling, the console's token views, evidence sealing services (whose v1.4
`evidence` tokens must keep working) and MCP clients.

## Version policy

Additive: the `mcp` scope and the read-only evidence capability, with no change
to existing scope meanings, issuance defaults or verification (MCP-RULE-1). The exact spellings and issuance shapes are
exported through the owning contract process and re-vendored before any consumer or
broker issues them. This record adds no hub schema or vector.

## Consequences

- An agent's MCP authority is the intersection of transport entry and its ordinary
  data-plane grants; an `mcp`-only token completes discovery but lists no tool.
- Evidence becomes readable to agents without granting the sealing authority of
  `evidence`.
- MCP qualification cannot complete until the scope spelling is exported and both
  native and MCP conformance pass.
