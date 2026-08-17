# Compliance traceability

The published frameworks that codify what this tool does, mapped in both
directions: from each framework requirement to what in role-call answers
it, and from each design decision to the requirements that informed it.
Updated as the work proceeds; a decision that leans on a framework cites
it, and a framework row that nothing answers yet says so. Wordings here
are paraphrased; exact clause text is verified against the current
edition before anything claims conformance.

<!-- vale BuildGuidelines.Audience = NO -->
<!-- Scoped exception: "reviewer" below names the product's user, the
     person who performs an access review, which is the standard term in
     every framework this work follows. It does not describe this
     document's audience, which is what the rule exists to prevent. -->
## From the frameworks to role-call

| Requirement | What it asks | What answers it here |
|---|---|---|
| PCI DSS 4.0, 7.2.4 | Review all user accounts and privileges at least every six months | Review campaigns with due dates and recurrence (D-021); the evidence export |
| PCI DSS 4.0, 7.2.5 and 7.2.5.1 | Application and system accounts get least privilege and periodic review at a risk-based frequency | The non-human inventory itself; campaign recurrence set per account; privilege findings |
| OWASP Non-Human Identities Top 10 (2025) | The named risk classes for non-human identities | The finding vocabulary carries the NHI identifiers: improper offboarding, overprivileged, long-lived secrets, reuse, and kin |
| NIST SP 800-53, AC-2 | Accounts managed, reviewed on a schedule, disabled when inactive | Inventory, staleness findings, campaigns; disabling itself waits for the action phases by design (D-005) |
| NIST SP 800-53, AC-6(7) | Periodic review of privileges, with removal when no longer fit | Privilege findings with source attribution (D-019); review decisions recorded and tracked |
| ISO/IEC 27002:2022, 5.16 | Identity lifecycle management, explicitly including non-human | The whole product |
| ISO/IEC 27002:2022, 5.18 | Access rights reviewed at planned intervals and on change | Campaigns; the delta view surfaces change for review |
| CIS Controls v8, 5.1 and 5.5 | An inventory of accounts, and a dedicated, validated service account inventory | The inventory, derived from snapshots, with the as-of completeness statement |
| CIS Controls v8, 5.3 | Dormant accounts disabled after a defined period | Staleness findings with the minimum observation age; action itself deferred (D-005) |
| SOX ITGC and SOC 2 CC6 practice | Complete population, independent reviewer, evidence per decision, timely remediation | The completeness statement, reviewer attribution, the per-campaign evidence export, decisions tracked to closure |

## From the decisions to the frameworks

| Decision | Framework grounding |
|---|---|
| D-005 enrichment over automation | AC-2 and CIS 5.3 name disabling as the goal; this design routes it through a human until the trust ladder earns the action phases |
| D-006 append-only derived state | The SOX completeness and evidence expectations: a population and history that cannot silently change |
| D-016 immutable identifier keying | OWASP NHI reuse risk: a recreated principal must not inherit standing |
| D-019 identities act, sources grant, both governed | ISO 5.18 and universal access review practice certify group memberships, so the group must hold owners and attestations |
| D-021 the review campaign scope | PCI 7.2.4 and 7.2.5, ISO 5.18, AC-2, and audit practice all define the periodic, evidenced review as the unit of governance |
<!-- vale BuildGuidelines.Audience = YES -->
