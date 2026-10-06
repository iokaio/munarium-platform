# Proposed local reference profile

**Proposal for review; no runnable deployment, selected dependency or qualified profile.**
This is the first profile candidate for the [build sequence](../build-plan.md) and
[reference scenario](reference-scenario.md). A profile ADR must accept its topology,
identity/broker choices, limits and threat model before effect-producing implementation.
The [contract backlog](contract-backlog.md) tracks the blocking decisions; the
[execution proposal](../decisions/0002-action-execution-protocol.md) defines the candidate
claim, consumption and dispatch protocol used below.

## Boundary and proposed topology

Use one disposable Linux VM with containers, including when the developer host is Windows.
Start with a proposed resource ceiling of 4 vCPU, 8 GiB memory and 20 GiB disposable storage;
measure actual consumption before calling this sufficient. The VM administrator, container
runtime, local certificate authority and database administrator are trusted. Containers do
not establish independent administration. No cloud account, paid provider or model call is
required; the release artifact and decision inputs are deterministic fictional fixtures.

Assign a unique `ref-<run-id>` resource prefix. Persist each service's state on a distinct
named volume; no source-checkout, home-directory or container-socket mounts. Pin the Linux
image, runtime, database and application images by immutable digest in the run record.
Only the authenticated human entry point is published, on host loopback. Fixed internal
service ports and collision-checked host ports belong in the future installation recipe.

| Process | Identity and state boundary | Proposed permitted outbound calls |
|---|---|---|
| Harness runner / agent | Unprivileged `svc-harness`; no target/broker/storage credentials | Gate proposal/lookup; Warden identity endpoint |
| Gate | `svc-gate`; sole writer of its journal, consumption and action-reservation database | Registry, Warden, Council, Server, isolated connector |
| Registry | `svc-registry`; own database role | Council authority verification and Server accountability |
| Warden | `svc-warden`; own identity/grant/revocation database role | IdP metadata, credential store, Server, Gate claim/consumption introspection; authenticated delivery to connector |
| Council | `svc-council`; own approval database role | IdP, Registry governed activation, Gate pause/apply-epoch and Warden epoch APIs, Server |
| Isolated connector | `svc-connector`; no Gate database access; ephemeral delivered credential | Gate final-admission API, disposable target; outcome back to Gate |
| Server and Matrix | Separate `svc-server` / `svc-matrix` and supported storage roles | Only documented dependencies of their pinned configurations |
| Disposable target | `svc-target`; exclusive target database/volume | No application egress |
| Human entry point | Distinct synthetic human sessions; no direct database authority | IdP, Council, governed bootstrap/recovery API |
| Test observer | Read-only target receipt/count capability; unavailable to agent | Target observation endpoint, exported records |

Stateful services also need access to their own declared datastore. Allow required local
DNS and authenticated time sources explicitly. Everything else is denied. Implement these
edges with network policy/firewall enforcement as well as authenticated, audience-bound
service calls; joining a container network alone does not enforce the table. Test denied
edges from inside the agent container. Keep all authority-changing administration outside
that container. Add Gateway, Sentinel, Assure and Console only for their scheduled slices;
Harness is an SDK/test process, not a mandatory additional deployed daemon.

Use the Server/Matrix storage engines and versions their pinned revisions actually support.
Propose PostgreSQL for new component persistence; assign distinct non-owner application
roles without cross-database access, with separate short-lived migration roles. Gate alone
owns the local transaction that consumes a grant, acquires ownership and reserves action
capacity. Warden does not write Gate tables; Server is a separately acknowledged record.
A database shared by processes does not create a distributed transaction across services.

Propose Keycloak for the first OIDC issuer, with persistent storage and its normal `start`
mode plus TLS/hostname configuration. Its [configuration guide](https://www.keycloak.org/server/configuration)
distinguishes this from development-mode defaults. Propose OpenBao as the external
credential store, using [integrated persistent storage](https://openbao.org/docs/configuration/storage/raft/)
and [KV v2](https://openbao.org/docs/secrets/kv/kv-v2/) for disposable target credentials.
These are candidate integrations, not installed dependencies or selected versions. Pin
versions, licenses and vulnerability review in the profile decision. KV storage supplies
neither one-use grants nor per-action dynamic target credentials: the Warden/connector
protocol must enforce authority, and the target must check request identity and fencing.
Warden checks Gate's authenticated consumption/claim/fence state before delivery to the
bound live connector; the connector needs a successful final-admission response before
using that credential. A broker response or recovered admission record cannot authorize a
send. If that cannot be demonstrated, this candidate profile cannot enable dispatch.

## Initial limits to decide and measure

These are proposed test inputs and acceptance bounds, **not observed performance or SLAs**.
The execution decision must reconcile them with the accepted clock and revocation protocol.

| Parameter | Initial proposal | Required behavior |
|---|---|---|
| Approval lifetime | 300 seconds | Recheck exact context and expiry at dispatch; no silent renewal |
| Grant lifetime | 30 seconds | Expiry never resets consumption or permits an uncertain resend |
| Execution ownership lease | 10 seconds | Expiry after dispatch becomes unresolved; takeover cannot resend |
| Maximum pairwise clock skew | 2 seconds | Bound/measurably monitor skew; uncertainty beyond bound stops time-sensitive admission |
| Online validation ticket lifetime | 5 seconds | Final Gate admission subtracts a 2-second expiry margin; revalidate if expired |
| Target request timeout | 5 seconds | Ambiguous timeout remains unresolved; read-only lookup is separate |
| Registry freshness at dispatch | Online confirmation plus ADR-0002's admission barrier | Gate's active epoch serializes with final admission; an online pointer read alone is insufficient |
| Revocation freshness | Online Warden validation and broker check; proposed maximum 7 seconds to stop new dispatch admission | Measure from durable revocation through final Gate admission; earlier admitted effects may finish later |
| Request / artifact size | 64 KiB / 1 MiB | Reject oversize inputs before evaluation/dispatch; digest exact accepted bytes |
| Action allowance | 2 publication admissions per tenant/target per UTC hour, including unresolved exposure | Admission atomically reserves capacity; unresolved debt carries across windows until settlement; no effect-completion rate claim |
| Restart / restore exercise | 60 seconds / 15 minutes | Measure recovery; never reopen dispatch merely to meet the target |

Use monotonic clocks for elapsed time and bounded UTC for authority validity. The proposed
7-second revocation bound is the 5-second ticket lifetime plus 2-second clock uncertainty;
it requires the accepted protocol and measured fault/race tests. A successful
health probe is not proof of synchronized clocks. No additional offline revocation/cache
grace beyond the bounded ticket is proposed. Failed required online checks, missing Server
acknowledgement or unavailable Gate journal stop admission. A partition after successful
validation cannot retroactively recall that ticket or an admitted request; report its
bounded admission race separately. Gate's activation barrier stays paused after any failed
epoch transition. A consumed grant must still pass the final admission check; after that
boundary retain uncertainty when a send cannot be excluded. Preserve outcome records/outbox
writes if Server goes
down after dispatch, then reconcile without overwriting history. Council outage prevents
new approvals; existing ones still need every live dispatch check. Infrastructure health
does not substitute for any authority check.

## Installation, bootstrap and cleanup acceptance recipe

The Harness installation packet must supply executable commands for each step below,
including failures and cleanup; none exist in this document. Run only after its component
and foundation prerequisites are satisfied, with the experimental run record already open.

1. Inventory exact repository/image/contract pins; verify the VM is disposable, resources
   are unused, local operator/cost authority is recorded and the environment expires after
   this run. Record availability and the 4 vCPU/8 GiB ceiling; exceeding it needs a new plan.
2. Create only the prefixed network/volumes, isolated service identities and role grants.
   Generate short-lived test secrets locally into restricted runtime storage. Keep secrets,
   broker recovery material and authentication tokens out of source, logs and run exports.
3. Start datastores, IdP and broker; prove persistence by restart before starting components.
   Provision two tenants and distinct requester/approver accounts. Record whether one human
   controls both accounts; account separation cannot demonstrate two-person independence.
4. Use the reviewed non-agent S1 bootstrap path to install only the synthetic policy and
   manifest. Retain the attestation and exact scope; retire bootstrap credentials and prove
   the agent cannot reopen bootstrap or ratify its own proposal. Failed retirement blocks
   dispatch. Do not use a SQL update or fixture-loader bypass to establish active authority.
5. Start decision-only services, check deny routes and tenant isolation, then run the scenario
   without granting connector credentials. Enable the isolated effect only after Stage 2
   prerequisites and operator review of the run's exact authority context. This is a
   controlled local test transition, not permission to activate a production deployment.
6. Run this stage's cases, retaining independent target evidence: crash/partition/restore
   gates the first effect; historical-key/offline evidence verification follows at Stage 4.
   Restore in dispatch-disabled mode. Reconcile consumed grants, reservations, target effects
   and Server references through a known cutoff. Keep the new recovery epoch and cutoff
   evidence outside the restored snapshot, fence off old routes, and install the target's
   new recovery-epoch/fence floor before a governed reopening; missing evidence stays blocked.
7. Export sanitized records with completeness/omission markers and digests. Revoke test
   credentials, stop exact prefixed processes and inspect the resource inventory. Remove
   only that run's containers/networks/volumes and resolved VM directory after verifying
   ownership and path containment; no global prune or broad recursive cleanup.

Retain evidence and its verification metadata beyond resource teardown under the run's
declared retention period. Production, independent-human quorum, high availability, cloud
identity and legacy targets without fencing each require a separate profile and evidence.
