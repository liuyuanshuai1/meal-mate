from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.dining_group import DiningGroupMember


class User(TimestampMixin, Base):
    __tablename__ = "app_user"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    openid: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    nickname: Mapped[str] = mapped_column(String(64), nullable=False, default="饭搭子", server_default="饭搭子")

    membership: Mapped["DiningGroupMember | None"] = relationship(back_populates="user", uselist=False)
