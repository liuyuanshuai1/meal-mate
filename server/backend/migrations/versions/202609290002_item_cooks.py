"""move cook assignment from dinner plans to individual items

Revision ID: 202609290002
Revises: 202609290001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202609290002"
down_revision: str | None = "202609290001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ID_TYPE = sa.BigInteger().with_variant(sa.Integer(), "sqlite")


def upgrade() -> None:
    op.add_column("dinner_plan_item", sa.Column("cook_user_id", ID_TYPE, nullable=True))
    op.add_column("dinner_plan_item", sa.Column("cook_name", sa.String(64), nullable=True))
    op.execute(
        sa.text(
            "UPDATE dinner_plan_item SET "
            "cook_user_id = (SELECT cook_user_id FROM dinner_plan WHERE dinner_plan.id = dinner_plan_item.plan_id), "
            "cook_name = (SELECT cook_name FROM dinner_plan WHERE dinner_plan.id = dinner_plan_item.plan_id)"
        )
    )
    with op.batch_alter_table("dinner_plan_item") as batch:
        batch.alter_column("cook_user_id", existing_type=ID_TYPE, nullable=False)
        batch.alter_column("cook_name", existing_type=sa.String(64), nullable=False)
        batch.create_foreign_key("fk_dinner_plan_item_cook_user_id", "app_user", ["cook_user_id"], ["id"])
    with op.batch_alter_table("dinner_plan") as batch:
        batch.drop_constraint("fk_dinner_plan_cook_user_id", type_="foreignkey")
        batch.drop_column("cook_name")
        batch.drop_column("cook_user_id")
    with op.batch_alter_table("feeding_value_entry") as batch:
        batch.drop_constraint("uq_feeding_value_entry_plan", type_="unique")
        batch.create_unique_constraint("uq_feeding_value_entry_plan_user", ["plan_id", "user_id"])


def downgrade() -> None:
    connection = op.get_bind()
    multiple_cooks = connection.execute(
        sa.text(
            "SELECT plan_id FROM dinner_plan_item GROUP BY plan_id "
            "HAVING COUNT(DISTINCT cook_user_id) > 1 LIMIT 1"
        )
    ).first()
    multiple_rewards = connection.execute(
        sa.text(
            "SELECT plan_id FROM feeding_value_entry WHERE plan_id IS NOT NULL "
            "GROUP BY plan_id HAVING COUNT(*) > 1 LIMIT 1"
        )
    ).first()
    if multiple_cooks or multiple_rewards:
        raise RuntimeError("Cannot downgrade plans with multiple cooks or multiple rewards")

    op.add_column("dinner_plan", sa.Column("cook_user_id", ID_TYPE, nullable=True))
    op.add_column("dinner_plan", sa.Column("cook_name", sa.String(64), nullable=True))
    op.execute(
        sa.text(
            "UPDATE dinner_plan SET "
            "cook_user_id = (SELECT cook_user_id FROM dinner_plan_item "
            "WHERE dinner_plan_item.plan_id = dinner_plan.id ORDER BY id LIMIT 1), "
            "cook_name = (SELECT cook_name FROM dinner_plan_item "
            "WHERE dinner_plan_item.plan_id = dinner_plan.id ORDER BY id LIMIT 1)"
        )
    )
    with op.batch_alter_table("dinner_plan") as batch:
        batch.alter_column("cook_user_id", existing_type=ID_TYPE, nullable=False)
        batch.alter_column("cook_name", existing_type=sa.String(64), nullable=False)
        batch.create_foreign_key("fk_dinner_plan_cook_user_id", "app_user", ["cook_user_id"], ["id"])
    with op.batch_alter_table("dinner_plan_item") as batch:
        batch.drop_constraint("fk_dinner_plan_item_cook_user_id", type_="foreignkey")
        batch.drop_column("cook_name")
        batch.drop_column("cook_user_id")
    with op.batch_alter_table("feeding_value_entry") as batch:
        batch.drop_constraint("uq_feeding_value_entry_plan_user", type_="unique")
        batch.create_unique_constraint("uq_feeding_value_entry_plan", ["plan_id"])
