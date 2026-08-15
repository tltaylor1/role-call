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
