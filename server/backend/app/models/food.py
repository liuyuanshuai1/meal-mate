from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.eat_record import EatRecordItem
    from app.models.food_category import FoodCategory


class Food(TimestampMixin, Base):
    __tablename__ = "food"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_food_price_non_negative"),
        Index("idx_food_category_id", "category_id"),
        Index("idx_food_is_recommended", "is_recommended"),
        Index("idx_food_is_active", "is_active"),
        Index("idx_food_sort", "sort"),
        Index("idx_food_name", "name"),
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    category_id: Mapped[int | None] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("food_category.id"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"), server_default="0")
    is_recommended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    category: Mapped["FoodCategory | None"] = relationship(back_populates="foods")
    eat_record_items: Mapped[list["EatRecordItem"]] = relationship(back_populates="food")
