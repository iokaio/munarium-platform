# ADR 0029: instruction-prefix ownership for inference stages

**Accepted (20 November 2026).** This records a maintainer decision of 20 November
2026 on who applies retrieval instruction prefixes for Server v1.5 "ClearView"
inference stages. The maintainer decided it directly, so it is recorded as accepted;
see [Disposition](#disposition-20-november-2026). Acceptance does not publish a
contract version, advance a catalog state or set a release label. The accountable
owner is the founder under [governance](../../GOVERNANCE.md).

Sources: the Server
[implementation ledger](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/design/implementation-ledger.md#maintainer-decisions-20-november-2026)
(maintainer decision 3 and row IR-1) and the Server
[inference endpoint guide](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/guides/inference-endpoints.md)
at Server `89e1bc2019c80d697d2d8adc9237a9ce577cf3d7` (`feat/clearview`), and the
Lens [endpoint profile](https://github.com/iokaio/munarium-lens/blob/08978eec0d463bb5a6cda2ab43b30b86595bbb58/docs/design/endpoint-profile.md)
at Lens `08978eec0d463bb5a6cda2ab43b30b86595bbb58` (`feat/clearview`). Where this
record and those texts differ, the difference is a review finding to resolve in
both places, not a silent override.

## Context

Instruction-tuned embedding models expect a query instruction, and sometimes a
passage instruction, prepended to the text. Either the caller or the endpoint could
apply them. If both do, the instruction is applied twice; if neither does, retrieval
quality silently degrades; and if the endpoint applies them, a vector's meaning
depends on endpoint configuration the Server's index identity does not record. The
Lens LENS-1 profile states that Lens applies no prefix or truncation and left open
whether Server or Lens owns the model profile's query instruction. The Server
ledger listed the question as an open cross-repository decision under LENS-1 and
IR-1. Under [ADR 0023](0023-enrolled-inference-policy-and-budgets.md), the Server
consumer and Lens must agree on the exact effective input of each call.

## Decision

1. **The Server owns retrieval instruction prefixes.** It prepends the query
   instruction to each query text and the passage instruction to each passage text,
   as plain text, before sending the embedding request. Each string the Server sends
   is the effective input.
2. **The instructions are part of the semantic index identity.** The embedding
   model, query and passage instructions, configuration name, endpoint fingerprint,
   dimension, normalization and no-truncation rule together form the semantic space,
   whose digest is part of the semantic index ID. Changing an instruction requires a
   new index.
3. **Lens applies no prefix and no truncation.** It embeds or scores exactly the
   strings it receives. Input above the model's token limit is refused, never
   truncated, consistent with ADR 0023 I1 item 4.
4. Any instruction later introduced for the rerank stage follows the same rule:
   the Server applies it and records it in the identity it affects.

## Alternatives

- **Lens-owned prefixes.** Lens would apply the model profile's instructions. Not
  adopted: the vectors' meaning would depend on endpoint configuration outside the
  Server's index identity, a second endpoint passing the generic probe could apply
  different instructions or none, and a Server that also prefixed would apply them
  twice.
- **A shared registry.** Instructions would be published per model in a registry
  both components read. Not adopted: it adds a third artifact to version and pin
  for a value the Server already records in the semantic identity, and it would
  still need a rule for which component applies it.

## Evidence

- Server `3ff798b827e3d929eb8bf87e2e92ae4945b2448b` (IR-1 to IR-4) applies
  `query_instruction` and `passage_instruction` from the collection binding as text
  prefixes and includes them in the `sem-…` semantic identity. The Server inference
  guide states: "Server applies query and passage instructions as text prefixes; the
  endpoint applies none."
- The Lens endpoint profile's LENS-1 clarifications (Lens `08978ee`) state that Lens
  applies no instruction prefix or truncation and that each string is the effective
  input. This record resolves the question that page leaves open.
- No retrieval-quality evidence is claimed. LENS-3 (evaluating and selecting the
  instructions on held-out examples) remains planned.

## Owners and affected consumers

| Owner | Responsibility |
|---|---|
| Founder | Accountable design owner and acceptance authority |
| Server retrieval and inference maintainers | Applying the prefixes on queries and build inputs, and recording them in the semantic identity (IR-1, IR-2) |
| Lens maintainers | Applying no prefix or truncation, and stating so in the LENS-1 endpoint profile |

Affected consumers: the Server inference stages (IR-1 serving and the IR-2
side-by-side semantic index builds), the Lens endpoint profile and any other
endpoint passing the generic probe, and operators configuring collection bindings.

## Version policy

No wire change. The LENS-1 request bodies are unchanged; the decision fixes which
side constructs the strings. Instruction values are binding configuration, and a
change produces a new semantic index rather than altering an existing one. This
record adds no hub schema or vector.

## Consequences

- An index is never served under instructions other than those it was built with,
  because the instructions are in the Server's semantic identity rather than in
  endpoint configuration.
- Lens stays a plain profile endpoint: an operator cannot change retrieval behavior
  by reconfiguring Lens instructions.
- The open question in the Lens endpoint profile should be updated in Lens to cite
  this record.

## Disposition (20 November 2026)

**Accepted by the maintainer on 20 November 2026**, decided directly by the
maintainer and recorded as
[maintainer decision 3](https://github.com/iokaio/munarium/blob/89e1bc2019c80d697d2d8adc9237a9ce577cf3d7/server/docs/design/implementation-ledger.md#maintainer-decisions-20-november-2026)
in the Server implementation ledger at Server
`89e1bc2019c80d697d2d8adc9237a9ce577cf3d7`: "the Server owns them; Lens applies
none." This record was drafted after that decision, so there was no separate
proposed revision to review. This disposition publishes no contract version,
composition manifest or release label, advances no catalog state or invariant
evidence field, and activates nothing.
