"""use food price as the source for feeding value

Revision ID: 202609300001
Revises: 202609290002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202609300001"
down_revision: str | None = "202609290002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("dinner_plan_item") as batch:
        batch.drop_constraint("ck_dinner_plan_item_feeding_value_non_negative", type_="check")
        batch.drop_column("feeding_value")
    with op.batch_alter_table("food") as batch:
        batch.drop_constraint("ck_food_feeding_value_non_negative", type_="check")
        batch.drop_column("feeding_value")


def downgrade() -> None:
    connection = op.get_bind()
    with op.batch_alter_table("food") as batch:
        batch.add_column(sa.Column("feeding_value", sa.Integer(), server_default="0", nullable=False))
        if connection.dialect.name != "sqlite":
            batch.create_check_constraint("ck_food_feeding_value_non_negative", "feeding_value >= 0")
    with op.batch_alter_table("dinner_plan_item") as batch:
        batch.add_column(sa.Column("feeding_value", sa.Integer(), server_default="0", nullable=False))
        if connection.dialect.name != "sqlite":
            batch.create_check_constraint("ck_dinner_plan_item_feeding_value_non_negative", "feeding_value >= 0")
