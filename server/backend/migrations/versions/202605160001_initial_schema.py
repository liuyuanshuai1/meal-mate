"""initial schema

Revision ID: 202605160001
Revises:
Create Date: 2026-05-16 00:01:00
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202605160001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "food_category",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("sort", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_food_category_is_active", "food_category", ["is_active"])
    op.create_index("idx_food_category_sort", "food_category", ["sort"])

    op.create_table(
        "banner",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=128), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("link_type", sa.String(length=32), server_default="none", nullable=False),
        sa.Column("link_target", sa.String(length=256), nullable=True),
        sa.Column("sort", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("link_type in ('none', 'food', 'url')", name="ck_banner_link_type"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_banner_is_active", "banner", ["is_active"])
    op.create_index("idx_banner_sort", "banner", ["sort"])

    op.create_table(
        "food",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("is_recommended", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("sort", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_food_price_non_negative"),
        sa.ForeignKeyConstraint(["category_id"], ["food_category.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_food_category_id", "food", ["category_id"])
    op.create_index("idx_food_is_active", "food", ["is_active"])
    op.create_index("idx_food_is_recommended", "food", ["is_recommended"])
    op.create_index("idx_food_name", "food", ["name"])
    op.create_index("idx_food_sort", "food", ["sort"])

    op.create_table(
        "eat_record",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("person", sa.String(length=64), server_default="default", nullable=False),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("eaten_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("total_price >= 0", name="ck_eat_record_total_price_non_negative"),
        sa.CheckConstraint("user_id > 0", name="ck_eat_record_user_id_positive"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_eat_record_eaten_at", "eat_record", ["eaten_at"])
    op.create_index("idx_eat_record_user_id", "eat_record", ["user_id"])

    op.create_table(
        "eat_record_item",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("record_id", sa.BigInteger(), nullable=False),
        sa.Column("food_id", sa.BigInteger(), nullable=True),
        sa.Column("food_name", sa.String(length=128), nullable=False),
        sa.Column("food_image_url", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_eat_record_item_price_non_negative"),
        sa.CheckConstraint("quantity > 0", name="ck_eat_record_item_quantity_positive"),
        sa.ForeignKeyConstraint(["food_id"], ["food.id"]),
        sa.ForeignKeyConstraint(["record_id"], ["eat_record.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_eat_record_item_food_id", "eat_record_item", ["food_id"])
    op.create_index("idx_eat_record_item_record_id", "eat_record_item", ["record_id"])


def downgrade() -> None:
    op.drop_index("idx_eat_record_item_record_id", table_name="eat_record_item")
    op.drop_index("idx_eat_record_item_food_id", table_name="eat_record_item")
    op.drop_table("eat_record_item")
    op.drop_index("idx_eat_record_user_id", table_name="eat_record")
    op.drop_index("idx_eat_record_eaten_at", table_name="eat_record")
    op.drop_table("eat_record")
    op.drop_index("idx_food_sort", table_name="food")
    op.drop_index("idx_food_name", table_name="food")
    op.drop_index("idx_food_is_recommended", table_name="food")
    op.drop_index("idx_food_is_active", table_name="food")
    op.drop_index("idx_food_category_id", table_name="food")
    op.drop_table("food")
    op.drop_index("idx_banner_sort", table_name="banner")
    op.drop_index("idx_banner_is_active", table_name="banner")
    op.drop_table("banner")
    op.drop_index("idx_food_category_sort", table_name="food_category")
    op.drop_index("idx_food_category_is_active", table_name="food_category")
    op.drop_table("food_category")
