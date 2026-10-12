"""snapshot published recipes on dinner plan items

Revision ID: 202610120002
Revises: 202610120001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202610120002"
down_revision: str | None = "202610120001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("dinner_plan_item", sa.Column("recipe_cook_minutes", sa.Integer(), nullable=True))
    op.add_column("dinner_plan_item", sa.Column("recipe_ingredients", sa.JSON(), server_default="[]", nullable=False))
    op.add_column("dinner_plan_item", sa.Column("recipe_steps", sa.JSON(), server_default="[]", nullable=False))

    connection = op.get_bind()
    food = sa.table(
        "food",
        sa.column("id", sa.BigInteger()),
        sa.column("recipe_status", sa.String()),
        sa.column("cook_minutes", sa.Integer()),
        sa.column("ingredients", sa.JSON()),
        sa.column("recipe_steps", sa.JSON()),
    )
    item = sa.table(
        "dinner_plan_item",
        sa.column("food_id", sa.BigInteger()),
        sa.column("recipe_cook_minutes", sa.Integer()),
        sa.column("recipe_ingredients", sa.JSON()),
        sa.column("recipe_steps", sa.JSON()),
    )
    published = connection.execute(
        sa.select(food.c.id, food.c.cook_minutes, food.c.ingredients, food.c.recipe_steps).where(
            food.c.recipe_status == "published"
        )
    )
    for row in published:
        if not row.cook_minutes or not row.ingredients or not row.recipe_steps:
            continue
        connection.execute(
            sa.update(item)
            .where(item.c.food_id == row.id)
            .values(
                recipe_cook_minutes=row.cook_minutes,
                recipe_ingredients=row.ingredients,
                recipe_steps=row.recipe_steps,
            )
        )


def downgrade() -> None:
    op.drop_column("dinner_plan_item", "recipe_steps")
    op.drop_column("dinner_plan_item", "recipe_ingredients")
    op.drop_column("dinner_plan_item", "recipe_cook_minutes")
