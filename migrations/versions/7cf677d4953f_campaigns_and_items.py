"""campaigns and items

Revision ID: 7cf677d4953f
Revises: 08c833879484
Create Date: 2026-08-18 20:46:26.172082
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '7cf677d4953f'
down_revision: str | Sequence[str] | None = '08c833879484'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('scope', sa.String(length=32), nullable=False),
        sa.Column('due_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('recurrence', sa.String(length=16), nullable=False),
        sa.Column('created_by', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_by', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'campaign_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=16), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('recommendation', sa.String(length=32), nullable=False),
        sa.Column('recommendation_reasons', sa.JSON(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('disposition', sa.String(length=32), nullable=True),
        sa.Column('disposition_note', sa.String(length=500), nullable=True),
        sa.Column('disposed_by', sa.String(length=64), nullable=True),
        sa.Column('disposed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('campaign_id', 'target_type', 'target_id'),
    )
    op.create_index(
        op.f('ix_campaign_items_campaign_id'),
        'campaign_items',
        ['campaign_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_campaign_items_campaign_id'), table_name='campaign_items'
    )
    op.drop_table('campaign_items')
    op.drop_table('campaigns')
