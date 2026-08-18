# role-call

An inventory and governance tool for non-human identities: the roles,
service accounts, and access keys that get created, granted permissions
once, and forgotten. They outnumber the humans in most cloud accounts,
and nobody offboards them.

role-call imports identity snapshots, derives each identity's state from
the observed history rather than storing a status that can drift, and
gives each identity what a human needs before acting: an owner, when it
was last used, how old its credentials are, how much privilege it holds
and where that privilege comes from, and whether a governed name has been
quietly recreated. The full comparison of granted against exercised
permissions arrives with the live provider connection.
The tool amplifies a human decision; it does not act on its own.

It starts with Amazon Web Services (AWS) identity.

## The vision

Human accounts in a regulated company have a lifecycle: created for a
named person, owned, reviewed on a schedule, and disabled at departure.
The identities software uses have none of that, and they outnumber the
humans many times over. The destination for role-call is a tool where
every non-human identity is governed the way human accounts already
are: a named owner, a stated purpose, a privilege picture beside its
actual usage, a next review date, and evidence behind every one of
those claims, so that the identity nobody can explain becomes visible
the day it appears rather than the day it is abused.

The operating principle is that people decide and the machine never
does. Automation carries out what a person already decided, inside
bounds that person set: a review window that closes on its own
schedule, an approved re-elevation that the clock takes back, a
drafted right-sizing change waiting as a diff for an owner to approve.
Automation prepares, schedules, executes, and verifies. It does not
grant, revoke, or certify on its own judgment, and every action it
carries out traces to the person who decided it.

## Status

**Phase 1 of 8: building, subphase 1.1 of 12 complete.** The
foundation runs: a fresh clone with Docker starts the stack, migrates
the schema, and answers on its health routes. The design documents
below govern the build, and [BUILD-PLAN.md](BUILD-PLAN.md) sets the
subphases. [ROADMAP.md](ROADMAP.md) always states the current phase.

This is a learning project, built in public, by one person. The software
is provided as is under the [Apache 2.0 license](LICENSE). Before relying
on any of it, read the code and the
[threat model](THREAT-MODEL.md), including its accepted risks. Nothing
here is production software until the documents say so.

The build is review-gated on purpose: [BUILD-PLAN.md](BUILD-PLAN.md) sets
the subphases and their order before any code, and
[AI-USAGE.md](AI-USAGE.md) keeps the record of what the coding
agent got wrong along the way, because that record is the point.

## What version one will do

Four operations, and nothing else:

- An operator authenticates, into one of three roles.
- An identity snapshot file is imported, recorded append-only, with
  synthetic sample data shipped so a stranger with only Docker can run
  the demo.
- The operator views the enriched inventory and can produce a
  self-contained risk report plus CSV and JSON exports.
- The operator assigns owners, flags identities, and records
  attestations, in role-call only; nothing is written to the cloud
  account.

## Where it is going

Version one is the floor, not the product. The roadmap builds toward, in
order:

- **Deeper context.** Creator attribution and usage baselines beyond the
  provider's 90 day event window, once the log infrastructure exists to
  hold them, plus expected-profile checks: a known vendor integration
  holding exactly its documented permissions is furniture, and the same
  integration holding more is a finding.
- **Report-only governance.** A quarantine that observes before it ever
  enforces: mark an identity pending, watch its usage through a review
  window, and let the owner decide with evidence. A what-if view answers
  "had this been revoked a month ago, what would have broken."
- **Human-decided remediation, machine-verified.** Deactivate and
  restore, each behind a fresh proof of identity, each shown as a policy
  diff before it happens, each verified against the provider afterward,
  because clicked is not revoked until the provider says so.
- **Temporary approved re-elevation.** An owner asks for a quarantined
  identity back for a window, someone else approves, and the clock does
  the offboarding. Just-in-time access, applied to non-human identities.
- **More providers behind one identity model.** Okta and Entra after AWS,
  as adapters over the same append-only ingestion, not as rewrites.

The full sequence, with what each phase proves, is in
[ROADMAP.md](ROADMAP.md).

## Where to start

- [ROADMAP.md](ROADMAP.md) is the phase plan, the confirmed scope, and
  what is deliberately excluded.
- [ARCHITECTURE.md](ARCHITECTURE.md) is the components, the data flow,
  the trust boundaries, and the list of diagrams.
- [THREAT-MODEL.md](THREAT-MODEL.md) is the ranked threats, each mapped
  to its control, and the accepted risks.
- [DECISIONS.md](DECISIONS.md) records what was chosen, what was
  rejected, and why.
- [AGENTS.md](AGENTS.md) is the standards this project is built to.

## Running it

The skeleton runs; the application arrives subphase by subphase.

```
cp .env.example .env   # then set a password, for example: openssl rand -hex 24
docker compose up --build
```

Then open http://127.0.0.1:8000/health. Full instructions, sample data,
and the demo walk-through arrive with the later subphases.
