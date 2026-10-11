from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.dining_group import DiningGroup
    from app.models.user import User


class FeedingReward(TimestampMixin, Base):
    __tablename__ = "feeding_reward"
    __table_args__ = (
        CheckConstraint("cost > 0", name="ck_feeding_reward_cost_positive"),
        Index("idx_feeding_reward_group_active", "group_id", "is_active"),
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    group_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), ForeignKey("dining_group.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True, server_default="true")


class FeedingValueEntry(TimestampMixin, Base):
    __tablename__ = "feeding_value_entry"
    __table_args__ = (
        CheckConstraint("amount != 0", name="ck_feeding_value_entry_amount_nonzero"),
        CheckConstraint("kind in ('earn', 'redeem')", name="ck_feeding_value_entry_kind"),
        UniqueConstraint("plan_id", "user_id", name="uq_feeding_value_entry_plan_user"),
        Index("idx_feeding_value_entry_group_user_created", "group_id", "user_id", "created_at", "id"),
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    group_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), ForeignKey("dining_group.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=False)
    plan_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), ForeignKey("dinner_plan.id", ondelete="CASCADE"), nullable=True
    )

    group: Mapped["DiningGroup"] = relationship()
    user: Mapped["User"] = relationship()
