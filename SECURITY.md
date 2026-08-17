# Security

What protects this project today, what will protect the application, and
how to report a problem privately.

## Reporting a vulnerability

Report suspected vulnerabilities privately through GitHub's security
advisories: the Security tab of this repository, then "Report a
vulnerability." Do not open a public issue, pull request, or discussion
for a suspected vulnerability before it has been triaged.

A useful report includes the affected file or behavior, the impact as you
understand it, reproduction steps or a minimal proof of concept, and any
conditions required. Do not include real credentials or personal data in
a report. Reports get acknowledged, triaged, and answered honestly,
including when the answer is that the behavior is a documented, accepted
risk; those are listed in [THREAT-MODEL.md](THREAT-MODEL.md).

## Controls in place today

The application does not exist yet, so the controls that exist guard the
repository and its pipeline. Each is a mechanism that runs, not a rule
that hopes.

| Control | What it guards against |
|---|---|
| TruffleHog pre-commit hook, offline mode | A credential reaching a commit on this machine (D-002) |
| TruffleHog in continuous integration, verification on | A credential in any pushed history, checked against its provider to learn whether it is live |
| Vale pre-commit hook and continuous integration job | Writing-rule violations reaching history |
| Deferred-work marker gate, pre-commit and continuous integration | Stub markers standing in for finished work or recorded decisions |
| Continuous integration actions pinned by full commit hash | A moved tag changing what the pipeline runs |
| Pipeline tools downloaded from canonical releases and checksum verified | A substituted tool running inside the pipeline |
| Dependencies: none yet | The first dependency arrives with hash pinning, a software bill of materials, and automated update review, per the roadmap |

At the repository's visibility flip, the server layer joins: GitHub secret
scanning and push protection, completing the three scanning layers.

## Controls planned for the application

The application's controls are designed before the code, mapped
threat-by-threat in [THREAT-MODEL.md](THREAT-MODEL.md) and committed as
Phase 1 requirements in [ROADMAP.md](ROADMAP.md): authentication on every
request, three roles with per-route authorization, rate limiting, bounded
ingestion, derived state, atomic audit, deployment-layer encryption at
rest (D-020), escaped exports, and the rest. When the code exists, this file gains the
controls-implemented table: each control, the threat it answers, and the
test that proves it. A control listed here without its test is a claim,
not a control, so the table waits for the tests.

## Supported versions

Fixes land on the latest commit of the main branch. There are no
versioned releases yet; when releases exist, this section will state
which ones receive fixes.
