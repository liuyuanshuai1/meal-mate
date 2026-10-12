"""track daily AI recipe exploration usage

Revision ID: 202610120001
Revises: 202610110001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202610120001"
down_revision: str | None = "202610110001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_explore_usage",
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("app_user.id"), primary_key=True),
        sa.Column("day", sa.Date(), primary_key=True),
        sa.Column("request_count", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ai_explore_usage")
