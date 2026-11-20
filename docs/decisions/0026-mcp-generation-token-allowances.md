# ADR 0026: MCP generation opt-in, token allowances and shared generation

**Proposed, 20 November 2026; open choices listed.** This records the shared
semantics of Server v1.5 "ClearView" decisions A2, A8 and A9. A2 requires the A8
allowances, and A9 defines how they combine, so the three are recorded together.
It does not accept a contract, advance a catalog state or publish a version. The
accountable owner is the founder under [governance](../../GOVERNANCE.md).

Normative source: the Server design at
`ef32276d593c190b5a25234a85604564769d0e60` (Server `feat/clearview`), sections
[A2](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#a2),
[A8](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#a8),
[A9](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#a9),
[7.5](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#75-configuration)
and [9.2](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/mcp-analysis.md#92-sequencing).
The Server design records A2, A8 and A9 as maintainer design decisions and the A8
policy inheritance as a separate implementation recommendation; this hub record
proposes the decisions as shared semantics and does not record their acceptance.

## Context

MCP tools can trigger model calls for expansion, verification and answers. The
native v1.4 optional `dailyTotalTokens` budget is keyed by tenant, provider
configuration and UTC day, and its physical-attempt estimates can be lower than
observed usage, so it cannot establish a hard limit. Operators, the console, report
readers and the planned policy contract need one meaning for who may spend, how much
and on whose behalf.

## Decision (proposed)

### A2: opt-in and budget owner

1. MCP generative model calls are disabled by default. An operator must explicitly
   enable generation, name the budget owner and configure both A8 allowances for the
   collection or index. This applies to local and remote models, including
   deployments without price data. Admission uses tokens; currency may appear in
   reports when pricing is available.
2. Disabled execution forms are omitted from the tool catalog; authorized receipt
   reads remain available under [ADR 0027](0027-mcp-durable-admission-and-recovery.md).

### A8: request and daily allowances

1. Operators configure a per-request allowance and a daily allowance, each in total
   input plus output tokens, at the collection or index level.
2. Server resolves the policy from the authorized collection and pinned index. Tool
   arguments cannot select the policy or payer.
3. Within one admitted tool invocation, expansion, verification, final answers,
   re-asks and every physical retry count toward the request total. A turn with
   `complete: false` can still request model-based expansion.
4. Each scope's daily allowance covers its requests across all replicas for the UTC
   day. Changing an index pin preserves a collection's accumulated daily usage.
5. Before each physical submission, reserve against the remaining request allowance and
   each applicable daily allowance in one shared, durable admission decision, using the
   ADR 0027 invocation identity and a distinct physical-attempt identity. Size the
   reservation from a defensible upper bound on effective input and permitted output.
   Refuse before dispatch, with a typed error for a required stage, if an allowance is
   insufficient, accounting is unavailable or the adapter cannot bound token use.
6. Settle each reservation once against reliable usage. Keep the full reservation
   against its original request and day when dispatch or usage is uncertain. A retry
   needs a fresh reservation. Usage above a declared bound is retained and stops further
   use of that bound pending investigation. Native v1.4 admission, tier counters and
   settlement stay compatible.

### A9: shared generation

1. For an attempt with several contributing collections or indexes, use their largest
   effective per-request allowance after resolving each contributor's policy. The
   allowances do not add. An unrelated or merely available index cannot raise it.
2. Contributors are the scopes that supply material or on whose behalf the stage runs,
   including material carried forward in session context; for expansion before
   retrieval, the authorized scopes selected for that expansion.
3. Every contributor must authorize the same payer. An unknown contributor or no
   commonly authorized budget refuses the attempt.
4. The larger limit applies to the request allowance only. Each contributor must have
   enough daily tokens for the full attempt. Reserve atomically against the shared
   request allowance and all applicable daily balances across replicas, deduplicating
   repeated scopes and leaving no partial reservation on refusal. When contributors
   change between stages, carry the request's usage and outstanding reservations forward.
5. The common payer is charged once per physical attempt; settlement correlates to the
   physical-attempt identity so a repeated receipt cannot duplicate usage. Refusal
   details and usage reports are scoped to the caller's authority.

The Server's worked example: Legal allows 2,000 tokens per request and Finance 8,000;
a shared call with both contributing and a common payer has an 8,000-token ceiling,
while Legal alone keeps 2,000.

Embedding and reranking costs on enrolled collections follow
[ADR 0023](0023-enrolled-inference-policy-and-budgets.md), not these allowances.

## Open choices

| Choice | State in the Server design | Closing evidence named by Server |
|---|---|---|
| Trusted collection/index policy representation | Open item, shared with the A4 scope spelling; "specify the trusted collection/index policy representation" before implementation | Additive contract with issuance, wire shapes, index-policy precedence and rejection vectors; re-vendored with native and MCP conformance |
| Index-policy precedence | Recommendation only: with no index-specific allowances a pinned index inherits the collection pair; a complete index pair supplies the index's own ceiling and daily allowance; an incomplete override is rejected; the collection daily balance remains a separate limit across all pins, reserved once per attempt alongside each distinct contributing index's own daily balance | A8-T3 |
| How Server identifies the contributors to each shared call | Required by 9.2, not specified | A9-T1 and A9-T2 |
| How the budget owner is named and bound | A2 requires a named owner; the representation is not specified | Same export |

This record does not select a representation and does not promote the inheritance
recommendation to a decision.

## Alternatives

- **Use the native `dailyTotalTokens` budget as the hard limit.** Rejected: its
  estimates can undercount and it is keyed by provider configuration, not scope.
- **Sum contributors' request allowances.** Rejected: allowances do not add.
- **Let tool arguments choose policy or payer.** Rejected.
- **Enable generation by default when pricing is absent or the model is local.**
  Rejected: opt-in applies regardless.

## Evidence

No implementation evidence. The [implementation ledger](https://github.com/iokaio/munarium/blob/ef32276d593c190b5a25234a85604564769d0e60/server/docs/design/implementation-ledger.md)
records A2, A8 and A9 as planned. Acceptance cases A2-T1, A8-T1 to A8-T3, A9-T1 and
A9-T2 count physical provider arrivals against admitted attempts.

## Owners and affected consumers

| Owner | Responsibility |
|---|---|
| Founder | Accountable design owner and acceptance authority |
| Server MCP and tenant budget maintainers | Admission, reservation, settlement and reports |
| Server API and hub contract owners | The exported policy representation and rejection vectors |

Affected consumers: operators and the console's policy views, report readers and
the four Server SDK families' report decoders, providers receiving submissions, and
MCP clients receiving typed refusals.

## Version policy

Additive and off by default (COMPAT-T4, MCP-RULE-6); the native token budgets keep
their v1.4 behavior. The policy representation is exported through the owning
contract process and re-vendored before consumers rely on it. This record adds no
hub schema or vector. It concerns Server's own MCP generation admission and does not
define the later Gateway invocation and settlement contract that
[ADR 0011](0011-platform-contract-evolution.md) reserves.

## Consequences

- No MCP model call happens without an explicit operator decision, a named owner and
  both allowances; an unbounded request makes zero calls.
- Uncertain outcomes hold capacity rather than release it, so interrupted work can
  exhaust a day's allowance until settled.
- A shared answer can exceed a smaller contributor's standalone ceiling only within
  the largest contributor's ceiling and every contributor's daily balance.
