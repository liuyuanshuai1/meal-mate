"""add query performance indexes

Revision ID: 202609220001
Revises: 202608120001
"""

from collections.abc import Sequence

from alembic import op

revision: str = "202609220001"
down_revision: str | None = "202608120001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "idx_dinner_plan_group_status_created",
        "dinner_plan",
        ["group_id", "status", "created_at", "id"],
    )
    op.create_index(
        "idx_eat_record_user_eaten_id",
        "eat_record",
        ["user_id", "eaten_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("idx_eat_record_user_eaten_id", table_name="eat_record")
    op.drop_index("idx_dinner_plan_group_status_created", table_name="dinner_plan")
