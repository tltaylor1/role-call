# Acknowledgements

The ideas below were learned from projects and publications that came
first. Ideas are free to take; taking them namelessly is not how this
project works. Where code is ever incorporated, its license terms are
followed exactly; everything here so far is adapted thinking, credited to
its source.

## Projects

- **[Repokid](https://github.com/Netflix/repokid)** (Netflix). The
  deepest lesson in the category: finding unused permissions is easy, and
  removing them safely is the product. Its staged, reversible approach to
  removal shapes this project's action phases, and its eligibility idea
  became the minimum observation age, which keeps a new identity from
  being flagged as unused before it has been watched long enough to mean
  it.
- **[Cloudsplaining](https://github.com/salesforce/cloudsplaining)**
  (Salesforce). The single-file, risk-prioritized report as the artifact
  people actually share, and a public example of classifying findings by
  consequence rather than by service.
- **[PMapper](https://github.com/nccgroup/PMapper)** (NCC Group). The
  demonstration that what a principal can reach through assume-role
  chains exceeds what its policies say directly. This project's version
  one states that limitation plainly instead of hiding it, which is a
  debt to PMapper's argument.
- **[Cartography](https://github.com/lyft/cartography)** (Lyft). Identity
  relationships as a graph with a common model across sources, the shape
  later providers join through.
- **[ConsoleMe](https://github.com/Netflix/consoleme)** (Netflix).
  Ownership and request workflows as the thing that turns an inventory
  into governance.
- **Rhino Security Labs' privilege escalation research** (2018), the
  published catalogue of AWS Identity and Access Management permission
  combinations that let a principal raise its own privilege. Version
  one's escalation heuristics detect the combinations that catalogue
  named, and the same research underpins several of the tools below.
- **[SkyArk](https://github.com/cyberark/SkyArk)** (CyberArk). Shadow
  admin detection: privilege judged by what a policy can do, not what it
  is called.
- **[Prowler](https://github.com/prowler-cloud/prowler)** and the
  credential report tradition. The check taxonomy for credential hygiene
  this project's findings vocabulary builds on.
- **[Aardvark](https://github.com/Netflix-Skunkworks/aardvark)**
  (Netflix, archived). Its history taught the adapter lesson: consume the
  provider's native successor rather than maintaining a scraper.
- **[diagram-design](https://github.com/cathrynlavery/diagram-design)**
  (Cathryn Lavery, MIT). The working sketches in the diagrams directory
  follow drawing principles adapted, in this project's own words, from
  its editorial doctrine: the complexity budget, restraint with emphasis,
  and the rule that a diagram is done when nothing can be removed.

## Publications and standards

- **[OWASP](https://owasp.org/)**, whose published lists shaped this
  design well beyond the one the findings anchor to. The Non-Human
  Identities Top 10 (2025) supplies the finding identifiers; the Web
  Application Top 10 (2021), the API Security Top 10, the CI/CD
  Security Top 10, the Kubernetes Top 10, the Docker security guidance,
  and the LLM Applications Top 10 were each walked item by item against
  the design before the first application commit, and several of this
  project's controls exist because that walk caught their absence.
- **PCI DSS 4.0, ISO/IEC 27002:2022, NIST SP 800-53, CIS Controls v8**,
  and the audit practice around SOX and SOC 2, which together define the
  periodic, evidenced access review this tool exists to serve. The
  two-way mapping lives in [COMPLIANCE.md](COMPLIANCE.md).
- **Andrew Koenig**, who coined the anti-pattern in 1995, and the authors
  of the 1998 AntiPatterns book, whose two-part test, a recurring
  practice that looks beneficial but harms, paired with a proven
  refactored alternative, disciplines how this project writes down what
  not to do.

## A note on honesty

Nothing here claims novelty for its parts. The parts are assembled from
the projects above, the standards named, and lessons from earlier builds;
what this project adds is the combination, the governance loop as open
source, and the record of how it was built. Where a lesson was taken, the
source is named; where a gap remains, the documents say so.
