"""add editable food recipes

Revision ID: 202610110001
Revises: 202609300002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202610110001"
down_revision: str | None = "202609300002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("food", sa.Column("cook_minutes", sa.Integer(), nullable=True))
    op.add_column("food", sa.Column("ingredients", sa.JSON(), server_default="[]", nullable=False))
    op.add_column("food", sa.Column("recipe_steps", sa.JSON(), server_default="[]", nullable=False))
    op.add_column("food", sa.Column("recipe_status", sa.String(16), server_default="draft", nullable=False))


def downgrade() -> None:
    op.drop_column("food", "recipe_status")
    op.drop_column("food", "recipe_steps")
    op.drop_column("food", "ingredients")
    op.drop_column("food", "cook_minutes")
