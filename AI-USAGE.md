# AI usage

Built with an AI coding agent under written standards, and this file is
the honest record of the arrangement.

## The approach

The agent works against [AGENTS.md](AGENTS.md) from the first commit, so
the constraints precede the code. Design documents came before any
application code, and the build itself follows [BUILD-PLAN.md](BUILD-PLAN.md):
ordered subphases, each closed by human review before the next begins.
Commits the agent co-authors carry a trailer naming the exact model, so
the provenance of the code is readable from history the same way the
provenance of every dependency is readable from the lock file.

Most AI-assisted building optimizes for speed. This project optimizes
for the record: the interesting output of working with a generator is
the catalogue of what it produced that was wrong, plausible, or subtly
overclaimed, and what caught it. That catalogue is the section below. It
only ever contains real events, in the order they happened, because a
manufactured entry would defeat the reason this file exists.

## Caught

- **The group model's first draft was wrong.** The agent proposed groups
  as analyzable but ungovernable, argued confidently for it, and the
  human challenge surfaced that access reviews certify group memberships
  as their standard object, so the model was inverted. D-019 records the
  corrected design and names its own rejected first draft.
- **The threat model cited a control that did not exist.** An early
  revision listed a tamper-evident audit trail as a mitigation while
  nothing provided one. Caught in a gap audit; the claim moved to the
  accepted risks, where it now states when the control actually arrives.
- **The pipeline failed itself on its first run.** The workflow
  downloaded a tool archive into the workspace, and the marker scan then
  found forbidden markers inside the archive it had just downloaded.
  The fix sends tool downloads to the runner's temporary directory so
  the workspace stays pristine for its own scans.
- **The marker gate blocked its own sibling.** The commit adding the
  continuous integration workflow was rejected by the pre-commit marker
  hook, because the workflow names the markers in order to forbid them.
  The exclusion is scoped to the two files that must name them, with the
  reason written beside it.
- **A working sketch broke the drawing rules it shipped under.** A
  connector ran straight through a box that was not its endpoint, the
  exact anti-pattern the diagram doctrine names. Caught by human eye;
  the doctrine's verification list gained an explicit trace check.
- **Two document headings were committed broken.** Markdown headings
  cannot wrap across lines; two did. Repaired in a follow-up commit
  rather than a rewrite, so the history keeps the mistake.
- **The writing gate fired a true false positive.** The rule that keeps
  audience language out of these documents flagged the word that names
  this product's user. The exception is a scoped inline allowlist with
  its reason; the rule runs at full strength everywhere else.

- **The provenance record was corrected wrongly, then corrected again.**
  This one took two tries and is the sharpest lesson in the file. Early
  commit trailers named the model as Claude Opus 4.8. The trailers were
  then "corrected" to Claude Fable 5 on the belief that Opus was a
  mistaken string, and this file said so. That correction was itself
  wrong. The runtime switches models between turns: this is a Mythos-class
  model whose safeguards flag dual-use work, and a security tool that
  reads access policies and models attacker moves is dual-use by
  definition, so many turns are handed to a fallback model. The switch
  happens below the model's own visibility, so its self-report is
  unreliable and the original Opus trailers were most likely accurate
  when written. The human resolved it with an external signal the model
  could not see. Because per-turn attribution is not reliably knowable
  from inside, the trailer no longer names one model; from the commit
  that adds this entry forward it reads "Claude (Anthropic), model varies
  per turn," which is the true statement. History is not rewritten,
  because rewriting a provenance record to look cleaner is exactly the
  failure this entry documents.
- **The secret gate blocked the first code commit.** The moment a
  Python virtual environment existed, the commit-time scan swept it and
  found dozens of example credentials in installed libraries'
  documentation, all fake, and refused the commit anyway. The fix
  scopes the scan with an exclude file for git-ignored tool
  directories, which nothing can commit from; alarms that are always
  false teach the eye to skip the alarm, and a gate nobody believes is
  not a gate.

Each entry changed a rule, a checklist, or a design, which is the point:
the catches compound, the mistakes do not. This last one changed the
attribution itself, and its lesson is the whole file's thesis turned on
its own record: a confident correction can be wrong, and only an outside
check settles it.
