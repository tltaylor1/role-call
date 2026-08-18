# Threat model

The method: STRIDE per component (Spoofing, Tampering, Repudiation,
Information disclosure, Denial of service, Elevation of privilege), ranked
by likelihood and impact, each threat mapped to the control that answers
it. This is the version one model; Phase 7 changes what the tool is
allowed to do and requires a revision before any of its code is written.

The premise that shapes everything here: role-call's database is a map of
every identity in the target account, which ones are unused, which ones
are over-privileged, and which credentials are old. That inventory is
exactly the reconnaissance an attacker wants, so the tool that reduces
identity risk is itself a concentration of it, and its own handling is the
core of the work.

**Contents:** [Components](#components) · [Ranked threats](#ranked-threats) · [Accepted risks](#accepted-risks)

-------------------------------------------------------------------------------

## Components

| Component | Role |
|---|---|
| Operator browser | The human's session; holds a login token |
| Application routes | The trust boundary every request passes through |
| Snapshot ingestion | The only untrusted input surface: API pulls and imported report files |
| Derivation engine | Computes status and enrichment from append-only observations |
| Inventory store (PostgreSQL) | Holds the identity map; encrypted at rest |
| Audit trail | Records every governance action, written with the action in one transaction |
| The tool's own cloud credential | A read-only role in the target Amazon Web Services (AWS) account, arriving with the live pull phases; the identity that must be governed best |

-------------------------------------------------------------------------------

## Ranked threats

Ordered by likelihood times impact. The STRIDE letter names the category.

| # | Threat | STRIDE | Likelihood | Impact | Control |
|---|---|---|---|---|---|
| 1 | Theft of role-call's own cloud credential, giving an attacker the full identity map and a foothold shaped like a security tool | S, I | Medium | High | Federated, short-lived credentials rather than a stored key; read-only scope; the role's own use is audited in the target account's trail, so the watcher is watched |
| 2 | Disclosure of the inventory: database access or a leaked export hands over the reconnaissance map | I | Medium | High | Authentication and authorization on every request; response models as an allowlist on the way out; exports carry deliberate fields only; encryption at rest supplied by the deployment layer and stated as a requirement, not assumed (D-020) |
| 3 | A hidden identity: tampering with stored data so an attacker's principal never appears in the inventory | T | Low | High | State is derived at read time from append-only observations, and every sync is a full snapshot, so hiding requires tampering again after every sync; database least privilege; the audit row commits with its action and carries attribution |
| 4 | A malicious imported snapshot rewrites another account's history or plants hostile values | T | Medium | Medium | Bounded parsing on every axis; the one-account-per-file precondition is verified rather than assumed; ingestion is append-only and duplicates are rejected |
| 5 | Stale data presents false comfort: a decision made on an inventory that no longer matches the account | I | Medium | Medium | Every view carries its as-of sync time; recency is a first-class field; an old sync is a visible warning, not a footnote |
| 6 | Theft of an operator session token | S | Medium | Medium | Sessions are revocable from day one; short expiry; step-up authentication arrives with any action that changes the cloud account |
| 7 | Injection through exported identity names and tags, which the target account's users control: formulas in spreadsheets, markup in the generated report | T | Medium | Medium | Formula-leading cells are escaped in every export path, and the report builder context-escapes every value, treating names and tags as data, never markup |
| 8 | A governance action is denied or misattributed: who attested this identity, who cleared this flag | R | Low | Medium | Attribution columns on the record itself, plus the audit row written in the same transaction as the action |
| 9 | Ingest exhaustion: an enormous account, or API throttling turning a sync into an outage | D | Medium | Low | Paced API calls that honor throttling; bounded imports; container resource caps |
| 10 | A shadow admin scored as low risk because its privilege is capability-shaped rather than name-shaped | I | Medium | Medium | Admin-equivalence heuristics judge what a policy can do, not what it is called; the chaining limitation below is stated rather than hidden |
| 11 | A deleted principal is recreated under its old name and inherits the dead identity's governance standing | S, T | Medium | Medium | Identities are keyed by the provider's immutable identifier (D-016), so a recreated principal is a new identity, and reuse of a governed name is surfaced as a finding |

-------------------------------------------------------------------------------

## Accepted risks

Recorded so each is a decision with a reason, not a surprise.

- **Effective privilege through role chaining is not computed.** Version
  one scores what a policy grants directly. A principal that reaches
  admin through a chain of assumable roles will be underscored, and the
  interface says so. Computing reachability is graph analysis that earns
  its own phase; the raw material for it, every trust policy document,
  is already recorded per snapshot as of the second ingestion surface,
  so the later phase starts from data, not from scratch. Two narrower
  limits join it with the privilege findings (D-033): an explicit deny
  is noticed but not evaluated against the allow it narrows, and a
  condition is noticed but not interpreted. Both can overstate a grant,
  and each finding resting on such a document says so in its own text
  rather than relying on a reader finding this paragraph.
- **Creator attribution is limited to the event history window.** Until
  the organization trail exists in Phase 3, "created by whom" reaches
  back 90 days and no further. The field says when its evidence starts.
- **Version one observes and records; it does not enforce.** An identity
  flagged in role-call keeps working in the cloud account until a human
  acts there. That is the enrichment-over-automation design, stated as a
  risk because a reader could mistake governance records for applied
  controls.
- **The audit trail is not yet tamper-evident.** The trail is atomic and
  attributed from the first commit, but an actor with database write
  access could still alter history. The exit is concrete: hash chaining
  arrives with the campaign work, anchored by the evidence exports,
  because a chain nobody anchors outside the database only detects
  casual tampering and would be a control in name. Until then this is
  the accepted gap, stated rather than implied.
- **Snapshot files are only as authentic as their handling.** The
  intended procedure, stated here until the runbook document exists to
  carry it, is exporting reports directly from the provider to the
  machine that imports them. A file that traveled through other hands in
  between is a risk the parser's bounds cannot remove, accepted and
  named.
- **Roles are global, not account-scoped.** Any operator sees every
  imported account. Right-sized for one team governing its own accounts;
  account-scoped authorization is the named prerequisite for any
  multi-tenant future, decided before that future starts. The sharpest
  consequence, a stolen token reading every account for its whole
  lifetime, gets its mitigation with user management's completion: an
  administrator surface that revokes any user's sessions on demand.
- **Single author, no second review of changes.** Every change lands
  through a pull request that must pass the required checks before
  merging, and main refuses direct pushes, force pushes, and deletion
  (D-028). What remains accepted is the absence of a second human:
  approvals are not required because there is nobody to give one, and
  pretending otherwise would be theater. The exit condition is the
  first collaborator, when required approvals join the required
  checks.
- **The tool depends on the provider's own reporting.** If the account's
  telemetry is wrong or delayed, the inventory inherits that. Verifying
  the provider against itself is out of scope.
