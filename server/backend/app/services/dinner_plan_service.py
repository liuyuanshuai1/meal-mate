from typing import cast

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload, selectinload

from app.core.response import AppException
from app.core.timezone import now_tz
from app.models.dining_group import DiningGroup, DiningGroupMember
from app.models.dinner_plan import DinnerPlan, DinnerPlanItem
from app.models.eat_record import EatRecord, EatRecordItem
from app.models.feeding_value import FeedingValueEntry
from app.models.food import Food
from app.models.user import User
from app.schemas.dinner_plan import DinnerPlanCreate
from app.services.dining_group_service import DiningGroupService


class DinnerPlanService:
    @staticmethod
    def _query() -> Select[tuple[DinnerPlan]]:
        return select(DinnerPlan).options(
            selectinload(DinnerPlan.items),
            joinedload(DinnerPlan.creator),
            joinedload(DinnerPlan.group).selectinload(DiningGroup.members).joinedload(DiningGroupMember.user),
        )

    @staticmethod
    async def _get_in_group(db: AsyncSession, group_id: int, plan_id: int) -> DinnerPlan:
        plan = await db.scalar(
            DinnerPlanService._query().where(DinnerPlan.id == plan_id, DinnerPlan.group_id == group_id)
        )
        if plan is None:
            raise AppException(40004, "菜单不存在")
        return plan

    @staticmethod
    async def current(db: AsyncSession, user_id: int) -> DinnerPlan | None:
        membership = await DiningGroupService.membership(db, user_id)
        if membership is None:
            return None
        return cast(
            DinnerPlan | None,
            await db.scalar(
                DinnerPlanService._query()
                .where(DinnerPlan.group_id == membership.group_id, DinnerPlan.status == "pending")
                .order_by(DinnerPlan.created_at.desc(), DinnerPlan.id.desc())
                .limit(1)
            ),
        )

    @staticmethod
    async def create(db: AsyncSession, user: User, payload: DinnerPlanCreate) -> DinnerPlan:
        membership = await DiningGroupService.require_membership(db, user.id)
        await db.scalar(select(DiningGroup.id).where(DiningGroup.id == membership.group_id).with_for_update())
        member_count = await db.scalar(
            select(func.count())
            .select_from(DiningGroupMember)
            .where(DiningGroupMember.group_id == membership.group_id)
        )
        if member_count != 2:
            raise AppException(40001, "等饭搭子加入后再发送菜单")
        cook_ids = {item.cook_user_id for item in payload.items}
        cook_members = list(
            (
                await db.scalars(
                    select(DiningGroupMember)
                    .options(joinedload(DiningGroupMember.user))
                    .where(
                        DiningGroupMember.group_id == membership.group_id,
                        DiningGroupMember.user_id.in_(cook_ids),
                    )
                )
            ).all()
        )
        cook_map = {member.user_id: member for member in cook_members}
        if len(cook_map) != len(cook_ids):
            raise AppException(40001, "请为每道菜选择饭搭子中的做菜人")
        food_ids = {item.food_id for item in payload.items}
        foods = list((await db.scalars(select(Food).where(Food.id.in_(food_ids), Food.is_active.is_(True)))).all())
        food_map = {food.id: food for food in foods}
        if len(food_map) != len(food_ids):
            raise AppException(40004, "菜单中有菜品不存在或已下架")

        existing = await db.scalar(
            select(DinnerPlan)
            .options(lazyload(DinnerPlan.items), lazyload(DinnerPlan.creator))
            .where(DinnerPlan.group_id == membership.group_id, DinnerPlan.status == "pending")
            .limit(1)
        )
        if existing is not None:
            existing.status = "cancelled"

        feeding_total = sum(food_map[item.food_id].feeding_value * item.quantity for item in payload.items)
        plan = DinnerPlan(
            group_id=membership.group_id,
            creator=user,
            feeding_total=feeding_total,
            items=[
                DinnerPlanItem(
                    food_id=item.food_id,
                    food_name=food_map[item.food_id].name,
                    food_image_url=food_map[item.food_id].image_url,
                    recipe_cook_minutes=(
                        food_map[item.food_id].cook_minutes
                        if food_map[item.food_id].recipe_status == "published"
                        else None
                    ),
                    recipe_ingredients=(
                        food_map[item.food_id].ingredients
                        if food_map[item.food_id].recipe_status == "published"
                        else []
                    ),
                    recipe_steps=(
                        food_map[item.food_id].recipe_steps
                        if food_map[item.food_id].recipe_status == "published"
                        else []
                    ),
                    quantity=item.quantity,
                    feeding_value=food_map[item.food_id].feeding_value,
                    cook_user_id=item.cook_user_id,
                    cook_name=cook_map[item.cook_user_id].display_name or cook_map[item.cook_user_id].user.nickname,
                )
                for item in payload.items
            ],
        )
        db.add(plan)
        await db.commit()
        return await DinnerPlanService._get_in_group(db, membership.group_id, plan.id)

    @staticmethod
    async def get(db: AsyncSession, user_id: int, plan_id: int) -> DinnerPlan:
        membership = await DiningGroupService.require_membership(db, user_id)
        return await DinnerPlanService._get_in_group(db, membership.group_id, plan_id)

    @staticmethod
    async def complete(db: AsyncSession, user: User, plan_id: int) -> DinnerPlan:
        membership = await DiningGroupService.require_membership(db, user.id)
        await db.scalar(select(DiningGroup.id).where(DiningGroup.id == membership.group_id).with_for_update())
        plan = await DinnerPlanService._get_in_group(db, membership.group_id, plan_id)
        if plan.status != "pending":
            raise AppException(40001, "菜单已处理")
        group = await DiningGroupService.get_group(db, membership.group_id)
        eaten_at = now_tz()
        for member in group.members:
            partner = next((candidate for candidate in group.members if candidate.user_id != member.user_id), None)
            db.add(
                EatRecord(
                    user_id=member.user_id,
                    person=(partner.display_name or partner.user.nickname) if partner else plan.creator.nickname,
                    eaten_at=eaten_at,
                    items=[
                        EatRecordItem(
                            food_id=item.food_id,
                            food_name=item.food_name,
                            food_image_url=item.food_image_url,
                            quantity=item.quantity,
                            feeding_value=item.feeding_value,
                        )
                        for item in plan.items
                    ],
                )
            )
        earned_by_cook: dict[int, int] = {}
        cook_names: dict[int, str] = {}
        for item in plan.items:
            earned_by_cook[item.cook_user_id] = (
                earned_by_cook.get(item.cook_user_id, 0)
                + item.feeding_value * item.quantity
            )
            cook_names[item.cook_user_id] = item.cook_name
        for cook_user_id, earned_value in earned_by_cook.items():
            if earned_value <= 0:
                continue
            db.add(
                FeedingValueEntry(
                    group_id=membership.group_id,
                    user_id=cook_user_id,
                    kind="earn",
                    amount=earned_value,
                    description=f"做菜奖励（{cook_names[cook_user_id]}）",
                    plan_id=plan.id,
                )
            )
        plan.status = "completed"
        plan.completed_at = eaten_at
        await db.commit()
        return plan

    @staticmethod
    async def cancel(db: AsyncSession, user: User, plan_id: int) -> DinnerPlan:
        membership = await DiningGroupService.require_membership(db, user.id)
        await db.scalar(select(DiningGroup.id).where(DiningGroup.id == membership.group_id).with_for_update())
        plan = await DinnerPlanService._get_in_group(db, membership.group_id, plan_id)
        if plan.status != "pending":
            raise AppException(40001, "菜单已处理")
        plan.status = "cancelled"
        await db.commit()
        return plan
