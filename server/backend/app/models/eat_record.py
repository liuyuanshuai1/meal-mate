from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.food import Food


class EatRecord(TimestampMixin, Base):
    __tablename__ = "eat_record"
    __table_args__ = (
        CheckConstraint("user_id > 0", name="ck_eat_record_user_id_positive"),
        CheckConstraint("total_price >= 0", name="ck_eat_record_total_price_non_negative"),
        Index("idx_eat_record_user_id", "user_id"),
        Index("idx_eat_record_eaten_at", "eaten_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    person: Mapped[str] = mapped_column(String(64), nullable=False, default="default", server_default="default")
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    eaten_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    items: Mapped[list["EatRecordItem"]] = relationship(
        back_populates="record",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class EatRecordItem(TimestampMixin, Base):
    __tablename__ = "eat_record_item"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_eat_record_item_quantity_positive"),
        CheckConstraint("price >= 0", name="ck_eat_record_item_price_non_negative"),
        Index("idx_eat_record_item_record_id", "record_id"),
        Index("idx_eat_record_item_food_id", "food_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    record_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("eat_record.id", ondelete="CASCADE"),
        nullable=False,
    )
    food_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("food.id"),
        nullable=True,
    )
    food_name: Mapped[str] = mapped_column(String(128), nullable=False)
    food_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    record: Mapped[EatRecord] = relationship(back_populates="items")
    food: Mapped["Food | None"] = relationship(back_populates="eat_record_items")
