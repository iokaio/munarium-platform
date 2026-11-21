# ADR 0030: Lens service bearer admission

Status: proposed for maintainer review, with a local Lens implementation candidate.

## Context

Server's existing openai-compatible inference provider can send a bearer
credential resolved from credentialRef. Lens currently offers an unauthenticated
loopback profile. The ClearView Lens deployment needs to authenticate Server
before reading inference inputs or disclosing loaded model identity.

## Proposal

- Give each Lens pool a high-entropy service bearer delivered through a secret
  file. Configure Server's existing credentialRef for the same secret.
  Authenticate the presented bearer before processing request bodies.
- Apply admission to discovery, readiness with stage details, embedding and
  reranking. Keep process liveness content-free and available without the
  bearer. Uniformly return HTTP 401 with a Bearer challenge and a content-free
  code for missing or invalid credentials.
- Deploy the authenticated pool on a private network with TLS-protected
  transport. Keep credentials out of manifests, receipts, diagnostics and URL
  fields. Replace credentials as part of an explicitly coordinated restart or
  pool rollout, and probe the pool before enrolling collections.
- Lens admission proves possession of the pool credential. Server continues to
  own user authorization, tenant placement, accounting and citation release
  under [ADR 0023](0023-enrolled-inference-policy-and-budgets.md) and
  [ADR 0024](0024-shared-lens-placement.md).

## Alternatives and evidence

The deployment could authenticate at an mTLS service gateway with a private
upstream socket. That requires a gateway and trust rollout per pool. A native
bearer check can use the current Server consumer and enables direct deployment
testing. TLS, service reachability and key lifecycle remain deployment concerns.

Review a real Server probe with the correct credential, missing and wrong
credential refusals, refusal precedence on malformed requests, unchanged
loopback defaults and process health. Contract publication and production qualification remain pending.
