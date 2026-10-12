from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.dining_group import DiningGroup
    from app.models.user import User


class DinnerPlan(TimestampMixin, Base):
    __tablename__ = "dinner_plan"
    __table_args__ = (
        CheckConstraint("status in ('pending', 'completed', 'cancelled')", name="ck_dinner_plan_status"),
        Index("idx_dinner_plan_group_status_created", "group_id", "status", "created_at", "id"),
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    group_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), ForeignKey("dining_group.id", ondelete="CASCADE"), index=True
    )
    created_by: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), ForeignKey("app_user.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending", server_default="pending")
    feeding_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    partner_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    group: Mapped["DiningGroup"] = relationship(back_populates="plans")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by], lazy="joined")
    items: Mapped[list["DinnerPlanItem"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan", lazy="selectin"
    )


class DinnerPlanItem(TimestampMixin, Base):
    __tablename__ = "dinner_plan_item"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_dinner_plan_item_quantity_positive"),
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), ForeignKey("dinner_plan.id", ondelete="CASCADE"), nullable=False
    )
    food_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), ForeignKey("food.id"), nullable=False
    )
    food_name: Mapped[str] = mapped_column(String(128), nullable=False)
    food_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    recipe_cook_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recipe_ingredients: Mapped[list[dict[str, str]]] = mapped_column(JSON, nullable=False, default=list)
    recipe_steps: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    feeding_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    cook_user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), ForeignKey("app_user.id"), nullable=False
    )
    cook_name: Mapped[str] = mapped_column(String(64), nullable=False)

    plan: Mapped[DinnerPlan] = relationship(back_populates="items")
