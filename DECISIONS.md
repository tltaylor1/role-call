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

## D-022: Ruff is the linter, and commented-out code is a finding

Ruff was vetted at build time as subphase 1.1 planned: one binary, no
plugin tree to audit, active maintenance, and rule families that cover
correctness, import order, known bug patterns, outdated idioms, and
security checks. The deciding rule family is ERA, which flags
commented-out code. The standards already forbid deferred-work markers;
commented-out code is the same debt wearing a disguise, and now a gate
catches it instead of a human eye. The alternative, flake8 with
plugins, spreads the same coverage across a half-dozen separately
maintained packages, which is more supply chain for the same result.
Formatting is not enforced in version one: a formatter is a one-line
addition later, and the linter is the part with security value.

## D-023: One tool audits the tree and writes the bill of materials

pip-audit both checks the pinned dependency tree against known
vulnerability databases and emits the software bill of materials in
CycloneDX form. One vetted tool, two supply-chain artifacts. The bill of
materials is generated fresh by continuous integration on every run and
published as a build artifact rather than committed, so it can never
drift from the requirements file it describes; the requirements file
with its hashes remains the single tracked source of truth. The
alternative, a dedicated generator beside a dedicated auditor, is a
second tool to vet and pin for no additional information.

## D-024: The machine never decides

The automation doctrine, named after living implicitly in D-005 and
D-021. Automation in role-call carries out what a person already
decided, inside bounds that person set: a review window that closes on
its own schedule, an approved re-elevation the clock takes back, a
drafted right-sizing change waiting as a diff for an owner to approve.
Automation prepares, schedules, executes, and verifies. It does not
grant, revoke, or certify on its own judgment, and every automated
action traces to the person who decided it and the bounds they chose.

This replaces the blanket phrase "never automation," which was both
stronger than the recorded decisions and contradicted by the design
itself, whose re-elevation expiry is a machine revoking access
legitimately. The line that matters is not whether the machine acts
but whether it decides. D-005's choice of enrichment over automation
and D-021's permanent rejection of auto-applied certification
decisions both stand; this decision names the boundary they were
circling.

## D-025: The pipeline guards itself

One deliberate batch, five tools, each doing for the pipeline and the
documents what the earlier gates do for the code. CodeQL runs deep
static analysis on the application and on the workflows themselves,
weekly as well as per push, so a new query pack finds old code.
actionlint lints the workflow files; zizmor audits them for the
security mistakes workflows invite, and both ran against this
repository before they were adopted, which is the vetting. The OpenSSF
Scorecard rates the repository's own posture and publishes the result,
so the score is checkable rather than claimed, and its check list is a
standing audit of practices not yet adopted. lychee checks the
cross-references between documents, offline, fetching nothing.

Provenance, stated: CodeQL and Scorecard run as actions pinned by
commit hash, from GitHub and the OpenSSF respectively. actionlint and
lychee are single binaries verified against their published checksums.
zizmor publishes no checksum, so its pin is the hash of the artifact
inspected at adoption; a changed artifact fails the pipeline. Every
binary added to the pipeline widens the set of pins nothing watches
for staleness, which is a recorded cost, carried knowingly.

## D-026: Sessions are opaque rows, and the database never holds a token

A signed stateless token (a JSON Web Token) was considered and
rejected for version one: statelessness buys horizontal scale this
deployment does not have, and it costs the one property a governance
tool cannot give up, the ability to revoke one session now and know it
is dead. Sessions are rows: an opaque 256-bit random token goes to the
client, and the database stores only its SHA-256, so a database leak
yields nothing a client can present. Plain hashing is correct here
where it would be wrong for passwords, because the values are random
and cannot be guessed offline. Expiry is absolute from sign-in rather
than sliding: a stolen token dies on schedule no matter how actively
it is used. The cost, one database read per authenticated request, is
the right trade at this scale.

## D-027: The sign-in rate limiter is forty lines we own

The library route (slowapi wrapping limits) was vetted and declined:
two more supply-chain entries, storage backends and decorators this
application does not need, for one policy on one route. The hand-rolled
limiter counts failures per username and per client address over a
sliding window; success clears the username key so a user who finally
types the right password is not locked behind their own mistakes, and
deliberately does not clear the address key, so a valid login cannot
refill an attacker's allowance. Failures are limited, accounts are
never locked, because lockout hands an attacker denial of service
against any username they can spell. State lives in process memory,
which is stated plainly: version one deploys as one process, a restart
clears the counters, and the control's job is slowing online guessing,
not surviving restarts. Forwarded-for headers are not consulted; they
are attacker-writable, and the deployment layer owns address
translation when it arrives.

## D-028: Every change lands through a pull request

The method change, adopted at the start of subphase 1.3: work happens
on a branch, the subphase's pull request carries the review evidence,
the required checks must pass, and the merge is the review's public
receipt. Main now refuses direct pushes outright, alongside the
existing force-push and deletion blocks, so the review gate that
previously ran invisibly on one machine is enforced by the server and
visible to any reader.

What is deliberately absent: required approvals. One person cannot
review their own work in any meaningful sense, and a self-approval
dressed up as review would be the exact theater this project refuses.
The controls are the checks and the deliberate merge; the accepted
risk in the threat model narrows from "direct pushes on trust" to
"no second review of changes," with the first collaborator as the
exit condition. Merges are plain merge commits, never squashes, because
the small-commit history is the record and flattening it would
destroy what review reads.

Dependabot's update pull requests flow through the same gate, which
also means the update path is now check-gated by construction.

## D-029: What the credential report cannot say, and what stands in

Verified against the provider's documentation at build time, the
credential report's content carries neither a generation timestamp nor
any immutable unique identifier. Two rules follow.

Capture time is operator-attested. The enumeration wanted it from file
content, and for this file that is impossible; inferring it from the
newest timestamp inside the report was rejected because a quiet account
would date its snapshot days early and staleness math would lie.
The operator supplies the capture time at import, it must carry a
timezone and must not be in the future, and it is content-authoritative
wherever content exists: the account number still comes only from the
rows themselves.

Identity keys from this file are provisional. D-016 forbids keying by
name or ARN because a recreated principal inherits both; the only
immutable content available is the ARN paired with the user's creation
time, which a recreated principal cannot reproduce. The provisional key
hashes that pair, the identity row says provisional plainly, and the
authorization details import upgrades it to the provider's real
identifier by matching the same pair. Resurrection still mints a new
identity, which is the property D-016 exists to keep.

## D-031: Status claims are gated, with the journey diagram as the source

A session review found the public documents materially stale: the
roadmap still said the design phase was in progress and no application
code existed, the security document said the application did not exist
while listing five built controls as planned, and the front door
undercounted the merged subphases. The failure was structural: the
subphase-close ritual covered the diagrams and the repository
description but never the document set, and a figure that lives in
several files drifts, which is the same disease the derive-don't-store
rule treats in data.

The mechanism: the journey diagram is the single source for the build
status figure, because the close ritual already moves it. A pipeline
and pre-commit check reads the figure there and fails when the front
door or the roadmap disagree, and it forbids outright the specific
claims that sat false in public, so those sentences can never return.
Prose accuracy beyond the figures stays with the close ritual, which
now names the document set explicitly; the gate holds the numbers, the
ritual holds the words.
## D-030: The authorization details file, taken at its word and no further

Four rules from the build-time verification of the provider's
documentation. A true IsTruncated flag rejects the whole file: a
truncated export is an incomplete snapshot, and importing it would
record absences that are artifacts of pagination, the exact false
comfort D-006 exists to prevent. Policy documents arrive URL-encoded
and are decoded before parsing, bounded, with pre-decoded objects
accepted from exporters that already did the work. A user's group list
carries names, not identifiers, so membership resolves against the
groups named in the same file and is recorded as observed identifiers
on the group's observation. Provider-managed policies carry the
literal account "aws" in their identifiers and are exempt from the
one-account claim, recorded with an aws-managed flag; every other
identifier in the file must agree on one account or the file is
rejected whole.

The stored take: only the default version of each managed policy's
document is kept per snapshot, because that is the version in force,
and the findings this feeds (1.6) judge what is in force, not what is
drafted.

## D-032: Findings explain themselves, in three tiers, on a watched clock

The credential findings arrive with the derivation engine, and three
choices shape them. Tiers are the triage order a human works in,
critical, warning, notice, because severity taxonomies with more
levels than a person has attention produce sorting, not action. The
minimum observation age gates the unused finding: an identity is not
flaggable as unused until it has been watched fourteen days, because a
new key that has not been used yet is new, not stale, and the false
positive that cries wolf on day one costs the tool its credibility
(the eligibility lesson from the prior art, credited in
ACKNOWLEDGEMENTS.md). Staleness is always computed against the
account's newest snapshot capture time, never the wall clock, so an
old import shows its age instead of silently accruing findings.

Every finding carries its OWASP Non-Human Identities Top 10 identifier
and an explanation containing the numbers that triggered it, because a
finding that cannot explain itself is an accusation, and the review
these findings feed runs on evidence.

## D-033: Privilege read by capability, attributed, and honest about limits

The judgment subphase, and three choices carry it.

Detection is capability-shaped, never name-shaped. A policy called
ReadOnly that can rewrite its own default version is administrator
access; a policy called FullAdminLegacy granting three read actions is
not. The heuristics read what a document permits: every action on every
resource, the wildcard breadth underneath that, identity-mutating
operations, and the escalation combinations from the published research
credited in ACKNOWLEDGEMENTS.md, including the pair where passing a role
into a compute service is ordinary on either side and an escalation
together. The escalation finding is reported only for identities that
are not already administrators, because an administrator reaches every
path by definition and listing them there buries the finding that
matters: the principal nobody calls an administrator that can become
one.

Every capability names its source. "This account is over-privileged" is
an accusation; "this account holds administrator access through the
automation group, and can rewrite its own policy through an inline
policy it holds directly" is something a human can act on. Inline
policies are stored and attributed by the provider's immutable
identifier rather than by name or address (D-016), because two
identities share an address during a resurrection window and the dead
one must not inherit the live one's privilege.

The limits ride with the claims rather than living in a footnote.
Version one reads grants, not effective permissions: an explicit deny
is noticed and not evaluated against the allow it narrows, a condition
is noticed and not interpreted, and privilege reachable by assuming
another role is not computed at all. Each finding that rests on a
document carrying a deny or a condition says so in its own text. The
consequence is stated once here and inherited everywhere: this reading
can overstate a grant that a deny or condition narrows, and it
understates anything reachable through a chain.

Tuning is part of the design, not a later polish. Wildcards over read
operations are separated from wildcards that can change things, because
the provider's own read-only policies grant read wildcards on every
resource, and scoring those like write access is exactly how a tool
earns the reputation that gets it muted.

## D-034: The plan mixes three methods, and one of them was misapplied

The subphase decomposition was never written against a single named
method, and the question of which one it followed is fair, so the
answer is recorded rather than left implied.

Three methods are in the plan, deliberately. The first subphase is a
walking skeleton: the thinnest end-to-end thread through container,
database, migrations, configuration, logging, and a served route, so
the architecture is proven before anything is built on it. Everything
after it is dependency-ordered layering: identity before data because
every route needs the role checks, parsers before the engine because
reading real data before designing against it is the lesson this
project inherited, credential findings before privilege findings
because the second carries judgment. Two constraints ride on top:
every subphase must end in something that runs and can be shown, and
controls arrive with the thing they protect, which is why there is no
hardening phase.

Vertical slicing, the dominant modern prescription, was not used, and
the cost is real: five consecutive subphases produced no surface a
person could click. The reasons for the choice are that the record is
the deliverable here rather than a shippable increment, that a solo
build has none of the cross-team integration risk vertical slicing
exists to reduce, and that layered order produces cleaner review
boundaries and cleaner decision entries. The mitigation is that every
subphase ends demonstrable through the interface that exists at the
time, which for the middle subphases meant the documented API rather
than a screen. An engineer who prefers slices would push
here, and the push would be fair.

Risk-driven sequencing was also inverted on purpose. The judgment-heavy
work sat sixth rather than first, because the risk retired earliest was
the shape of the real data, and heuristics designed against imagined
data would have been rewritten anyway.

Where the ordering was wrong: sample data. The synthetic generator sat
eleventh while every subphase from the first parser onward needed demo
input, and input made by hand was wrong three separate times, each
caught by the system rather than by its author. The generator moves to
seventh, ahead of the frontend, so the remaining subphases demonstrate
against realistic data. The stranger drill it used to share a subphase
with stays at the end, inside the proof, because a fresh-clone run of
the finished demo cannot happen before the demo is finished. The count
stays at twelve, so the status figures and their gate stay valid, and
the earlier subphases keep the numbers their transcripts already cite.

## D-035: The sample account is generated, committed, and checked

The demonstration data is produced by code in the repository, shipped
as files beside it, and guarded by a test that regenerates and compares.
Each of those three exists for a reason.

Generated, because input made by hand was wrong three times in three
subphases: an invented creation time, a false finding produced by that
same mismatch, and a capture time dated in the future. The system
caught all three and the author caught none, which is the argument for
deriving fixtures rather than typing them.

Committed, because a stranger with only Docker should not have to run a
generator before seeing anything, and because files in the repository
are readable in a browser by someone deciding whether to clone.

Checked, because those two choices together are exactly the drift the
derive-don't-store rule exists to prevent, and the answer is the
one-source pattern the role matrix already uses: the generator is the
source, the files are its output, and a test fails the build if they
disagree.

The generator is deterministic and refers to no clock: three fixed
snapshot generations a month apart, every date a literal. That is only
possible because staleness is measured against a snapshot's capture
time rather than the wall clock (D-006), so the sample stays meaningful
without maintenance, and it is what lets the comparison test exist at
all.

Completeness is the property that matters most and is asserted rather
than hoped: a test imports the shipped files and fails unless every
finding the engine can produce appears, because a demonstration that
exercises half the rules teaches a reader that the other half are
decorative. Two identities are deliberately quiet for the same reason:
a tool that finds something everywhere has found nothing.

## D-036: The page renders text, holds its token in memory, and ships plain

Three choices, and the first is the security control this subphase
exists to install.

Every value the page displays is written through the document's text
interface, never through a markup sink. Identity names, tags, and
policy text all arrive from imported files, which makes them attacker
content by definition, and the answer is structural rather than
vigilant: the page contains no sink for markup to reach, so escaping
is not something a future edit can forget. A test scans the script for
those sinks and fails the build if one appears, which turns the
promise into a gate; the content policy forbids inline script and
style, and a second test proves the page needs neither, so the policy
can stay strict. Values are never sanitised on the way in or out,
because a tool that quietly rewrites what it found has started lying
about what it found; the hostile name is stored exactly, displayed
exactly, and displayed as text.

The session token lives in a closure variable and never in browser
storage. The cost is real and accepted: a refresh signs the operator
out. The benefit is that the token is not sitting in a place any
future script can read, and this application's whole subject is
credentials that outlive their purpose.

No build step, no framework, no package manager for the page. The
stated cost of the alternative is a second toolchain to pin, audit,
and keep current beside the Python one, for a page that renders tables.
The stated cost of this choice is that the page will stay plain, which
is acceptable while the questions this tool answers, not the interface
it answers them through, are what the project is about.

## D-037: The posture score publishes, and stays out of code scanning

The scorecard's findings were being uploaded into code scanning, where
they became pull request alerts. The consequence showed up on the
first pull request after the frontend landed: a check reporting a high
severity security alert, which turned out to be the repository having
no second person reviewing changes and no fuzzing subphase yet. Both are recorded
accepted risks. Neither is a defect in the change under review, and no
pull request can fix either.

A gate that fails on findings the change cannot address is the alarm
that is always red, and this project already refuses that pattern
where scanners are concerned. So the score keeps publishing, where it
is read from the public scorecard and cited in the security document,
and nothing is written into code scanning. The five alerts already
sitting there were dismissed with that reason recorded on each.

The tool keeps its scoped permission for publishing and loses the one
that wrote findings, which is least privilege applied to a workflow
after learning what it actually needs.

Two smaller pipeline decisions ride with it, both from the same run.
Tool downloads retry, because a reset connection is a network event
and not a build result. And the checks workflow runs on pull requests
and on main rather than on every branch push, with a concurrency
group, because the duplicate run taught nothing and doubled the
exposure to exactly the network blip that failed this one.

## D-038: The owner is typed, and teams are the default

Governance records arrive as an append-only human layer: owner,
purpose, flag, and attestation, on identities and groups, each record
attributed to the person who wrote it and closed rather than edited
when it is superseded or cleared, which is the observation model
applied to human statements.

The owner is not a string. It carries a type: team, business unit,
individual, vendor, or unknown. The reasoning starts from this tool's
own opening finding. An individual owner is the orphan in waiting: the
person leaves, nothing in the provider changes, and the identity keeps
its keys and its privilege with nobody accountable, which is improper
offboarding, the finding class the engine leads with. A tool that
encourages individual ownership manufactures its own top finding, so
the interface and the documentation treat a team as the normal answer.
An individual owner on a privileged identity is reported as a notice
that states the exposure and leaves the judgment to the reader.

Review practice still wants a named person who signed. That need is
met without giving up the durable owner, because the two were never
the same thing: the owner is who answers for the identity over time,
and the attestor is who looked on a given date, which the attestation
record and the audit row already capture with attribution.

An assigned owner outranks the owner tag, because the assignment is
the deliberate human input this table exists to hold, while the tag is
an observation like every other imported field. The unowned finding is
answered by an assignment, which makes it clearable inside role-call
rather than only by re-tagging the provider. A disagreement between
the assigned owner and the tag is surfaced as its own notice naming
both values, because a silent winner would hide exactly the staleness
a governance tool exists to show.

The rejected shape is the three-field enterprise answer: cost centre,
application identifier, and engineering team. They answer different
questions and real organizations track all three, but with no
directory or configuration source to validate against, three free-text
fields are three fields of typos. One typed field now, and the split
becomes worth revisiting when an integration arrives that can validate
at least one of them.

<!-- vale BuildGuidelines.Audience = NO -->
<!-- Scoped exception: "reviewer" below names the product's role, the
     person who performs an access review inside the application. It
     does not describe this document's audience. -->
Attestation is open to all three roles, while owner, purpose, and flag
writes stay with the operator and administrator, because stating "I
looked at this and it is still needed" is exactly the reviewer's act,
and changing who answers for an identity is not.
<!-- vale BuildGuidelines.Audience = YES -->

<!-- vale BuildGuidelines.Audience = NO -->
<!-- Scoped exception: "reviewer" below names the product's role, the
     person performing the access review inside the application. It
     does not describe this document's audience. -->
## D-039: The campaign freezes its population, and nobody certifies in bulk

A review campaign resolves its scope into items once, at creation,
with each item carrying the evidence as it stood: the findings, the
owner, the privilege sources, the liveness. The population statement
in the evidence export describes that frozen set, which is what makes
it a statement rather than a moving target.

Every disposition is one item, decided by one person, recorded with
attribution and its audit row in the same transaction. There is no
operation anywhere in the application that disposes more than one
item, because a certification records that someone looked at that
identity, and a button that certifies a hundred rows records that
nobody did. A decision is final within its campaign; a changed mind is
the next campaign's decision, which keeps the record honest about what
was believed when.

Insufficient evidence is a first-class answer that must name what was
missing, and the rollup collects those notes across campaigns: one
recurring line is a reviewer's problem, the same line across a column
is the program's problem. Close refuses while any item is undecided,
because an access review with gaps is a false population statement.
Recurrence is a preset the next cycle is created from by a person;
the machine recommends with reasons and never decides (D-005).

The engine's recommendation order is deliberate: too little
observation history outranks everything, because a verdict built on
four days of watching is a guess wearing a verdict; then revocation
signals; then the tier weight; then the quiet default.

## D-040: The report renders through an engine that escapes by default

The risk report is a single self-contained file, built to be opened
from disk years later, which means it runs with no content security
policy and no server headers: whatever is in the file is what
executes. So the report is built by a template engine that escapes
every interpolated value by default, contains no script element at
all, and inlines its styles in the one file.

The engine is Jinja2, vetted at adoption: maintained by the Pallets
project alongside the framework family this application already
trusts, pinned by hash like every dependency, with automatic escaping
selected explicitly rather than assumed. The alternative was
hand-escaping each interpolation in string-built HTML, which is the
pattern where one forgotten call reintroduces the class; the engine
removes the class the way the ORM removes query injection.

The other two exits get the escaping their format needs. CSV cells
that begin with a formula character are prefixed so a spreadsheet
reads them as text, because identity names and tags are controlled by
the observed account's users and a name that starts with an equals
sign is a program. JSON is exported raw, because JSON is data and its
consumers parse rather than interpret; escaping it would corrupt the
values auditors compare against the provider.

## D-041: The proof subphase, and what its checks are allowed to block on

The last subphase is the one that proves the others, and each of its
mechanisms records what it may block a merge on, because a gate that
is always red teaches the eye to skip it (the D-037 lesson, applied
in advance).

The coverage floor is 90, set under the measured 94 at adoption: it
catches erosion without inviting tests written to move a number. The
mutation check is a fixed, reviewed set of seven mutations, each
removing one named control and requiring the tests that claim that
control to fail; fixed rather than generated, so the kill list is
readable in one screen and the check runs in minutes. Generated
mutation sweeps stay a local exploration tool. The check earned its
place on its first run by surviving a broken token hash: nothing
proved a fabricated token was rejected, and now a test does.

The container file is linted, and the base image's operating system
packages are scanned with a deliberate split: the merge blocks only on
critical findings that have fixes, because there the fix is moving the
digest, which a pull request can do. Findings without fixes are
reported for the record; failing on them would be an alarm nothing in
this repository can answer. Adopting the scan surfaced that the pinned
base was months behind its rebuilds, and the digest moved in the same
change, which is the scan doing its job before it was even merged.

The request budget: uploads were already bounded in memory, the
keep-alive timeout is now stated in the serve command, and imports and
campaign creation carry a per-user write budget of thirty per minute,
far above any human pace and below any useful abuse. State for that
budget is process memory, the same stated limitation as the login
limiter (D-027).

The route surface is now a documented enumeration asserted against the
live route table in both directions. Adding that assertion exposed
that the framework had begun wrapping included routers lazily, which
had quietly made the existing drift test vacuous: it was checking
three routes and passing. The flattened enumeration carries a count
canary so the next framework change fails loudly instead of passing
silently, and the incident is the strongest argument this subphase
will make for asserting what a test actually sees.
<!-- vale BuildGuidelines.Audience = YES -->
