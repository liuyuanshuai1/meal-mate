from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.dinner_plan import DinnerPlan
    from app.models.user import User


class DiningGroup(TimestampMixin, Base):
    __tablename__ = "dining_group"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, default="我们的饭搭子", server_default="我们的饭搭子")
    invite_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    members: Mapped[list["DiningGroupMember"]] = relationship(
        back_populates="group", cascade="all, delete-orphan", lazy="selectin"
    )
    plans: Mapped[list["DinnerPlan"]] = relationship(back_populates="group")


class DiningGroupMember(TimestampMixin, Base):
    __tablename__ = "dining_group_member"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_dining_group_member"),)

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    group_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), ForeignKey("dining_group.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("app_user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="member", server_default="member")
    display_name: Mapped[str | None] = mapped_column(String(64), nullable=True)

    group: Mapped[DiningGroup] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="membership", lazy="joined")
