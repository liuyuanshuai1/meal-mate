"""add reservation time and partner reminder state to dinner plans

Revision ID: 202610120003
Revises: 202610120002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202610120003"
down_revision: str | None = "202610120002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("dinner_plan", sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True))
    op.add_column("dinner_plan", sa.Column("partner_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE dinner_plan SET partner_seen_at = created_at WHERE status = 'pending'")


def downgrade() -> None:
    op.drop_column("dinner_plan", "partner_seen_at")
    op.drop_column("dinner_plan", "scheduled_for")
