from secrets import token_urlsafe
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload, selectinload

from app.core.response import AppException
from app.models.dining_group import DiningGroup, DiningGroupMember
from app.models.user import User


class DiningGroupService:
    @staticmethod
    async def membership(db: AsyncSession, user_id: int) -> DiningGroupMember | None:
        return cast(
            DiningGroupMember | None,
            await db.scalar(
                select(DiningGroupMember)
                .options(
                    lazyload(DiningGroupMember.group),
                    lazyload(DiningGroupMember.user),
                )
                .where(DiningGroupMember.user_id == user_id)
            ),
        )

    @staticmethod
    async def require_membership(db: AsyncSession, user_id: int) -> DiningGroupMember:
        membership = await DiningGroupService.membership(db, user_id)
        if membership is None:
            raise AppException(40004, "请先创建或加入饭搭子")
        return membership

    @staticmethod
    async def create(db: AsyncSession, user: User, name: str) -> DiningGroup:
        if await DiningGroupService.membership(db, user.id):
            raise AppException(40001, "你已经有饭搭子了")
        group = DiningGroup(
            name=name.strip(),
            invite_token=token_urlsafe(24),
            members=[DiningGroupMember(user_id=user.id, role="owner")],
        )
        db.add(group)
        await db.commit()
        return await DiningGroupService.get_group(db, group.id)

    @staticmethod
    async def join(db: AsyncSession, user: User, invite_token: str) -> DiningGroup:
        if await DiningGroupService.membership(db, user.id):
            raise AppException(40001, "你已经有饭搭子了")
        group_id = await db.scalar(
            select(DiningGroup.id).where(DiningGroup.invite_token == invite_token).with_for_update()
        )
        if group_id is None:
            raise AppException(40004, "邀请不存在")
        member_count = await db.scalar(
            select(func.count()).select_from(DiningGroupMember).where(DiningGroupMember.group_id == group_id)
        )
        if (member_count or 0) >= 2:
            raise AppException(40001, "这个饭搭子已经满员")
        db.add(DiningGroupMember(group_id=group_id, user_id=user.id))
        await db.commit()
        db.expire_all()
        return await DiningGroupService.get_group(db, group_id)

    @staticmethod
    async def get_group(db: AsyncSession, group_id: int) -> DiningGroup:
        group = await db.scalar(
            select(DiningGroup)
            .options(selectinload(DiningGroup.members).joinedload(DiningGroupMember.user))
            .where(DiningGroup.id == group_id)
        )
        if group is None:
            raise AppException(40004, "饭搭子不存在")
        return group
