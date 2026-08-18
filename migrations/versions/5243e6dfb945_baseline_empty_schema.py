"""baseline, empty schema

Revision ID: 5243e6dfb945
Revises:
Create Date: 2026-08-17

The anchor revision. It changes nothing; it exists so every real
migration has an ancestor and a fresh database has a first step.
"""

from collections.abc import Sequence

revision: str = "5243e6dfb945"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
