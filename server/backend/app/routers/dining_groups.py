from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.response import AppException, ok
from app.models.dining_group import DiningGroup, DiningGroupMember
from app.models.user import User
from app.schemas.dining_group import (
    DiningGroupCreate,
    DiningGroupJoin,
    DiningGroupMemberNameUpdate,
    DiningGroupMemberOut,
    DiningGroupOut,
)
from app.services.dining_group_service import DiningGroupService

router = APIRouter(prefix="/dining-groups", tags=["dining-groups"])


def group_out(group: DiningGroup) -> dict[str, object]:
    return DiningGroupOut(
        id=group.id,
        name=group.name,
        invite_token=group.invite_token,
        members=[
            DiningGroupMemberOut(
                user_id=item.user_id,
                nickname=item.display_name or item.user.nickname,
                role=item.role,
            )
            for item in group.members
        ],
    ).model_dump(mode="json")


@router.get("/current")
async def current_group(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict[str, object]:
    membership = await DiningGroupService.membership(db, user.id)
    if membership is None:
        return ok(None)
    return ok(group_out(await DiningGroupService.get_group(db, membership.group_id)))


@router.post("")
async def create_group(
    payload: DiningGroupCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    return ok(group_out(await DiningGroupService.create(db, user, payload.name)))


@router.post("/join")
async def join_group(
    payload: DiningGroupJoin,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    return ok(group_out(await DiningGroupService.join(db, user, payload.invite_token)))


@router.patch("/me")
async def update_my_name(
    payload: DiningGroupMemberNameUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    membership = await DiningGroupService.require_membership(db, user.id)
    target_user_id = payload.user_id or user.id
    target = await db.scalar(
        select(DiningGroupMember).where(
            DiningGroupMember.group_id == membership.group_id,
            DiningGroupMember.user_id == target_user_id,
        )
    )
    if target is None:
        raise AppException(40004, "这个饭搭子成员不存在")
    target.display_name = payload.nickname
    await db.commit()
    return ok(group_out(await DiningGroupService.get_group(db, membership.group_id)))
