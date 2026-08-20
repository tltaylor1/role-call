#!/usr/bin/env python3
"""The actions inventory gate: the README's table is the workflows.

The workflows stand on third-party actions the same way the
application stands on packages, so the README documents each action
with its commit pin, and this gate holds the table to the truth in
both directions: an action added, removed, or re-pinned in any
workflow fails the build until the table moves with it. The figures
lesson, applied to the supply chain.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERN = re.compile(
    r"([A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+)@([0-9a-f]{40})"
)


def pins_in(text: str) -> set[tuple[str, str]]:
    return set(PATTERN.findall(text))


def main() -> int:
    workflow_pins: set[tuple[str, str]] = set()
    for workflow in sorted(ROOT.glob(".github/workflows/*.yml")):
        workflow_pins |= pins_in(workflow.read_text())

    readme_pins = pins_in(ROOT.joinpath("README.md").read_text())

    missing = workflow_pins - readme_pins
    stale = readme_pins - workflow_pins
    for action, sha in sorted(missing):
        print(f"in a workflow but not the README table: {action}@{sha}")
    for action, sha in sorted(stale):
        print(f"in the README table but no workflow: {action}@{sha}")
    if missing or stale:
        return 1
    print(f"actions inventory matches: {len(workflow_pins)} pinned uses")
    return 0


if __name__ == "__main__":
    sys.exit(main())
