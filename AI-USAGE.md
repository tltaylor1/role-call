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
- **An edit silently did not happen, and a commit message lied about
  it.** Two scripted text replacements targeted wording that was not in
  the file, and the replacement primitive reports nothing on a miss: a
  comment claimed for the workflow file never landed, and neither did
  the database service block, so the pipeline shipped a job that needed
  a database with no database. The commit message stating the comment
  was in both files entered public history false. Caught by the
  pipeline failing on the missing service; the falsehood is corrected
  forward, not rewritten. The lesson joins the environment one: an edit
  is not made until the result is read back, and a tool that fails
  loudly on a missed match beats one that continues in silence.
- **A destructive cleanup ran on a report of state instead of the
  state.** Told that three pull requests were merged, the agent deleted
  their branches without checking; none had merged, and the deletions
  closed all three. Recovery was total, every tip was known and the
  requests reopened byte-identical, but the lesson is the sharpest form
  of the oldest rule here: a destructive action is never justified by a
  report of state, only by the state itself, read at execution time.
  Caught by reading the API after acting, which is one read too late.
- **The vetting itself was weaker than the gate it vetted.** The
  workflow linter delegates embedded scripts to a shell analyzer only
  when one is installed. The build machine had none, so the local
  vetting run silently skipped a whole class of checks and passed;
  the pipeline, which has the analyzer, failed on two unquoted
  substitutions the local run never saw. The analyzer is now installed
  locally, the finding was real and fixed, and the lesson is that a
  passing check proves nothing until the environments match: the same
  tool ran in both places and was not the same gate.
- **The new gates found work before they were installed.** Vetting the
  pipeline batch meant running each tool against the repository first.
  The workflow audit found every checkout persisting a repository
  token on disk for later steps that never needed it; the link checker
  found three references to a file that lives in another repository.
  Then the fix for those links introduced a misspelled address, caught
  only by running the checker again. Fix, then re-verify the fix: the
  second check is not optional, because the fix is written by the same
  hands that wrote the flaw.
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
