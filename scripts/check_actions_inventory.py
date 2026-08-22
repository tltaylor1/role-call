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


IMAGE_PATTERN = re.compile(
    r"docker run[^\n]*?([a-z0-9.-]+(?:/[a-z0-9._-]+)+)@(sha256:[0-9a-f]{64})"
)


def main() -> int:
    workflow_pins: set[tuple[str, str]] = set()
    workflow_images: set[tuple[str, str]] = set()
    for workflow in sorted(ROOT.glob(".github/workflows/*.yml")):
        text = workflow.read_text()
        workflow_pins |= pins_in(text)
        workflow_images |= set(IMAGE_PATTERN.findall(text))

    readme = ROOT.joinpath("README.md").read_text()
    readme_pins = pins_in(readme)
    # Images the README claims the workflows run: any registry-path
    # digest reference outside the action table's uses form.
    readme_images = {
        (image, sha)
        for image, sha in re.findall(
            r"`([a-z0-9.-]+(?:/[a-z0-9._-]+)+)@(sha256:[0-9a-f]{64})`", readme
        )
    }

    missing = workflow_pins - readme_pins
    stale = readme_pins - workflow_pins
    for action, sha in sorted(missing):
        print(f"in a workflow but not the README table: {action}@{sha}")
    for action, sha in sorted(stale):
        print(f"in the README table but no workflow: {action}@{sha}")

    image_missing = workflow_images - readme_images
    image_stale = readme_images - workflow_images
    for image, sha in sorted(image_missing):
        print(f"run by a workflow but not in the README image table: {image}@{sha}")
    for image, sha in sorted(image_stale):
        print(f"in the README image table but run by no workflow: {image}@{sha}")

    if missing or stale or image_missing or image_stale:
        return 1
    print(
        f"actions inventory matches: {len(workflow_pins)} pinned uses, "
        f"{len(workflow_images)} workflow-run images"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
