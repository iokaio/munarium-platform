# SPDX-License-Identifier: Apache-2.0
"""Render the architecture review's original SVG diagrams with Python stdlib.

Run from any directory: python docs/architecture/images/render_architecture.py
SVGs are deterministic, contain accessible titles/descriptions, and need no fonts,
network resources, diagram service, cloud account, or runtime dependencies.
"""

from html import escape
from pathlib import Path


OUT = Path(__file__).resolve().parent
INK = "#19324b"
MUTED = "#536b80"
BLUE = "#2374ab"
TEAL = "#087f82"
PURPLE = "#7653a2"
ORANGE = "#b56a19"
RED = "#aa384b"
COLORS = {
    "agent": ("#edf4fb", BLUE),
    "mediation": ("#e9f7f5", TEAL),
    "authority": ("#f2edf9", PURPLE),
    "assurance": ("#fff5e6", ORANGE),
    "neutral": ("#f3f6f9", MUTED),
    "risk": ("#fff0f2", RED),
}


class Diagram:
    def __init__(self, name, title, subtitle, width, height, description):
        self.name, self.width, self.height = name, width, height
        self.parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<!-- SPDX-License-Identifier: Apache-2.0 -->',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(description)}</desc>',
            '<defs>',
        ]
        for color in (INK, BLUE, TEAL, PURPLE, ORANGE, RED, MUTED):
            self.parts.append(
                f'<marker id="arrow{color[1:]}" markerWidth="10" markerHeight="8" '
                'refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse">'
                f'<path d="M0,0 L10,4 L0,8 Z" fill="{color}"/></marker>'
            )
        self.parts += [
            '</defs>',
            '<style>text{font-family:Arial,Helvetica,sans-serif} '
            '.title{font-size:29px;font-weight:700} .heading{font-size:19px;font-weight:700} '
            '.body{font-size:16px} .small{font-size:14px}</style>',
            f'<rect width="{width}" height="{height}" fill="#fff"/>',
        ]
        self.text(32, 44, title, "title")
        self.text(32, 75, subtitle, "body", MUTED)

    def text(self, x, y, value, cls="body", color=INK, anchor="start"):
        self.parts.append(
            f'<text x="{x}" y="{y}" class="{cls}" fill="{color}" '
            f'text-anchor="{anchor}">{escape(value)}</text>'
        )

    def panel(self, x, y, w, h, title, kind="neutral", dashed=False):
        fill, stroke = COLORS[kind]
        dash = ' stroke-dasharray="8 5"' if dashed else ''
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>'
        )
        self.text(x + 18, y + 29, title, "heading", stroke)

    def box(self, x, y, w, h, title, lines=(), kind="neutral"):
        _, stroke = COLORS[kind]
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" '
            f'fill="#fff" stroke="{stroke}" stroke-width="1.5"/>'
        )
        self.text(x + 16, y + 29, title, "heading", stroke)
        for i, line in enumerate(lines):
            self.text(x + 16, y + 54 + 22 * i, line)

    def arrow(self, points, label="", color=INK, dashed=False, label_at=None):
        dash = ' stroke-dasharray="7 5"' if dashed else ''
        self.parts.append(
            '<polyline points="' + ' '.join(f'{x},{y}' for x, y in points) +
            f'" fill="none" stroke="{color}" stroke-width="2"{dash} '
            f'marker-end="url(#arrow{color[1:]})"/>'
        )
        if label:
            x, y = label_at or ((points[0][0] + points[-1][0]) / 2,
                               (points[0][1] + points[-1][1]) / 2 - 10)
            width = len(label) * 7.5 + 16
            self.parts.append(
                f'<rect x="{x-width/2}" y="{y-15}" width="{width}" '
                'height="21" rx="3" fill="#fff"/>'
            )
            self.text(x, y, label, "small", color, "middle")

    def finish(self, note):
        self.text(32, self.height - 38, note, "small", MUTED)
        self.text(32, self.height - 16,
                  "TARGET ARCHITECTURE • Proposed deployment choices • See architecture-review.md for evidence and limits",
                  "small", MUTED)
        (OUT / f"{self.name}.svg").write_text('\n'.join(self.parts + ['</svg>']) + '\n',
                                                 encoding="utf-8")


def context():
    d = Diagram("01-platform-context", "Munarium Governance Platform | System context",
                "The agent may reason and propose; deployed controls determine what may take effect.",
                1500, 800,
                "Agents use mediation services. Separate human authority governs rules. Targets and model providers are outside the platform boundary.")
    d.panel(405, 115, 665, 565, "Qualified platform boundary", "neutral", True)
    d.box(35, 170, 280, 125, "People", ["Business approvers", "Operators and auditors", "Distinct governing authority"], "authority")
    d.box(35, 440, 280, 125, "Agent applications", ["Harness SDK in the runtime", "Scoped workload identity", "No direct target credentials"], "agent")
    d.box(435, 170, 605, 100, "Authority", ["Registry • Warden • Council", "Inventory, identity, grants, approval and activation"], "authority")
    d.box(435, 330, 605, 125, "Mediation", ["Gate: consequential action • Gateway: model calls", "Server: governed memory and accountability", "Matrix: governed read-only structured evidence"], "mediation")
    d.box(435, 525, 605, 100, "Assurance", ["Sentinel • Assure • Console", "Operational views, portable evidence and human workflows"], "assurance")
    d.box(1170, 165, 295, 100, "Enterprise sources", ["Documents and structured data", "Scoped read access"], "neutral")
    d.box(1170, 345, 295, 100, "Business targets", ["SaaS, release and other tools", "Isolated connectors act here"], "neutral")
    d.box(1170, 525, 295, 100, "Model providers", ["Approved hosted or local routes", "Data disclosure and cost limits"], "neutral")
    d.arrow([(315, 215), (435, 215)], "govern", PURPLE)
    d.arrow([(315, 500), (360, 500), (360, 390), (435, 390)], "read / propose", BLUE, label_at=(365, 374))
    d.arrow([(735, 270), (735, 330)], "bound authority", PURPLE)
    d.arrow([(735, 455), (735, 525)], "records / views", ORANGE)
    d.arrow([(1040, 365), (1110, 365), (1110, 215), (1170, 215)], color=TEAL)
    d.arrow([(1040, 397), (1170, 397)], "authorized effect", TEAL)
    d.arrow([(1040, 430), (1130, 430), (1130, 575), (1170, 575)], color=TEAL)
    d.text(440, 715, "Four powers: READ  |  GOVERNED WRITE  |  ACT  |  GOVERN", "heading", INK)
    d.finish("Guarantee covers declared, qualified paths. Unmanaged credentials, tools and administrators remain explicit trust assumptions.")


def logical():
    d = Diagram("02-logical-components", "Logical architecture | Four planes, eleven components",
                "Component ownership is distinct from process count. Harness is an SDK; the hub is documentation, contracts and evidence.",
                1600, 1070,
                "Four planes contain Harness; Gate, Gateway, Server and Matrix; Registry, Warden and Council; Sentinel, Assure and Console. A connector alone sends target mutations.")
    d.panel(30, 120, 310, 225, "AGENT PLANE", "agent")
    d.panel(425, 120, 515, 695, "MEDIATION PLANE", "mediation")
    d.panel(1025, 120, 545, 695, "AUTHORITY PLANE", "authority")
    d.box(50, 175, 270, 135, "Application + Harness", ["Build stable proposals", "Bind verified task lineage", "Look up typed outcomes", "SDK carries no enforcement"], "agent")
    d.panel(30, 455, 310, 180, "CONNECTOR DOMAIN", "mediation", True)
    d.box(50, 505, 270, 110, "Isolated connector", ["Own privilege domain", "Bound live invocation", "Target-only narrow egress"], "mediation")
    d.box(50, 690, 270, 90, "Target system", ["Effect key + precondition", "Supported recovery fence"], "neutral")
    for y, title, lines in [
        (175, "Gate", ["Policy and exact-request admission", "Claims, reservations, final-send journal"]),
        (330, "Gateway", ["Model routes and disclosure checks", "Model-spend reservations and settlement"]),
        (485, "Server", ["Governed memory and protected action records", "Authoritative append-only accountability"]),
        (640, "Matrix", ["Approved read-only query contracts", "Typed evidence, source scope and provenance"]),
    ]:
        d.box(445, y, 475, 115, title, lines, "mediation")
    for y, title, lines in [
        (175, "Registry", ["Signed manifests and inert candidates", "Immutable artifacts + activation pointers"]),
        (365, "Warden", ["Verified principal/delegation and narrow grants", "Credential custody, revocation and suspension"]),
        (555, "Council", ["Exact approvals and distinct human authority", "Ratification + activation coordination"]),
    ]:
        d.box(1045, y, 505, 115, title, lines, "authority")
    d.arrow([(320, 230), (445, 230)], "proposal", BLUE)
    d.arrow([(320, 280), (380, 280), (380, 385), (445, 385)], "model", BLUE, label_at=(380, 365))
    d.arrow([(445, 265), (355, 265), (355, 545), (320, 545)], "dispatch", TEAL, label_at=(355, 470))
    d.arrow([(185, 615), (185, 690)], "effect", TEAL)
    d.arrow([(920, 220), (1045, 220)], "manifest", PURPLE)
    d.arrow([(920, 240), (975, 240), (975, 415), (1045, 415)], "identity / grant", PURPLE, label_at=(977, 350))
    d.arrow([(920, 265), (955, 265), (955, 605), (1045, 605)], "approval", PURPLE, label_at=(984, 580))
    d.panel(30, 845, 1540, 145, "ASSURANCE PLANE | authorized records and governed operator APIs", "assurance")
    d.box(50, 892, 460, 77, "Sentinel", ["Rebuildable timelines + bounded suspension"], "assurance")
    d.box(550, 892, 470, 77, "Assure", ["Evidence packages + offline integrity verification"], "assurance")
    d.box(1060, 892, 490, 77, "Console", ["Human views + Council/Warden service calls"], "assurance")
    d.finish("Selected dependencies shown. Each state owner writes only its own store; all authoritative producers retain ordered Server outboxes.")


def action():
    d = Diagram("03-governed-action", "Governed action | From proposal to a known or unresolved effect",
                "An allow decision, approval, grant or HTTP success alone cannot authorize a target send.",
                1600, 1180,
                "Sequence across agent, Gate journal, authority services, Server, connector and target. Durable claim, grant consumption and predispatch acknowledgement precede one live final admission.")
    xs = [135, 400, 670, 940, 1205, 1470]
    labels = ["Agent / Harness", "Gate + journal", "Registry / Council", "Warden", "Server", "Connector / target"]
    for x, label in zip(xs, labels):
        d.box(x - 115, 120, 230, 65, label, kind="neutral")
        d.parts.append(f'<line x1="{x}" y1="185" x2="{x}" y2="1055" stroke="#dce4ed" stroke-width="2"/>')
    rows = [
        (235, 0, 1, "1  Submit stable intent; authenticated caller", BLUE),
        (290, 1, 3, "2  Verify current principal / delegation", PURPLE),
        (345, 1, 2, "3  Pin manifest / active policy; evaluate", PURPLE),
        (400, 1, 4, "4  Archive request + decision; exact custody", TEAL),
        (455, 1, 2, "5  Exact approval if policy requires", PURPLE),
        (565, 1, 3, "7  Issue claim-bound grant; retry keeps expiry", PURPLE),
        (675, 1, 4, "9  Predispatch outbox; await exact durable ACK", TEAL),
        (730, 1, 3, "10  Current grant, approval and connector custody", PURPLE),
        (785, 3, 5, "11  Credential only to bound connector", PURPLE),
        (845, 5, 1, "12  Live final-admission request", TEAL),
        (945, 1, 5, "14  First live winning reply allows one send", TEAL),
        (1000, 5, 1, "15  Target receipt or uncertainty; retain exposure", TEAL),
        (1050, 1, 4, "16  Outcome outbox; immutable later reconciliation", TEAL),
    ]
    for y, a, b, label, color in rows:
        d.arrow([(xs[a], y), (xs[b], y)], label, color)
    for y, text in [(510, "6  Persist immutable claim"),
                    (620, "8  Atomic: consume + own + reserve + outbox"),
                    (900, "13  Lock: recheck + spend send opportunity")]:
        d.parts.append(f'<rect x="230" y="{y-21}" width="545" height="37" rx="6" fill="#e9f7f5" stroke="{TEAL}"/>')
        d.text(247, y + 3, text, "body", TEAL)
    d.text(35, 1100, "Lost final-admission reply: no replacement send. Lost target reply: unresolved; investigate through independent read-only evidence.", "body", RED)
    d.finish("No distributed transaction spans Gate, Warden, Server and target. The connector's target contract bounds the actual effect guarantee.")


def governance():
    d = Diagram("04-governance-activation", "Governance lifecycle | Approval is separate from activation",
                "Candidates remain inert until a separately authorized, recorded transition installs an effective artifact set.",
                1500, 860,
                "Proposal, package, shadow testing, distinct ratification and time lock precede a paused multi-participant activation. Incomplete receipt sets keep dispatch paused.")
    top = [(35, "1  Propose", ["Agent or human", "Inert candidate"]),
           (330, "2  Package / test", ["Registry admission", "Digest + compatibility"]),
           (625, "3  Shadow / review", ["Declared replay scope", "Boundary regressions"]),
           (920, "4  Ratify / time-lock", ["Council + eligible humans", "Exact set, scope and expiry"])]
    for x, title, lines in top:
        d.box(x, 135, 260, 115, title, lines, "authority")
    for x in [295, 590, 885]:
        d.arrow([(x, 192), (x + 35, 192)], color=PURPLE)
    d.panel(35, 315, 1430, 340, "5  Activate under a durable cell barrier | Council coordinates; each participant owns its commit", "authority")
    d.box(60, 385, 250, 135, "Gate: pause", ["Expected prior epoch", "Serialize against admission", "Durable pause receipt"], "mediation")
    d.box(375, 385, 370, 135, "Apply exact transition", ["Registry: effective artifact set", "Server: protected custody / authority", "Warden: current grant authority"], "authority")
    d.box(810, 385, 280, 135, "Gate: install epoch", ["Authenticated owner receipts", "Complete participant set", "Still paused while incomplete"], "mediation")
    d.box(1150, 385, 290, 135, "Gate: resume", ["Verify current heads", "Commit matching transition", "New admissions may proceed"], "mediation")
    d.arrow([(310, 450), (375, 450)], color=PURPLE)
    d.arrow([(745, 450), (810, 450)], color=PURPLE)
    d.arrow([(1090, 450), (1150, 450)], color=PURPLE)
    d.arrow([(1050, 250), (1050, 288), (20, 288), (20, 450), (60, 450)], color=PURPLE)
    d.text(62, 571, "Expired, partial or conflicting transition: retain history and keep admission paused; lookup never resumes execution.", "body", RED)
    d.text(62, 607, "Later profiles declare all required participants, including Gateway where model-route governance is affected.", "body", MUTED)
    d.box(375, 695, 700, 80, "6  Observe / retain / controlled rollback", ["A prior bundle is reactivated under a new epoch; history is never rewritten."], "assurance")
    d.arrow([(1295, 520), (1295, 735), (1075, 735)], color=ORANGE)
    d.finish("Action approval permits one exact action context. Governance ratification changes rules. Neither substitutes for the other.")


def model_evidence():
    d = Diagram("05-model-evidence", "Model and evidence paths | Read and disclosure remain governed",
                "Model output and retrieved content are inputs to a proposal; neither creates action authority.",
                1500, 900,
                "Agents retrieve scoped Server memory and Matrix query evidence, invoke models through Gateway reservations and disclosure checks, and submit a separately authorized Gate proposal. Assurance reads ledger ranges.")
    d.box(35, 160, 300, 140, "Agent + Harness", ["Verified task/root lineage", "Build proposal from evidence", "Treat model output as untrusted"], "agent")
    d.box(460, 130, 435, 130, "Server / Matrix", ["Scoped memory or approved query", "Point-in-time evidence + provenance", "Current access checked on reuse"], "mediation")
    d.box(460, 365, 435, 155, "Gateway", ["Check route, destination and data labels", "Reserve model-spend capacity", "Record required admission facts", "Settle usage; unknown cost retains exposure"], "mediation")
    d.box(1075, 370, 390, 145, "Approved model provider", ["Hosted endpoint or local inference", "Streaming / usage / response metadata", "Provider adapter qualification required"], "neutral")
    d.box(35, 590, 300, 130, "Gate action path", ["Independent action evaluation", "Action-capacity reservations", "Separate grant + final admission"], "mediation")
    d.box(460, 625, 435, 130, "Server accountability ledger", ["Producer-owned ordered outboxes", "Original facts + correction links", "Qualified source ranges / coverage"], "mediation")
    d.box(1075, 625, 390, 130, "Sentinel / Assure / Console", ["Authorized views and exports", "Watermarks + explicit omissions", "Offline verifier uses separate trust"], "assurance")
    d.arrow([(335, 190), (460, 190)], "scoped read", BLUE)
    d.arrow([(335, 255), (400, 255), (400, 420), (460, 420)], "model request", BLUE, label_at=(390, 350))
    d.arrow([(895, 425), (1075, 425)], "admitted disclosure", TEAL)
    d.arrow([(1075, 485), (895, 485)], "usage / response", TEAL)
    d.arrow([(185, 300), (185, 590)], "new action proposal", BLUE)
    d.arrow([(335, 665), (460, 665)], "action facts", TEAL)
    d.arrow([(677, 520), (677, 625)], "model facts", TEAL)
    d.arrow([(895, 690), (1075, 690)], "authorized export", ORANGE)
    d.text(40, 815, "Gate action limits and Gateway model budgets share verified attribution, but have separate balances and transaction owners.", "body", MUTED)
    d.finish("A digest proves content binding, not truth. A read can disclose sensitive data; a hosted model call can itself be consequential.")


def cloud(name, provider):
    azure = provider == "Azure"
    d = Diagram(name, f"{provider} physical architecture | Proposed single-region governed cell",
                "One home cell per operation; private service boundaries; separate agent and connector execution domains.",
                1700, 1220,
                f"Proposed {provider} deployment separates corporate ingress, isolated agent compute, private platform Kubernetes across zones, connector compute, owner datastores, secrets and an independently retained recovery boundary.")
    edge = "Private Application Gateway" if azure else "Internal Application Load Balancer"
    cluster = "Private AKS cluster" if azure else "Private EKS cluster"
    network = "Platform subscription / spoke VNet" if azure else "Platform account / private VPC"
    agent = "Agent subscription / VNet" if azure else "Agent account / VPC"
    connector = "Connector subscription / VNet" if azure else "Connector account / VPC"
    identity = "Microsoft Entra ID" if azure else "Enterprise IdP + AWS IAM"
    database = "Azure PostgreSQL Flexible Server" if azure else "RDS for PostgreSQL (Multi-AZ)"
    vault = "Key Vault + managed identity adapter" if azure else "Secrets Manager + IAM role adapter"
    objects = "Blob Storage + approved retention" if azure else "S3 + approved Object Lock policy"
    registry = "Azure Container Registry" if azure else "Amazon ECR"
    telemetry = "Azure Monitor / enterprise SIEM" if azure else "CloudWatch / enterprise SIEM"
    d.box(30, 120, 300, 110, "Corporate access", ["People + enterprise applications", "VPN / private circuit", "Separate operator credentials"], "neutral")
    d.box(385, 120, 430, 110, edge, ["Human Console + scoped API ingress", "TLS; preserve verified caller identity"], "neutral")
    d.box(950, 120, 360, 110, identity, ["Human and workload enrollment", "Cloud identity is not an action grant"], "authority")
    d.box(1380, 120, 290, 110, "External dependencies", ["Enterprise query sources", "Approved model providers", "Business targets"], "neutral")
    d.panel(30, 290, 330, 535, agent, "agent", True)
    d.box(50, 350, 290, 140, "Isolated agent compute", ["Separate cluster or VM pool", "Application + Harness SDK", "No target or vault IAM rights", "Egress only to admitted APIs"], "agent")
    d.box(50, 650, 290, 105, "Agent network controls", ["Default deny + route allowlist", "No cluster/host admin", "No metadata credential bypass"], "agent")
    d.panel(410, 290, 850, 535, network, "mediation", True)
    d.panel(435, 345, 800, 300, cluster + " | zone-spread eligible replicas", "mediation")
    d.box(455, 402, 350, 92, "Mediation workloads", ["Gate • Gateway • Server • Matrix", "Separate identities and service roles"], "mediation")
    d.box(850, 402, 365, 92, "Authority workloads", ["Registry • Warden • Council", "Protected administrative permissions"], "authority")
    d.box(455, 520, 760, 90, "Assurance workloads", ["Sentinel • Assure • Console  |  read models have source watermarks", "Operators approve through service APIs; telemetry is not audit custody."], "assurance")
    for i in range(3):
        zx = 455 + 260 * i
        d.parts.append(f'<rect x="{zx}" y="617" width="240" height="22" rx="4" fill="#fff" stroke="{TEAL}"/>')
        d.text(zx + 120, 633, f"Availability zone {i + 1}", "small", TEAL, "middle")
    d.box(435, 685, 800, 100, "Private data access + default-deny east/west policy", ["Authenticated, audience-bound service channels; qualified TLS termination", "Private cluster API; explicit DNS/time/image/identity endpoints; controlled provider egress"], "neutral")
    d.panel(1310, 290, 360, 270, connector, "neutral", True)
    d.box(1330, 350, 320, 140, "Isolated connector workers", ["One qualified adapter / privilege domain", "Credential delivered through Warden", "Final admission from Gate before send", "Target allowlist; no agent secret mounts"], "mediation")
    d.panel(1310, 610, 360, 215, "Independent target boundary", "risk", True)
    d.box(1330, 660, 320, 110, "Target-owned state", ["Stable effect identity + precondition", "Recovery floor retained outside Gate", "Independent read-only effect observer"], "risk")
    d.arrow([(330, 175), (385, 175)], color=BLUE)
    d.arrow([(600, 230), (600, 345)], "private ingress", BLUE)
    d.arrow([(340, 405), (455, 445)], "scoped APIs", BLUE, label_at=(389, 405))
    d.arrow([(1215, 440), (1330, 440)], "grant / custody", PURPLE)
    d.arrow([(760, 494), (760, 505), (1285, 505), (1285, 465), (1330, 465)],
            "Gate dispatch / final admission", TEAL, label_at=(1125, 512))
    d.arrow([(1490, 490), (1490, 580), (1685, 580), (1685, 715), (1650, 715)],
            "one admitted send", TEAL, label_at=(1510, 573))
    d.panel(30, 870, 1640, 255, "PRIVATE MANAGED SERVICES / OWNER-ISOLATED STATE | Each service accesses only its enrolled resources", "neutral")
    d.box(50, 925, 525, 135, database, ["Gate journal: atomic consumption / capacity", "Owner-separated databases, roles and backups", "Server ledger: protected accountability custody", "Other owner stores: qualified single-writer PVs"], "mediation")
    d.box(610, 925, 485, 135, vault, ["Cloud adapter requires admission tests", "Broker access limited to Warden", "Target secret delivered only to connector", "Vault storage is not grant or send authority"], "authority")
    d.box(1130, 925, 520, 135, objects, [registry + " • digest-pinned images", telemetry, "Export/checkpoint storage + separate trust custody", "Cross-region backup: dispatch stays quarantined"], "assurance")
    d.arrow([(835, 825), (835, 870)], "private endpoints / private database routing", TEAL)
    d.text(52, 1099, "Cloud vaults store credentials; Warden owns grant semantics. Zones and replica counts depend on the qualified storage profile.", "small", MUTED)
    d.finish("Selected physical paths shown. Cross-network allowlists enforce the logical flow table; account/subscription separation requires distinct real administrators.")


def recovery():
    d = Diagram("08-recovery-assurance", "Failure, recovery and assurance | Preserve uncertainty before availability",
                "A database restore or failover cannot resurrect a consumed grant, erase exposure or authorize another effect.",
                1500, 880,
                "Local journals and outboxes retain facts; Server provides independently retained custody; the target retains its recovery floor. Restore stays quarantined until reconciliation and separately authorized reopening.")
    d.box(35, 140, 420, 140, "Owner journals + outboxes", ["Claim, consumption and send intent", "Approval / grant / cancellation receipts", "Unresolved capacity debt survives restart", "Retry exact event bytes; never resend target"], "mediation")
    d.box(535, 140, 430, 140, "Server protected custody", ["Original archives + acknowledgements", "Append-only correction / reconciliation", "Independent source ranges and cutoffs", "Backups alone are not restore admission"], "mediation")
    d.box(1045, 140, 420, 140, "Target + external recovery", ["Actual effects and independent receipts", "Installed monotonic recovery floor", "Recovery generation outside restored store", "Stale workers refused by target profile"], "authority")
    d.arrow([(455, 210), (535, 210)], "outbox", TEAL)
    d.panel(35, 355, 1430, 245, "Restore / partial transition / missing evidence", "risk")
    d.box(60, 420, 270, 120, "1  Quarantine", ["Disable issuance / dispatch", "Preserve unresolved records", "No health-probe override"], "risk")
    d.box(390, 420, 360, 120, "2  Reconcile retained facts", ["Server cutoff + target observation", "Claim / reservation / cancellation facts", "Missing or disputed facts stay visible"], "risk")
    d.box(810, 420, 290, 120, "3  Install new generation", ["Separate recovery authority", "Target-floor acknowledgement", "Current policy / identity checks"], "authority")
    d.box(1160, 420, 280, 120, "4  Governed reopening", ["Only if profile evidence holds", "No replay of consumed sends", "Unresolved work stays blocked"], "mediation")
    for a, b in [(330, 390), (750, 810), (1100, 1160)]:
        d.arrow([(a, 480), (b, 480)], color=RED)
    d.box(35, 670, 650, 110, "Operational assurance", ["Sentinel + Console: known state, lag, omissions and pending recording", "Suspension narrows authority; restoration requires its governing path."], "assurance")
    d.box(785, 670, 680, 110, "Portable evidence / offline verification", ["Assure: composition, records, checkpoints, covered ranges and gaps", "Verify integrity with independent trust; do not infer truth or compliance."], "assurance")
    d.finish("Target-effect status and recording-delivery status are separate. Full recovery/reopening and evidence export remain qualification obligations.")


def main():
    context()
    logical()
    action()
    governance()
    model_evidence()
    cloud("06-azure-physical", "Azure")
    cloud("07-aws-physical", "AWS")
    recovery()
    print("Rendered 8 architecture SVGs.")


if __name__ == "__main__":
    main()
