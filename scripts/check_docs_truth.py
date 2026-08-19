#!/usr/bin/env python3
"""The docs-truth gate (D-031).

The journey diagram is the single source for build status, because the
subphase-close ritual already updates it. This check makes the README
and roadmap agree with it, and forbids the specific stale claims that
sat in public documents for weeks: a status figure that exists in more
than one place drifts, so every copy must match the source or the gate
blocks.

Run from the repository root; exits nonzero with the rule that failed.
"""

import re
import sys
from pathlib import Path

FIGURE = re.compile(r"[Ss]ubphases?\s+(\d+)\s+of\s+(\d+)")

# Phrases that were publicly false once; they may never appear in these
# files again. Scoped to the status-bearing documents on purpose, so
# history-keeping files can still quote them.
FORBIDDEN = {
    "README.md": ["No application code exists", "does not exist yet",
                  "The skeleton runs", "Phase 0 is in progress"],
    "SECURITY.md": ["does not exist yet", "No application code exists"],
}


def main() -> int:
    failures: list[str] = []

    source = Path("diagrams/phase-journey-sketch.svg").read_text()
    match = FIGURE.search(source)
    if match is None:
        failures.append(
            "the journey diagram no longer states 'subphases N of M'; "
            "the status source is gone"
        )
    else:
        figure = match.groups()
        for name in ("README.md",):
            text = Path(name).read_text()
            found = FIGURE.search(text)
            if found is None:
                failures.append(f"{name} does not state the subphase figure")
            elif found.groups() != figure:
                failures.append(
                    f"{name} says {found.group(1)} of {found.group(2)}; "
                    f"the journey diagram, the source, says "
                    f"{figure[0]} of {figure[1]}"
                )

    for name, phrases in FORBIDDEN.items():
        text = Path(name).read_text()
        for phrase in phrases:
            if phrase in text:
                failures.append(f"{name} contains the stale claim: {phrase!r}")

    for failure in failures:
        print(f"docs-truth: {failure}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
