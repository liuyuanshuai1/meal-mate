from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.food import Food


class FoodCategory(TimestampMixin, Base):
    __tablename__ = "food_category"
    __table_args__ = (
        Index("idx_food_category_sort", "sort"),
        Index("idx_food_category_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    foods: Mapped[list["Food"]] = relationship(back_populates="category")
