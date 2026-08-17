# Decisions

What was chosen, what was rejected, and why. Risk acceptance lives here.
Decisions are numbered in the order they were made and are never renumbered.

-------------------------------------------------------------------------------

## D-001: AWS identity first, then possibly Okta, then Entra

The first supported identity provider is Amazon Web Services (AWS):
Identity and Access Management (IAM) users and their access keys, roles and
their trust relationships, instance profiles, federated principals, and
Identity Center assignments.

Entra was rejected as the starting provider despite being the author's
deepest platform. The AWS identity model is where the largest population of
ungoverned non-human identities lives in practice, the enrichment sources
are unusually good (the credential report, access advisor data, Access
Analyzer findings, CloudTrail history), and building against AWS exercises
the platform this project is meant to deepen. Additional providers join
behind a common identity model rather than as separate code paths, which is
why the order is a roadmap entry and not a rewrite.

## D-002: TruffleHog for secret scanning, in two modes

This repository uses TruffleHog as its secret scanner: as a pre-commit hook
with verification disabled, so the commit-time check is fast and fully
offline, and in continuous integration with verification enabled, where a
finding is checked against the credential's provider to learn whether it is
live.

gitleaks was rejected for this repository, though it remains in use
elsewhere. The difference that decides it: this project is developed against
live cloud accounts, so a credential that reaches a commit here could be a
real one, and the question that matters in that moment is whether it still
works. Verification answers that; detection alone does not. One tool in two
modes also means one configuration and one allowlist format instead of two.

The accepted cost: verification in continuous integration makes outbound
calls to credential providers, and testing a candidate can appear in the
provider's logs as a failed authentication. That trade is taken knowingly,
because the answer it buys ("rotate now" versus "stale example") is the
whole point.

## D-003: The repository starts private, with the public flip as a gate

The repository is private during design and early build, and goes public
only after a full read of every file and the whole history, while the
history is still small enough to read completely. Before the flip, two
things must exist: a LICENSE file chosen deliberately (Apache License 2.0
is the working intent, recorded as final only at the flip), and a
SECURITY.md with a private vulnerability reporting path.

Building in public from the first commit was rejected because early design
documents churn, and a public history of half-formed decisions serves no
reader. Staying private indefinitely was rejected because the finished
design is meant to be read.

## D-004: Design before code

Phase 0 produces architecture, a threat model, a roadmap, and this decision
record, and no application code. Writing code first was rejected for the
same reason it always is: design is the cheapest place to fix anything, and
a schema chosen well makes the hard requirements structural instead of
procedural.

## D-005: Enrichment over automation

The product amplifies a human decision; it does not act on its own. Version
one holds a read-only credential and writes nothing to the cloud account.
Human-triggered actions arrive only in a late phase, each reversible where
the platform allows, shown as a diff before it happens, and verified
against the provider afterward. Automated remediation was rejected
permanently: a tool that revokes on its own gets disabled the first time it
breaks something, and a tool that never asks for trust it has not earned
keeps its own threat model small.

## D-006: Ingestion is append-only and state is derived, never stored

Each sync records what was observed. An identity's state is computed from
the observations at read time, so re-imports are harmless, out-of-order
syncs self-correct, and there is no stored status column to drift from
reality. Mutate-on-ingest designs were rejected because a stored security
status that can drift is worse than none: people trust it. This structure
was proven in an earlier build and is the core of this one.

## D-007: The stack is Python, FastAPI, and PostgreSQL under Docker Compose

Typed request validation at the boundary, a real database service as the
honest shape of a composed deliverable, and database access only through
the object-relational mapper (ORM), which parameterizes every query and
removes injection as a class rather than defending it query by query.
SQLite was rejected for the deliverable because the runnable stack is the
product. Raw SQL anywhere was rejected outright.

## D-008: The ingestion surface distrusts even its own preconditions

Imported snapshots are bounded on every axis, parsed in memory, and never
written to disk. The file's content is authoritative and its name is not,
because a filename is client-supplied. A file claiming to cover one account
is verified to cover one account rather than trusted. A timestamp with an
unrecognised timezone is rejected rather than guessed, because sync
timestamps order the history and therefore decide what counts as current.
Each of these rules exists because the assumption it replaces is exactly
what a malicious file would exploit.

## D-009: Keys and startup are strict

Two keys with two lifetimes, the session signer and the data encryption
key, generated independently and never derived from each other, so rotating
one never silently changes the other. No defaults ship for either: the
application refuses to start with a missing or malformed key and prints the
command that generates a valid one. Bootstrap is idempotent with the
environment as the source of truth, so changing the configured credential
and restarting always converges instead of locking an operator out.

## D-010: Output is an allowlist at every exit

Every response declares a response model, so what a client can see is
defined by schema rather than by what a row contains. Sensitive
identifiers are masked in list views, and any full reveal is a dedicated,
audited event. Client errors are generic, including a custom validation
handler so a rejected value is never echoed back. Logs serialize an
explicit field allowlist carrying identifiers, never values. Exports
escape formula-leading cells so a spreadsheet cannot execute
attacker-influenced content. There is no cross-origin configuration on
purpose, and the interactive documentation page is a recorded decision
either way, because concealing an API's shape is not a control.

## D-011: The audit row commits with the action, and records who

Any action that changes governance state writes its audit row in the same
transaction, so no action can exist without its record; an audit write
failure fails the action, integrity chosen over availability for the
trail. Records that change state also carry their own attribution columns,
so a row answers who did this without a join. Best-effort trails were
rejected: a gap between action and record is exactly where an investigation
dies.

## D-012: Sessions are revocable from day one

Whatever the session mechanism, one stolen credential can be ended without
ending every session. Stateless-only tokens were rejected because expiry
without revocation leaves only the option of rotating the signing key and
logging everyone out, which in practice means nobody does it.

## D-013: Migrations from the first table, data rights only for the app

The schema is created and changed by versioned migrations run as a
privileged role, never by the application at startup. The application's
database role has data rights only, so an injection flaw, however
unlikely the ORM makes one, could not modify the schema. Create-all at
startup was rejected because it cannot evolve a database that already
holds data, and because it forces the application to hold schema rights it
should never have. These two decisions come as a pair.

## D-014: The interface is REST, not GraphQL

Each endpoint is one operation with one explicit authorization check, so
the authorization surface stays countable and testable. GraphQL was
rejected because it spreads authorization across a query graph, which is
where authorization mistakes hide.

## D-015: Version one scope is four operations, files in, reports out

Confirmed scope: an operator authenticates; a snapshot file is imported,
append-only; the enriched inventory is viewed and can produce a
self-contained risk report plus escaped CSV and JSON exports; governance
(owner, flag, attestation) is recorded in role-call only.

Two sub-decisions carry the reasoning. Ingestion is file import only in
version one, because the fresh-clone demo must run with Docker alone and
nothing else, and everything runs locally before it runs in the cloud; the
live read-only pull joins in the cloud phases as an adapter behind the
same ingestion. The report ships in version one rather than later because
a self-contained risk artifact is how this class of findings actually
travels between people, a pattern proven publicly by Cloudsplaining, and
the fields it needs already exist in the inventory view. A live pull in
version one was rejected; a view-only version one was rejected.

## D-016: An identity is keyed by the provider's immutable identifier

In AWS, a deleted principal can be recreated under its old name, and the
new principal carries the old name and Amazon Resource Name (ARN) with a
fresh immutable unique identifier underneath. Keying identities by name or
ARN would therefore let a recreated principal inherit a dead identity's
governance standing: its owner, its flags, its attestation history, its
reviewed-last-quarter credibility. So an identity is keyed by the account
plus the provider's immutable identifier; names and ARNs are display
attributes. A recreated principal is a new identity, and the reuse of a
governed name is itself surfaced as a finding, because resurrection is
exactly the move an attacker inside the account would make. Keying by ARN
was rejected for that reason.

## D-017: Three roles from the first commit

Version one ships three roles: a viewer reads the inventory and reports,
an operator imports snapshots and performs governance actions, and an
administrator manages accounts and users. A single role was rejected
because a governance tool's audit trail is only meaningful when the person
who views a finding and the person who attests it can differ, and because
an earlier build documented the one-role gap honestly rather than fixing
it; this build starts past it. Authorization failures return 403 and are
distinct from authentication failures from the first commit. Sample users
for each role ship with the demo data.

## D-018: Local sign-in first, single sign-on at the cloud phases

Version one authenticates against local credentials: passwords hashed with
bcrypt, verification that costs the same whether the account exists or not
(a dummy comparison for unknown names, so response timing cannot enumerate
accounts), and a stated byte-length cap ahead of the hash. Local-first
follows the same reasoning as file-first ingestion: a stranger with only
Docker must be able to run the demo, and single sign-on requires an
identity provider the fresh clone does not have. Single sign-on (OpenID
Connect) joins at the cloud phases, and the local login then becomes a
break-glass path. A single-sign-on-only version one was rejected.

## D-019: Identities act, privilege sources grant, and both are governed

The model holds two governable kinds. Identities (users, roles, the root
account) can act: they authenticate, hold credentials, and carry liveness
enrichment. Privilege sources (groups now, and policies as they earn it)
cannot act but grant: they carry membership, policy, and privilege
enrichment instead. Governance records, meaning owners, flags, and
attestations, attach to both, because access review in practice certifies
group memberships as much as it certifies actors, and the remediation for
an over-privileged member is usually a change to the group, so the
group must be first class for the fix to be trackable.

Consequences built in from the start: every privilege in an identity's
summary names its source, direct or through which group; membership is
observed per snapshot, so a member appearing in a privileged group
between snapshots is a finding; an empty privileged group and an unowned
privileged group are both findings on the group itself; and groups never
appear in the identity inventory pretending to be actors.

Two alternatives were rejected. Treating groups as identities blurs what
acting means and hangs liveness questions on things that cannot log in.
Treating groups as mere policy carriers, attributable but not governable,
was this decision's own first draft, rejected because it could not hold
an owner or an attestation for the object where real access reviews
actually happen.

## D-020: Encryption at rest is the deployment layer's job, stated

role-call stores no secrets: no credential values, no tokens, nothing
whose disclosure is worse than the inventory itself. Field-level
encryption of the stored policy documents was considered and rejected: it
adds key management and rotation burden to protect documents that any
reader of the target account can already fetch, which is cost without
commensurate gain. The inventory's confidentiality controls are
authentication and authorization on every request, the egress allowlists,
and encrypted storage at the deployment layer (the disk and the database
service), which the runbook states as a deployment requirement rather
than assuming. If a future field ever carries a secret, this decision is
revisited before that field exists.

<!-- vale BuildGuidelines.Audience = NO -->
<!-- Scoped exception: "reviewer" below names the product's user, the
     person who performs an access review, which is the standard term in
     every framework this work follows. It does not describe this
     document's audience, which is what the rule exists to prevent. -->
## D-021: Version one gains the review campaign, shaped by the reviewer

The published codifications of this work (PCI DSS 4.0 requirements 7.2.4
and 7.2.5, ISO/IEC 27002 5.18, NIST AC-2 and AC-6(7), CIS Control 5, and
the audit practice around SOX and SOC 2; see COMPLIANCE.md) all define
the unit of governance as a periodic, scoped, evidenced review. Version
one therefore adds, on top of the four confirmed operations: review
campaigns (a scope of identities and groups, assigned reviewers, a due
date, item-level progress, and a close); a purpose governance record,
answering the reviewer's first question, what is this for; the delta
view, what changed since the last certification, computed from snapshot
differences; a recommended disposition per item with its evidence stated;
and a per-campaign evidence export carrying the population statement,
every decision, its actor, and its time.

Review dispositions include "insufficient evidence," with the reviewer
saying what was missing. That is a first-class outcome, not a skipped
row: it appears in the campaign report, and the rollup of what reviewers
found missing steers what the product adds next.

On scheduling, considered rather than assumed: real programs run
quarterly and semiannual big-bang campaigns under SOX and PCI, annual
recertification under federal regimes, and risk-based frequencies for
system accounts. Version one gives a campaign a due date and an optional
recurrence preset (quarterly, twice yearly, yearly), and completion over
time is inherent because items are decided individually while the
campaign tracks progress. Rejected for version one: arbitrary schedule
configuration, which is maintenance surface without a named user, and
rolling event-triggered micro-reviews, which are a real modern practice
that deserves its own later decision once campaigns exist to hang it on.
Auto-applied decisions are rejected permanently here as they were in
D-005.

This decision also names the method it came from: the design phase takes
the reviewer's and the auditor's itemized needs as first-class inputs
beside the threat model, user first and security first together, and the
framework references run in both directions through COMPLIANCE.md.
<!-- vale BuildGuidelines.Audience = YES -->
