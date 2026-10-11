"""add feeding values and redemption history

Revision ID: 202609290001
Revises: 202609220001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202609290001"
down_revision: str | None = "202609220001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ID_TYPE = sa.BigInteger().with_variant(sa.Integer(), "sqlite")


def upgrade() -> None:
    with op.batch_alter_table("food") as batch:
        batch.add_column(sa.Column("feeding_value", sa.Integer(), server_default="0", nullable=False))
        batch.create_check_constraint("ck_food_feeding_value_non_negative", "feeding_value >= 0")

    with op.batch_alter_table("dining_group_member") as batch:
        batch.add_column(sa.Column("display_name", sa.String(64), nullable=True))

    with op.batch_alter_table("dinner_plan") as batch:
        batch.add_column(sa.Column("cook_user_id", ID_TYPE, nullable=True))
        batch.add_column(sa.Column("cook_name", sa.String(64), nullable=True))
    op.execute(
        sa.text(
            "UPDATE dinner_plan SET cook_user_id = created_by, "
            "cook_name = (SELECT nickname FROM app_user WHERE app_user.id = dinner_plan.created_by)"
        )
    )
    with op.batch_alter_table("dinner_plan") as batch:
        batch.alter_column("cook_user_id", existing_type=ID_TYPE, nullable=False)
        batch.alter_column("cook_name", existing_type=sa.String(64), nullable=False)
        batch.create_foreign_key("fk_dinner_plan_cook_user_id", "app_user", ["cook_user_id"], ["id"])

    with op.batch_alter_table("dinner_plan_item") as batch:
        batch.add_column(sa.Column("feeding_value", sa.Integer(), server_default="0", nullable=False))
        batch.create_check_constraint("ck_dinner_plan_item_feeding_value_non_negative", "feeding_value >= 0")

    op.create_table(
        "feeding_reward",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("group_id", ID_TYPE, nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("cost", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("cost > 0", name="ck_feeding_reward_cost_positive"),
        sa.ForeignKeyConstraint(["group_id"], ["dining_group.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_feeding_reward_group_active", "feeding_reward", ["group_id", "is_active"])

    op.create_table(
        "feeding_value_entry",
        sa.Column("id", ID_TYPE, primary_key=True),
        sa.Column("group_id", ID_TYPE, nullable=False),
        sa.Column("user_id", ID_TYPE, nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(256), nullable=False),
        sa.Column("plan_id", ID_TYPE, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("amount != 0", name="ck_feeding_value_entry_amount_nonzero"),
        sa.CheckConstraint("kind in ('earn', 'redeem')", name="ck_feeding_value_entry_kind"),
        sa.ForeignKeyConstraint(["group_id"], ["dining_group.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["dinner_plan.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("plan_id", name="uq_feeding_value_entry_plan"),
    )
    op.create_index(
        "idx_feeding_value_entry_group_user_created",
        "feeding_value_entry",
        ["group_id", "user_id", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("idx_feeding_value_entry_group_user_created", table_name="feeding_value_entry")
    op.drop_table("feeding_value_entry")
    op.drop_index("idx_feeding_reward_group_active", table_name="feeding_reward")
    op.drop_table("feeding_reward")
    with op.batch_alter_table("dinner_plan_item") as batch:
        batch.drop_constraint("ck_dinner_plan_item_feeding_value_non_negative", type_="check")
        batch.drop_column("feeding_value")
    with op.batch_alter_table("dinner_plan") as batch:
        batch.drop_constraint("fk_dinner_plan_cook_user_id", type_="foreignkey")
        batch.drop_column("cook_name")
        batch.drop_column("cook_user_id")
    with op.batch_alter_table("dining_group_member") as batch:
        batch.drop_column("display_name")
    with op.batch_alter_table("food") as batch:
        batch.drop_constraint("ck_food_feeding_value_non_negative", type_="check")
        batch.drop_column("feeding_value")
