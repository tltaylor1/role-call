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

- **The provenance record itself was wrong.** Every commit before this
  entry carries a co-author trailer naming a model that was not the one
  running; the session's actual model is Claude Fable 5, id
  claude-fable-5. Caught by the human reading the history against the
  claim in this very file. The trailers are deliberately not rewritten,
  because rewriting history to polish a provenance error would defeat
  both the history and the provenance; from the commit that adds this
  entry forward, the trailer names the running model exactly, and this
  entry is the correction the old trailers point to.

Each entry changed a rule, a checklist, or a design, which is the point:
the catches compound, the mistakes do not.
