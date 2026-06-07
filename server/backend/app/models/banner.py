from sqlalchemy import BigInteger, Boolean, CheckConstraint, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class Banner(TimestampMixin, Base):
    __tablename__ = "banner"
    __table_args__ = (
        CheckConstraint("link_type in ('none', 'food', 'url')", name="ck_banner_link_type"),
        Index("idx_banner_is_active", "is_active"),
        Index("idx_banner_sort", "sort"),
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    link_type: Mapped[str] = mapped_column(String(32), nullable=False, default="none", server_default="none")
    link_target: Mapped[str | None] = mapped_column(String(256), nullable=True)
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
