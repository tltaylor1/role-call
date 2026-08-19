"""governance records

Revision ID: 08c833879484
Revises: 267d4f9afedb
Create Date: 2026-08-18 20:16:19.439291
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '08c833879484'
down_revision: str | Sequence[str] | None = '267d4f9afedb'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'governance_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=16), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.String(length=16), nullable=False),
        sa.Column('value', sa.String(length=500), nullable=False),
        sa.Column('owner_type', sa.String(length=16), nullable=True),
        sa.Column('actor_user_id', sa.Integer(), nullable=True),
        sa.Column('actor_username', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cleared_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cleared_by', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_governance_records_target_type'),
        'governance_records',
        ['target_type'],
        unique=False,
    )
    op.create_index(
        op.f('ix_governance_records_target_id'),
        'governance_records',
        ['target_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_governance_records_target_id'), table_name='governance_records'
    )
    op.drop_index(
        op.f('ix_governance_records_target_type'), table_name='governance_records'
    )
    op.drop_table('governance_records')
