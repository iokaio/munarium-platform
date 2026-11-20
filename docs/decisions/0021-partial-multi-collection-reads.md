# ADR 0021: explicit partial multi-collection reads

**Accepted (20 November 2026).** This records the shared semantics of Server v1.5
"ClearView" decision C1. The maintainer accepted it as written; see
[Disposition](#disposition-20-november-2026). Acceptance does not publish a contract
version, advance a catalog state or set a release label. The accountable owner is the
founder under [governance](../../GOVERNANCE.md).

Normative source: the Server design at
`ef32276d593c190b5a25234a85604564769d0e60` (Server `feat/clearview`), sections
[R2 and C1](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#c1)
with acceptance cases
[C1-T1](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#c1-t1)
and [C1-T2](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/airk-analysis.md#c1-t2),
and the MCP session rule in
[section 5.1](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#51-query-tools).

## Context

A v1.4 multi-collection read adds a member returning `NotFound` to `skipped`, a list
of names with no reason, and fails the whole operation on any other member error,
discarding members that succeeded. Callers cannot distinguish an authorized empty
result from an unavailable member, and nothing states which claims the remaining
evidence can support. The response fields, evidence semantics and refusals are
consumed by the four Server SDKs, the REST and gRPC transports and the planned MCP
tools, so the meaning of a partial read is a shared semantic.

## Decision

1. **Omitted policy keeps v1.4 behavior**, including the `NotFound` skip and failure
   on other member errors. `skipped` and its existing meanings are preserved.
2. **Explicit `report`.** An unavailable optional collection leaves the verified,
   authorized results of the other members available.
   - Apply authorization and scope-readability checks before composing the response.
   - An authorized search that completes with zero hits has a successful empty outcome.
   - An unavailable authorized member has an incomplete outcome and a content-free reason.
   - A hidden collection contributes no outcome, name, count or diagnostic. Gaps are
     reported only within the caller's visible scope.
   - Selection by the existing routing probe is distinguished from a deep search that failed.
3. **A stricter `require` policy, if offered, must be explicit.**
4. **Evidence rule.** Document hits never prove exhaustive coverage, even when every
   collection responds. Evidence-kind and pin checks apply to each assertion. An
   independently complete count can support a claim about its own authorized scope;
   an assertion spanning an incomplete fan-out needs separate, complete evidence for
   that whole scope.
5. **Withholding (C1-T1).** Withhold each claim that depends on a missing member,
   including absence and exhaustive coverage across that scope. If the requested
   answer requires the missing evidence, refuse that answer. Separately verified
   citations and claims about a narrower, independently supported scope remain.
6. **Both turn forms.** The same semantics apply to unary and streamed turns (C1-T2).
7. **Interactions.** For MCP multi-collection answers, the proposed MCP request
   selects the strict availability policy and cannot claim a complete answer when a
   required collection is unavailable, without exposing an unauthorized collection's
   identity. Under [ADR 0023](0023-enrolled-inference-policy-and-budgets.md), a partial
   read cannot use an optional collection's unapproved inference fallback.

## Open choices

| Choice | State in the Server design |
|---|---|
| Whether `require` is offered for native reads | "If offered, must be explicit"; not decided |
| Wire spelling of the policy selector, per-member outcome and reason fields, and their REST/gRPC carriers | Not specified; the ClearView plan requires the shared response semantics to be recorded and exported before Phase 2 wire work |
| A shared deadline across members | The baseline notes there is none; C1 does not decide one |

The per-member outcome names used by the system the Server design compares against
are observations motivating the design, not proposed wire values.

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
(Server `1aa7dc5a6e0a6a4080abf43c4b12ca0a6ece6002`, ledger row R2 · C1, and the C1
table in the Server [wire compatibility policy](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/wire-compatibility.md)):

| Choice | Resolution |
|---|---|
| Whether `require` is offered for native reads | Offered, explicit only. It refuses with the existing `required-evidence-unavailable` problem type before query expansion or completion spends. C1 refusals reuse that type rather than adding one. Under `report`, a turn with no completed visible member is refused with the same type, as listed in the Server [error registry](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/api/errors.md). |
| Wire spelling of the selector, outcomes and reasons, and their carriers | Selector `collection_availability` on the turn request: a REST/SSE enum string `report` or `require`, typed gRPC `TurnRequest` `string` tag 7 where `""` keeps v1.4. Unknown values are `invalid-input`. Response `coverage` (`policy`, `complete`, `members[]`, `withheld_claims`) on a REST response that flattens the unchanged v1.4 turn response, and typed gRPC `TurnResponse.coverage` tag 9. Member outcomes `complete`, `empty`, `unavailable`; stages `search`, `probe`; reasons `no_active_index`, `engine_unavailable`, `search_failed`. SSE `probe` and `retrieval` stages gain optional `outcome` and `reason` members under an explicit policy only. |
| A shared deadline across members | Not introduced. Members keep the request's existing bounds. |

`coverage` is returned with the turn and not written to the session transcript.
Only availability errors become gaps; an authorization error still fails the turn. For item 7,
the MCP `ask_session` tool sends `collection_availability: "require"` (Server
`43d38c0ec7c36e9b68509467429671d6d558be44`).

Maintainer decisions of 20 November 2026 that bear on this record:

- **Decision 6.** The C1 wire fields above are accepted as release ready. The hub
  contract export named in the version policy remains a separate step; this
  disposition does not perform it.
- **Decision 1** (binary rollback by backup restore) does not affect this record:
  C1 adds no persisted state.

## Alternatives

- **Keep v1.4 failure on any member error.** Retained as the default when no policy
  is supplied; it is not removed.
- **Report every member, including hidden ones.** Rejected: a hidden collection must
  contribute nothing, including its name.
- **Treat a partial fan-out as complete evidence.** Rejected by the evidence rule.

## Evidence

No implementation evidence at drafting. The implementation since is cited in the
[disposition](#disposition-20-november-2026). At drafting, the [implementation ledger](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/implementation-ledger.md)
records R2 · C1 as planned, pending this semantic. The existing evidence hierarchy and
completeness tests in Server's `munarium-core` are the baseline the design preserves.

## Owners and affected consumers

| Owner | Responsibility |
|---|---|
| Founder | Accountable design owner and acceptance authority |
| Server retrieval and session API maintainers | Policy, outcomes, withholding and refusal behavior on REST, gRPC and streams |
| Server MCP maintainers | Strict policy selection for MCP multi-collection answers |

Affected consumers: the four Server SDK families, the Server CLI and console,
MCP clients through the planned tools, and the Lens-enrolled read path under ADR 0023.

## Version policy

Additive only, following the Server
[wire compatibility policy](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/wire-compatibility.md)
and COMPAT-T1: omitted options keep v1.4 meaning, new information uses optional
fields or an explicitly requested profile, and existing gRPC tags and DTO types do
not change. The exact wire shape is exported through the owning contract process and
re-vendored before any consumer relies on it. This record adds no hub schema or vector.

## Consequences

- Callers that opt in can use verified partial results while knowing exactly which
  claims were withheld and why, within their own visible scope.
- Answer composition must track which claims depend on which members; a claim that
  cannot be traced to complete evidence is withheld.
- Tests must cover the hidden-member and authorized-empty cases on both unary and
  streamed paths, not only the unavailable case.
