from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.response import AppException, ok
from app.models.dining_group import DiningGroup
from app.models.feeding_value import FeedingReward, FeedingValueEntry
from app.models.user import User
from app.schemas.feeding_value import FeedingRedeem, FeedingRewardCreate
from app.services.dining_group_service import DiningGroupService

router = APIRouter(prefix="/feeding-values", tags=["feeding-values"])


async def current_value(db: AsyncSession, group_id: int, user_id: int) -> int:
    return int(
        await db.scalar(
            select(func.coalesce(func.sum(FeedingValueEntry.amount), 0)).where(
                FeedingValueEntry.group_id == group_id,
                FeedingValueEntry.user_id == user_id,
            )
        )
        or 0
    )


@router.get("")
async def summary(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    membership = await DiningGroupService.require_membership(db, user.id)
    group = await DiningGroupService.get_group(db, membership.group_id)
    balances = []
    for member in group.members:
        balances.append(
            {
                "user_id": member.user_id,
                "nickname": member.display_name or member.user.nickname,
                "balance": await current_value(db, group.id, member.user_id),
            }
        )
    entries = (
        await db.scalars(
            select(FeedingValueEntry)
            .where(FeedingValueEntry.group_id == group.id)
            .order_by(FeedingValueEntry.created_at.desc(), FeedingValueEntry.id.desc())
            .limit(100)
        )
    ).all()
    rewards = (
        await db.scalars(
            select(FeedingReward)
            .where(FeedingReward.group_id == group.id, FeedingReward.is_active.is_(True))
            .order_by(FeedingReward.created_at.asc(), FeedingReward.id.asc())
        )
    ).all()
    return ok(
        {
            "balances": balances,
            "entries": [
                {
                    "id": entry.id,
                    "user_id": entry.user_id,
                    "nickname": next(
                        (item["nickname"] for item in balances if item["user_id"] == entry.user_id), "饭搭子"
                    ),
                    "kind": entry.kind,
                    "amount": entry.amount,
                    "description": entry.description,
                    "created_at": entry.created_at,
                }
                for entry in entries
            ],
            "rewards": [
                {"id": reward.id, "name": reward.name, "cost": reward.cost} for reward in rewards
            ],
        }
    )


@router.post("/rewards")
async def create_reward(
    payload: FeedingRewardCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    membership = await DiningGroupService.require_membership(db, user.id)
    reward = FeedingReward(group_id=membership.group_id, name=payload.name, cost=payload.cost)
    db.add(reward)
    await db.commit()
    await db.refresh(reward)
    return ok({"id": reward.id, "name": reward.name, "cost": reward.cost})


@router.delete("/rewards/{reward_id}")
async def delete_reward(
    reward_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    membership = await DiningGroupService.require_membership(db, user.id)
    reward = await db.scalar(
        select(FeedingReward).where(
            FeedingReward.id == reward_id,
            FeedingReward.group_id == membership.group_id,
            FeedingReward.is_active.is_(True),
        )
    )
    if reward is None:
        raise AppException(40004, "兑换内容不存在")
    reward.is_active = False
    await db.commit()
    return ok()


@router.post("/redeem")
async def redeem(
    payload: FeedingRedeem,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    membership = await DiningGroupService.require_membership(db, user.id)
    await db.scalar(select(DiningGroup.id).where(DiningGroup.id == membership.group_id).with_for_update())
    reward = await db.scalar(
        select(FeedingReward).where(
            FeedingReward.id == payload.reward_id,
            FeedingReward.group_id == membership.group_id,
            FeedingReward.is_active.is_(True),
        )
    )
    if reward is None:
        raise AppException(40004, "兑换内容不存在")
    balance = await current_value(db, membership.group_id, user.id)
    if balance < reward.cost:
        raise AppException(40001, "投喂值还不够哦")
    db.add(
        FeedingValueEntry(
            group_id=membership.group_id,
            user_id=user.id,
            kind="redeem",
            amount=-reward.cost,
            description=f"兑换：{reward.name}",
        )
    )
    await db.commit()
    return ok({"spent": reward.cost, "reward_name": reward.name, "balance": balance - reward.cost})
