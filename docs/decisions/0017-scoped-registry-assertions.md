# ADR 0017: scoped Registry assertions during short-lived admission

**13 October 2026; experimental implementation directed; acceptance pending.**
This refines [ADR 0016](0016-dynamic-release-admission.md). Inputs are merged Gate
`0b4be9c28c7a5fa5eff5d70eb8256aecb559c8ae`, Warden
`fa6951ffdd83c74c0699ca217351562b2da28e5b` and Harness's
[dynamic composition PR 7](https://github.com/iokaio/munarium-harness/pull/7).
All candidates, vectors and historical acceptance pins remain unchanged.

## Timing requirement and evidence

Warden's current root admission returns a two-second `usable_at` delay; Gate waits
through that boundary before presenting the signed assertion. Warden limits connector
custody to five seconds, and live validation requires more than the two-second clock
margin to remain. Reissuing the Registry read assertion inside final admission can
therefore consume the entire usable custody interval. Increasing custody lifetime,
removing the clock margin or omitting current Registry checks is not the solution.

The first real dynamic [composition attempt](https://github.com/iokaio/munarium-harness/actions/runs/38433521333)
passed its native proposal/refusal/retry controls but failed both final-send histories.
That attempt does not establish an approved effect. Follow-up fixed-label diagnostics
are required to distinguish timing, transport and authority failures. The source
timing conflict motivates this bounded proposal; its actual end-to-end remedy still
requires the complete exact-head real-service and independent-effect oracle.

## Qualified identity reuse, with current owner checks

Gate may retain only its own Warden-issued **Registry read identity assertion** in
memory. Reuse the signed bytes without modifying or renewing them. This is neither
a cached decision nor cached Registry/Server/approval/grant/custody evidence.

Key entries by deployment, tenant, Gate presenter, Registry audience/read resource,
the complete currently verified Server authority state and the current provider-token
fingerprint. Fingerprints and token bytes remain private in memory. A different
authority state or token input cannot hit an earlier entry. Limit the cache to 32
entries; discard on process restart and eviction. No journal, response or evidence
artifact receives the service assertion or provider credential.

Before insertion and every reuse, independently verify the complete assertion chain
with the existing principal verifier against Registry's current signed recipient
identity policy, actual Gate service, tenant, deployment and clock. Require the exact
Registry read resource. Unknown keys, invalid signatures, changed presenter/scope,
expiry, unavailable trust or attenuation failures refuse. Registry independently
verifies that same chain on every live manifest resolution.

Reuse only while at least ten seconds remain in the minimum of the assertion's signed
expiry and a 30-second monotonic retention window. Neither cache access nor retry
renews either bound. The extra retention margin is a cache eligibility rule; the
existing two-second authorization clock bound and five-second custody lifetime
remain unchanged.

The existing privileged claim lookup may prepare this scoped read identity for a
dynamic task before the connector requests custody. It returns the existing claim
response, not an assertion or execution right. Final admission requires an eligible
already-prepared assertion; a miss refuses without attempting delayed issuance
inside the active custody window. A restart, expiry or changed authority may require
a new preflight, never renewal of an already issued custody ticket.

Every proposal/current-use path still resolves the live Registry manifest/head and
current signed policy/evidence, verifies retirement and activation, and rechecks the
complete current authority. Final admission still independently checks current
Council approval, live Warden custody/revocation, exact recording, capacity and worker
fences before its one-shot transaction. Unavailable owners refuse execution. There
is no cached grant or permission, and no uncertain action is resent.

## Alternatives, packets and acceptance

Always issuing another root within final admission can exhaust the bounded ticket.
Longer tickets or reduced clock margins change the safety profile. Caching owner
decisions/heads would suppress current checks. This proposal reuses only an already
qualified scoped identity while retaining every current owner query and receipt.

Gate adds the bounded private cache, dynamic preflight/final admission wiring,
signature/tenant/state/provider/expiry/restart controls and native service tests.
Harness reproduces the failed entry point with the merged Gate input and checks
native dynamic approved effects, refusal/retry histories and independent counts.
Preserve all prepared, activation, Windows/Linux, PostgreSQL and hygiene coverage.

The founder remains accountable owner/reviewer; independent human acceptance is
pending. Use the existing disposable local/CI intake and eight-hour re-estimation
boundary in ADR 0015. Report unavailable local native coverage and all failed
attempts. No new dependency, contract version, release, production trust, paid run,
qualification label or restore-reopening claim is created by this decision.
