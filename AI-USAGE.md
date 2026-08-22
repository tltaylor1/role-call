# AI usage

Built with an AI coding agent under written standards, and this file
records the arrangement: what the agent got wrong, what caught it, and
what each catch changed.

## The approach

The agent works against [AGENTS.md](AGENTS.md) from the first commit, so
the constraints precede the code. Design documents came before any
application code, and the build itself followed the plan in the roadmap section of [README.md](README.md):
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
  failure this entry documents. Updated August 20, 2026: the trailer
  shortened to the standard form, "Co-authored-by: Claude" with the
  attribution address, because the standard form is what external
  tooling parses. The limits stay stated, here and in the README,
  rather than in the trailer's name field; no trailer claims a model,
  which remains the true statement.
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
- **The sample data found two defects on its first run.** Importing
  both file formats across three generations, which is what real use
  looks like, is something no hand-made demonstration had ever done.
  It exposed an identity upgraded to its real identifier being
  duplicated by the next credential report, because the report could
  no longer recognise it, and a privilege reading that took the newest
  observation rather than the newest value, so an identity's
  group-granted administrator access vanished whenever two sources
  shared a capture time. Both were written weeks earlier and passed
  every test until the fixture stopped being typed by hand.
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

- **The route drift test had gone silently vacuous.** A framework
  update began wrapping included routers lazily, and the test that
  asserts every route is governed or named public was iterating a
  collection that no longer contained them: it was checking three
  routes and passing. Nothing failed, which is the danger; the gate
  reported green while guarding nothing. Found while extending the
  test to compare against the documented route enumeration, fixed by
  flattening the wrapped routers, and now held by a count canary that
  fails loudly if enumeration ever collapses again. A test must assert
  what it can see before asserting what it sees is right.
- **The mutation check did its job on its first run.** Seven
  controls were each broken deliberately to prove the suite notices;
  six failed as claimed and one survived: with token hashing broken to
  a constant, every fabricated token matched whatever session existed,
  and no test noticed, because every test presented either a real
  token or none. The missing test now exists, and the check that found
  the gap runs in the pipeline.

- **The runbook claimed a verification that had not happened.** The
  operating procedures stated that each was run against a live stack
  before being written down, and folding them into the README exposed
  the tell: the commands named a service that does not exist in the
  compose file, so they had never been executed. The full cycle,
  backup, restore, the throwaway-database drill with counts compared,
  was then actually run with the corrected commands before the folded
  text was allowed to repeat the claim. A procedure that was never
  executed is not yet a procedure, and the claim of
  verification is itself a figure that needs verifying.

- **The agent's own tooling broke its own promise on its first run,
  and the first remedy was the wrong kind.** The script that pushes
  branches under the agent's identity carried a comment saying tokens
  never touch disk; its first execution wrote the token into the local
  branch configuration, because the push URL carried the credential
  and the upstream flag recorded that URL. Nothing reached the
  repository, the file is git's local configuration, which no commit
  carries, and the token was revoked at the provider inside its
  one-hour life. The initial response was scrubbing the file, and the
  human's ruling on that response became the real lesson: needing to
  scrub means the secret was already somewhere it should never have
  been, and a remedy that depends on noticing is not a control. Two
  mechanisms replaced it. The credential left the URL entirely, git
  now receives it through a credential helper from memory, so no
  upstream, log, or configuration write can ever carry it, removing
  the class rather than the instance. And a commit-time gate now
  watches the one file the secret scanner deliberately skips, the
  local git configuration, so anything credential-shaped landing
  there is a build failure, not a discovery.

- **A decision said one thing and the build did the opposite, for
  eighteen subphases.** D-013 decided the application's database role
  holds data rights only and migrations run separately as a
  privileged role, explicitly rejecting schema changes at startup;
  the build ran migrations in the serving container's start command
  as the owner role from the first subphase onward, and the threat
  model cited the unimplemented decision as a control. Nothing caught
  it, not the agent that wrote both the decision and the code, not
  eighteen subphase reviews, until a direct question was answered by
  reading the code instead of the record. The repair is D-051, and
  the lasting mechanism is the pipeline probe that attempts a schema
  change as the runtime role and fails the build unless refused: the
  class of decision-versus-build drift now has at least one gate, and
  the honest note is that only this instance is gated, because such
  drift is found by asking questions, not by grep.

Each entry changed a rule, a checklist, or a design, which is the point:
the catches compound, the mistakes do not. This last one changed the
attribution itself, and its lesson is the whole file's thesis turned on
its own record: a confident correction can be wrong, and only an outside
check settles it.
