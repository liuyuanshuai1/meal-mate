from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models.dinner_plan import DinnerPlan
from app.models.user import User
from app.schemas.dinner_plan import DinnerPlanCreate, DinnerPlanItemOut, DinnerPlanOut
from app.services.dinner_plan_service import DinnerPlanService

router = APIRouter(prefix="/dinner-plans", tags=["dinner-plans"])


def plan_out(plan: DinnerPlan, viewer_user_id: int) -> dict[str, object]:
    return DinnerPlanOut(
        id=plan.id,
        group_id=plan.group_id,
        created_by=plan.created_by,
        creator_name=next(
            (
                member.display_name or plan.creator.nickname
                for member in plan.group.members
                if member.user_id == plan.created_by
            ),
            plan.creator.nickname,
        ),
        status=plan.status,
        feeding_total=plan.feeding_total,
        scheduled_for=plan.scheduled_for,
        notification_unread=(
            plan.status == "pending" and plan.created_by != viewer_user_id and plan.partner_seen_at is None
        ),
        created_at=plan.created_at,
        completed_at=plan.completed_at,
        items=[DinnerPlanItemOut.model_validate(item) for item in plan.items],
    ).model_dump(mode="json")


@router.get("/current")
async def current_plan(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict[str, object]:
    plan = await DinnerPlanService.current(db, user.id)
    return ok(plan_out(plan, user.id) if plan else None)


@router.get("/upcoming")
async def upcoming_plans(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict[str, object]:
    plans = await DinnerPlanService.upcoming(db, user.id)
    return ok([plan_out(plan, user.id) for plan in plans])


@router.post("")
async def create_plan(
    payload: DinnerPlanCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    return ok(plan_out(await DinnerPlanService.create(db, user, payload), user.id))


@router.get("/{plan_id}")
async def get_plan(
    plan_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict[str, object]:
    return ok(plan_out(await DinnerPlanService.get(db, user.id, plan_id), user.id))


@router.post("/{plan_id}/seen")
async def mark_plan_seen(
    plan_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict[str, object]:
    return ok(plan_out(await DinnerPlanService.mark_seen(db, user, plan_id), user.id))


@router.post("/{plan_id}/complete")
async def complete_plan(
    plan_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict[str, object]:
    return ok(plan_out(await DinnerPlanService.complete(db, user, plan_id), user.id))


@router.post("/{plan_id}/cancel")
async def cancel_plan(
    plan_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict[str, object]:
    return ok(plan_out(await DinnerPlanService.cancel(db, user, plan_id), user.id))
