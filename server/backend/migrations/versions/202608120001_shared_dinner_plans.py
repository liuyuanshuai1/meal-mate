"""add users, dining groups and shared dinner plans

Revision ID: 202608120001
Revises: 202605160001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202608120001"
down_revision: str | None = "202605160001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_user",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("openid", sa.String(128), nullable=False),
        sa.Column("nickname", sa.String(64), server_default="饭搭子", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("openid"),
    )
    op.create_index("ix_app_user_openid", "app_user", ["openid"], unique=True)
    op.create_table(
        "dining_group",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(64), server_default="我们的饭搭子", nullable=False),
        sa.Column("invite_token", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invite_token"),
    )
    op.create_index("ix_dining_group_invite_token", "dining_group", ["invite_token"], unique=True)
    op.create_table(
        "dining_group_member",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(16), server_default="member", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["dining_group.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", "user_id", name="uq_dining_group_member"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "dinner_plan",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(16), server_default="pending", nullable=False),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status in ('pending', 'completed', 'cancelled')", name="ck_dinner_plan_status"),
        sa.CheckConstraint("total_price >= 0", name="ck_dinner_plan_total_price_non_negative"),
        sa.ForeignKeyConstraint(["created_by"], ["app_user.id"]),
        sa.ForeignKeyConstraint(["group_id"], ["dining_group.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dinner_plan_group_id", "dinner_plan", ["group_id"])
    op.create_table(
        "dinner_plan_item",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("plan_id", sa.BigInteger(), nullable=False),
        sa.Column("food_id", sa.BigInteger(), nullable=False),
        sa.Column("food_name", sa.String(128), nullable=False),
        sa.Column("food_image_url", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_dinner_plan_item_price_non_negative"),
        sa.CheckConstraint("quantity > 0", name="ck_dinner_plan_item_quantity_positive"),
        sa.ForeignKeyConstraint(["food_id"], ["food.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["dinner_plan.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("dinner_plan_item")
    op.drop_index("ix_dinner_plan_group_id", table_name="dinner_plan")
    op.drop_table("dinner_plan")
    op.drop_table("dining_group_member")
    op.drop_index("ix_dining_group_invite_token", table_name="dining_group")
    op.drop_table("dining_group")
    op.drop_index("ix_app_user_openid", table_name="app_user")
    op.drop_table("app_user")
