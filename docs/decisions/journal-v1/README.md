# Proposed Stage 2 journal checkpoint candidate

**Inert candidate; not accepted, activated, qualified or released.** Prepared under
[ADR 0019](../0019-journal-checkpoint-exchange.md), separately from the immutable
Stage 1 and Stage 2 action bundles. This directory supplies offline review inputs,
not runtime authority. Server, Gate and Harness implementation remains pending.

The closed [schema](schema.json) defines owner enrollment, proposed mutation intent,
actual commit, immutable receipt, chain head and governed reader policy. Dedicated
request definitions cover head, record and exact digest lookup. The
[profile](profile.json) enumerates every owned Gate table/column/key from migrations
0001–0005. Checkpoint metadata is separately validated and excluded from its own
digest. A new operational table requires a new reviewed coverage profile, never a
silent omission. The decision-only SQLite cache is outside effect authority.

Each record uses `decision-json-v1`: canonical UTF-8 sorted ASCII member names,
no duplicate keys/BOM/floats, integers within 53 bits, at most 64 KiB and 16 container
levels. Deltas contain 1–256 complete typed row changes, ordered by table and
canonical key bytes. Before/after absence is null. Reject unchanged rows, duplicate
keys, key mutation, cross-scope rows and incomplete/unknown columns. Proposed delta
bytes are retained in the intent so custody does not depend on a later commit;
the commit repeats the exact delta after the local SQL transaction.

Record digests use `munarium:stage2:{record-type}:v1` followed by NUL and canonical
record bytes. Delta digest uses `munarium:stage2:journal-delta:v1` followed by NUL
and canonical `{"rows":[...delta...]}`. State digest streams SHA-256 over
`munarium:stage2:journal-state:v1` plus NUL, canonical `{"scope":...,"tables":[...]}`
plus NUL, then each canonical `{"table":...,"key":...,"row":...}` plus NUL. Tables
and rows sort by ASCII table name and canonical UTF-8 key bytes. All 14 table names
are included even when empty. Each entry retains its individual canonical bounds;
the entire journal is streamed and need not fit a single record. No database
sequence allocator value supplies effect authority; retain every assigned row
sequence and original receipt. Checkpoint mutation sequence is separate.

Intent admission requires the exact enrollment, prior committed checkpoint, actual
before state and audit prefix. It retains proposed after state, complete proposed
delta, mutation kinds, operation/attempt identities and conservative exposure.
Consumption/send footprints retain target, grant, worker/fence, spent-send status
and every applicable bucket/window/unit/limit. Unknown pending intent cannot be
aborted, refunded or reset by this profile. Commit cannot change the proposal.
Retries recover exact evidence receipts under current authorization, never send
permission. Five-second custody and two-second clock uncertainty remain unchanged.

The [vectors](vectors.json) include fixed canonical bytes/digests and refusal
cases. The offline oracle checks shape, row replay, chain linkage, ownership/scope
and footprint consistency. Its supplied trusted state is fictional test input,
not authentication, independent SQL observation, target evidence, capacity-policy
verification, durable high-water storage or proof of safe reopening. Runtime tests
and independent consumer conformance must add those boundaries before qualification.

Reproduce without modifying files:

```console
python scripts/generate_journal_candidate.py --check
python -m unittest discover -s scripts -p "test_*.py"
```

Export only after committing the exact source:

```console
python scripts/vendor_journal.py --destination ../consumer/new-journal-namespace
```

The [bundle lock](bundle-lock.json) pins all four review files. Export verifies
committed bytes, lock/profile agreement and destination collisions before writing;
the vendor lock adds the exact source revision. Existing locked versions and
different destination artifacts are never overwritten. No acceptance pin,
catalog/invariant status or release label advances from generating or exporting it.
