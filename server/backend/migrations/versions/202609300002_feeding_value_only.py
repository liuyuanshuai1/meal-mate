"""use feeding values without dish prices

Revision ID: 202609300002
Revises: 202609300001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202609300002"
down_revision: str | None = "202609300001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()
    sqlite = connection.dialect.name == "sqlite"
    checks = {
        table: {item["name"] for item in sa.inspect(connection).get_check_constraints(table)}
        for table in ("food", "dinner_plan", "dinner_plan_item", "eat_record", "eat_record_item")
    }
    op.add_column("food", sa.Column("feeding_value", sa.Integer(), server_default="0", nullable=False))
    op.execute(sa.text("UPDATE food SET feeding_value = CAST(ROUND(price, 0) AS INTEGER)"))
    with op.batch_alter_table("food") as batch:
        if "ck_food_price_non_negative" in checks["food"]:
            batch.drop_constraint("ck_food_price_non_negative", type_="check")
        batch.drop_column("price")
        if not sqlite:
            batch.create_check_constraint("ck_food_feeding_value_non_negative", "feeding_value >= 0")

    op.add_column("dinner_plan_item", sa.Column("feeding_value", sa.Integer(), server_default="0", nullable=False))
    op.execute(sa.text("UPDATE dinner_plan_item SET feeding_value = CAST(ROUND(price, 0) AS INTEGER)"))
    with op.batch_alter_table("dinner_plan_item") as batch:
        if "ck_dinner_plan_item_price_non_negative" in checks["dinner_plan_item"]:
            batch.drop_constraint("ck_dinner_plan_item_price_non_negative", type_="check")
        batch.drop_column("price")
        if not sqlite:
            batch.create_check_constraint("ck_dinner_plan_item_feeding_value_non_negative", "feeding_value >= 0")

    op.add_column("dinner_plan", sa.Column("feeding_total", sa.Integer(), server_default="0", nullable=False))
    op.execute(
        sa.text(
            "UPDATE dinner_plan SET feeding_total = COALESCE("
            "(SELECT SUM(feeding_value * quantity) FROM dinner_plan_item WHERE plan_id = dinner_plan.id), 0)"
        )
    )
    with op.batch_alter_table("dinner_plan") as batch:
        if "ck_dinner_plan_total_price_non_negative" in checks["dinner_plan"]:
            batch.drop_constraint("ck_dinner_plan_total_price_non_negative", type_="check")
        batch.drop_column("total_price")

    op.add_column("eat_record_item", sa.Column("feeding_value", sa.Integer(), server_default="0", nullable=False))
    op.execute(sa.text("UPDATE eat_record_item SET feeding_value = CAST(ROUND(price, 0) AS INTEGER)"))
    with op.batch_alter_table("eat_record_item") as batch:
        if "ck_eat_record_item_price_non_negative" in checks["eat_record_item"]:
            batch.drop_constraint("ck_eat_record_item_price_non_negative", type_="check")
        batch.drop_column("price")
    with op.batch_alter_table("eat_record") as batch:
        if "ck_eat_record_total_price_non_negative" in checks["eat_record"]:
            batch.drop_constraint("ck_eat_record_total_price_non_negative", type_="check")
        batch.drop_column("total_price")


def downgrade() -> None:
    connection = op.get_bind()
    sqlite = connection.dialect.name == "sqlite"
    op.add_column("food", sa.Column("price", sa.Numeric(10, 2), server_default="0", nullable=False))
    op.execute(sa.text("UPDATE food SET price = feeding_value"))
    with op.batch_alter_table("food") as batch:
        if not sqlite:
            batch.drop_constraint("ck_food_feeding_value_non_negative", type_="check")
        batch.drop_column("feeding_value")
        if not sqlite:
            batch.create_check_constraint("ck_food_price_non_negative", "price >= 0")

    op.add_column("dinner_plan_item", sa.Column("price", sa.Numeric(10, 2), server_default="0", nullable=False))
    op.execute(sa.text("UPDATE dinner_plan_item SET price = feeding_value"))
    with op.batch_alter_table("dinner_plan_item") as batch:
        if not sqlite:
            batch.drop_constraint("ck_dinner_plan_item_feeding_value_non_negative", type_="check")
        batch.drop_column("feeding_value")
        if not sqlite:
            batch.create_check_constraint("ck_dinner_plan_item_price_non_negative", "price >= 0")

    op.add_column("dinner_plan", sa.Column("total_price", sa.Numeric(10, 2), server_default="0", nullable=False))
    op.execute(sa.text("UPDATE dinner_plan SET total_price = feeding_total"))
    with op.batch_alter_table("dinner_plan") as batch:
        batch.drop_column("feeding_total")
        if not sqlite:
            batch.create_check_constraint("ck_dinner_plan_total_price_non_negative", "total_price >= 0")

    op.add_column("eat_record_item", sa.Column("price", sa.Numeric(10, 2), server_default="0", nullable=False))
    op.execute(sa.text("UPDATE eat_record_item SET price = feeding_value"))
    with op.batch_alter_table("eat_record_item") as batch:
        batch.drop_column("feeding_value")
        if not sqlite:
            batch.create_check_constraint("ck_eat_record_item_price_non_negative", "price >= 0")

    op.add_column("eat_record", sa.Column("total_price", sa.Numeric(10, 2), server_default="0", nullable=False))
    op.execute(
        sa.text(
            "UPDATE eat_record SET total_price = COALESCE("
            "(SELECT SUM(price * quantity) FROM eat_record_item WHERE record_id = eat_record.id), 0)"
        )
    )
    with op.batch_alter_table("eat_record") as batch:
        if not sqlite:
            batch.create_check_constraint("ck_eat_record_total_price_non_negative", "total_price >= 0")
