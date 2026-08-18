# Roadmap

Where this is going and what is out of scope. How each phase gets
built, and the current phase's subphases, live in
[BUILD-PLAN.md](BUILD-PLAN.md).

The build runs in phases. Each phase ends in a state that can be run and
demonstrated on its own, rather than leaving work half-finished until a
later phase completes it.

**Contents:** [Status](#status) · [Phases](#phases) · [Scope of version one](#scope-of-version-one) · [Out of scope](#out-of-scope)

-------------------------------------------------------------------------------

## Status

Phase 1 is in progress: the application is being built in review-gated
subphases whose order and content [BUILD-PLAN.md](BUILD-PLAN.md) fixed
in advance. Subphases 6 of 12 are built and merged: the foundation, the
operators and audit spine, both ingestion surfaces, the derivation
engine, and the credential and privilege findings. Phase 0's design
artifacts are complete: the decisions in [DECISIONS.md](DECISIONS.md),
the threat model, the architecture, the confirmed scope below, and the
diagram list at the end of the architecture document. This figure is
kept honest by a pipeline check against the journey diagram (D-031).

-------------------------------------------------------------------------------

## Phases

![The eight phases as a timeline, with the current position marked](diagrams/phase-journey-sketch.svg)

**Phase 0. Design.** Architecture, data flow, and trust boundaries. A
threat model using STRIDE per component, ranked by likelihood and impact
and mapped to the controls that answer each threat. Confirmed scope for
version one. A list of the diagrams to draw. No code.

**Phase 1. Build the application.** The smallest system that genuinely
governs identities: the version one operations below, with the security
controls present from the first commit rather than added afterward.
Authentication on every request, three roles with authorization checked
per route, rate limiting on sign-in and every sensitive route, a request
timeout budget, input validation at every boundary, audit rows written in
the same transaction as the actions they record, schema migrations from
the first table, deployment-layer encryption at rest stated as a requirement (D-020), a backup and
restore procedure with a stated retention policy, and exports that cannot
carry spreadsheet formulas. Locally the stack speaks plain HTTP on the
loopback interface; transport encryption is the edge's job and arrives
with the cloud phases. Hash-pinned dependencies, a
software bill of materials, secret scanning, attack-path tests, and
continuous integration are set up here, and the container image is built
from a digest-pinned base.

**Phase 2. Local Kubernetes.** The image from Phase 1 orchestrated on kind
with Calico installed, so network policies are enforced rather than
silently ignored. Role-based access control, pod security standards, and
admission control. The phase answers whether the controls that depend on an
orchestrator work, on a laptop, with no cloud account involved.

**Phase 3. Cloud enclave as code.** The Amazon Web Services (AWS)
environment, defined as code and split into a persistent foundation and an
ephemeral workload. The foundation includes the organization trail into
storage, which is also the moment enrichment deepens: creator attribution
and usage history beyond the 90 day event window become possible only here.

**Phase 4. Managed Kubernetes.** The image promoted by digest into the
enclave. The orchestration questions were answered locally in Phase 2, so
this phase moves a known-good workload rather than debugging one.

**Phase 5. Security-gated pipeline.** The gates already running are
consolidated into one pipeline, remaining gaps close, and the whole set is
proven by introducing a flaw deliberately and confirming the pipeline
stops it.

**Phase 6. Runtime security and alerting.** Detection on the audit events
the threat model names, alerting on new high-risk identities, and the
first-hour response procedure written and exercised once.

**Phase 7. Human-triggered remediation.** The trust step change: role-call
gains a tightly scoped action credential and the ability to deactivate and
restore credentials in the target account, each action behind step-up
authentication, audited, shown as a policy diff before it happens, and
verified against the provider afterward. Report-only quarantine and the
review period arrive here. This phase requires its own threat model
revision before any code, because write access changes what the tool is.

Each phase ends with the diagrams updated, the decisions recorded, and the
documents re-read and shortened.

-------------------------------------------------------------------------------

## Scope of version one

Confirmed. Version one implements four operations, and nothing else:

- An operator authenticates.
- An identity snapshot is imported from a file, a credential report or a
  snapshot export, recorded append-only. Synthetic sample data ships with
  the repository, so a stranger with only Docker can run the whole demo.
- The operator views the enriched inventory, each identity with its origin,
  owner, last use, granted-versus-exercised permissions, credential
  hygiene, and risk context, derived from the snapshots rather than
  stored, and can produce a self-contained risk report plus CSV and JSON
  exports, every export escaped against spreadsheet formulas.
- The operator governs in role-call only: assigns an owner, flags an
  identity, or records an attestation. Nothing is written to the cloud
  account.

That set exercises authentication, authorization across three roles, input validation, derived state, audit
logging, and the enrichment model, and it keeps the tool's own cloud
credential read-only. Adding more operations would not add a control that
is not already demonstrated.

-------------------------------------------------------------------------------

## Out of scope

Recorded here so each absence is a decision rather than an oversight.

- **No writes to the cloud account until Phase 7.** Enrichment over
  automation: the product amplifies a human decision rather than acting on
  its own, and the tool never holds a credential more powerful than its
  current phase needs.
- **One provider.** AWS first; Okta and Entra join later behind the common
  identity model. Building two providers before one is governed well would
  add breadth without adding a property.
- **Effective privilege through role chaining is not computed.** Version
  one scores what a policy grants, not what assume-role chains can reach,
  and says so on the page. Computing reachability is real graph work that
  earns its own phase.
- **No automated remediation, ever, by design.** Report-only, review
  periods, and human-triggered actions are the ceiling. A tool that
  revokes on its own gets disabled the first time it breaks something.
- **No live provider connection in version one.** Files first, because the
  fresh-clone demo must run with Docker alone. The read-only pull joins in
  the cloud phases as an adapter behind the same append-only ingestion.
- **No real-time event stream in version one.** Snapshots are imported;
  event-driven refresh arrives with the cloud phases.
