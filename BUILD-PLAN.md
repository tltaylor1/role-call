# Build plan

How the application gets built, decided before any of it is. Phase 1 is
divided into ordered subphases, planned in full in advance, built one at
a time. A subphase is built in small commits on its own branch and then
stops: a human reads the diff, runs the demo, and reads the tests, and
only after that review is the subphase's pull request merged, with the
required checks green, so the merge itself is the public record of the
review. No approval is required on the pull request, because there is
no second person to give one and a self-approval would be theater; the
gates are the checks and the deliberate merge. A subphase is not finished until the phase
diagrams match what is now true and the repository's one-line
description says the current phase; both live outside the gates'
reach, so the ritual is what keeps them honest. There is no testing phase at the end, because every
subphase ships its own tests, and there is no hardening phase in
substance, because each control arrives with the thing it protects; the
final subphase is proof, not retrofit.

The plan binds the order, not the learning. Testing and hardening run
through every subphase and get verified again at the end; and change is
expected, because building teaches. A discovery mid-build is not silently
absorbed: it becomes a decision, a roadmap amendment, or a backlog entry,
and this plan updates visibly, so the difference between the plan as
written and the build as it happened stays readable. Design is never
finished: each phase boundary reopens it, and the design documents are
revised with what the phase taught before the next one begins.

This is the opposite of building fast, on purpose. The pace is set by
review, and the interesting output of an AI-assisted build is the record
of what generation got wrong and what caught it; that record lives in
[AI-USAGE.md](AI-USAGE.md).

![The cycle every subphase travels: plan, build, demo and tests, human review, pull request merged](diagrams/subphase-cycle-sketch.svg)

## The subphases

1. **Foundation.** Hash-pinned dependencies checked against canonical
   sources, the software bill of materials, automated update review, a
   digest-pinned container image, fail-fast configuration, migrations
   from the first table, allowlist logging, health. Continuous
   integration grows test, dependency-audit, and lint jobs.
2. **Operators.** Local sign-in with a timing-equal path for unknown
   names, individually revocable sessions, the three roles checked per
   route, idempotent bootstrap, sign-in rate limiting, the audit spine
   writing in the same transaction as every action, and error responses
   that never echo input. Static type checking joins the gates here,
   with the first real logic, and the migration drift check joins with
   the first real model.
3. **Ingestion one.** The credential report parser: bounded, in memory,
   verified against its own claims, append-only, duplicates rejected,
   identities keyed by the provider's immutable identifier. Its fuzz
   suite arrives with it, property-based: stated invariants, hunted
   counterexamples, remembered failures.
4. **Ingestion two.** The account authorization details parser: roles,
   trust policies, groups as privilege sources, memberships, policy
   documents, tags, and the recreated-name detection. Its fuzz suite
   arrives with it.
5. **Derivation and credential findings.** The engine that computes
   state from history at read time, and the credential-hygiene findings
   with their tiers and the minimum observation age.
6. **Privilege findings.** Policy parsing, wildcard and admin-equivalent
   detection, external trust exposure, ownership findings, group
   findings, membership drift, and privilege attributed to its source.
7. **Inventory and frontend.** The lists, the detail view with its
   observation timeline, the dashboard, the as-of banner, and the single
   page that renders every value as text.
8. **Governance records.** Owner, purpose, flag, and attestation on
   identities and groups, attributed, audited, clearable.
9. **Review campaigns.** Scoped, deadlined review cycles with per-item
   dispositions including insufficient evidence, recommendations with
   their reasons, the change-since-last-certification view, recurrence
   presets, and no bulk certification by design.
10. **Reports and exports.** Escaped CSV and JSON, the self-contained
    risk report with every value context-escaped, and the per-campaign
    evidence export with its population statement.
11. **Sample data and the stranger drill.** The synthetic generator
    covering every archetype the rules need, and the fresh-clone run
    with nothing installed but Docker, following the README literally.
12. **Proof.** Container hardening verified by command, with the
    container file linted and the base image's operating system packages
    scanned, not only the Python tree; remaining rate limits and the
    timeout budget; the backup and retention procedure; the mutation
    check, automated, with coverage measured to inform it; the external
    checklist audits; figures verified against the running system; and
    the documents re-read and shortened.

Between subphases, the pipeline itself gets one deliberate batch: deep
static analysis on every push, linting and security audit of the
workflow files that gate everything else, an external scorecard of the
repository's own posture, and a link check across the cross-referenced
documents. Each tool is vetted at adoption and recorded as a decision,
the same way the linter was.

## Why this order

Identity before data, because every later route needs the role checks.
Parsers before the engine, because reading the data before designing
against it is the deepest lesson this project inherits. Credential
findings before privilege findings, because the second carries the
judgment and gets the hardest review. The frontend in the middle, so
every later subphase demonstrates with clicks. Governance before
campaigns, because the noun precedes the workflow. Reports after the
engine settles, because they consume it. The stranger drill before the
proof, so the audits run against the real demo. And the proof last only
in its verification, since most of its controls exist from the first
subphase.
