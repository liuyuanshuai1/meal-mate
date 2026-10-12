from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from pydantic import ValidationError
from sqlalchemy import Date, bindparam, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.response import AppException, ok
from app.models.food import Food
from app.models.user import User
from app.schemas.recipe_exploration import ExploredRecipe, ExploreIn
from app.services.deepseek import request_json

router = APIRouter(prefix="/recipes", tags=["recipes"])

EXPLORE_PROMPT = """你是家常菜做法助手。根据用户现有食材和要求，生成两到三道适合在家制作的菜。
优先使用用户提到的食材；用户明确提出的忌口和口味要求必须遵守。
不要生成与已有菜单同名的菜，也不要冒充已有菜单菜品。
做法要具体，写清食材用量、预计时间、份数和每一步。
需要但用户没提到的食材放入 missing_ingredients，且这些食材也要在 ingredients 中。
不要声称热量、过敏风险或营养功效已经核实。生肉和海鲜的步骤必须写明充分做熟。
只返回 JSON，格式为 {"items":[{"name":"菜名","reason":"推荐理由","cook_minutes":20,
"servings":2,"ingredients":[{"name":"食材","amount":"用量"}],"steps":["步骤一","步骤二"],
"missing_ingredients":["还需要的食材"]}]}。如果没有合适做法，返回 {"items":[]}。"""


def normalize_name(value: str) -> str:
    return "".join(value.split()).casefold()


async def reserve_exploration(db: AsyncSession, user_id: int) -> None:
    settings = get_settings()
    day = datetime.now(ZoneInfo(settings.tz)).date()
    statement = text(
        """INSERT INTO ai_explore_usage (user_id, day, request_count)
        VALUES (:user_id, :day, 1)
        ON CONFLICT (user_id, day) DO UPDATE
        SET request_count = ai_explore_usage.request_count + 1
        WHERE ai_explore_usage.request_count < :daily_limit
        RETURNING request_count"""
    ).bindparams(bindparam("day", type_=Date()))
    count = await db.scalar(
        statement,
        {"user_id": user_id, "day": day, "daily_limit": settings.ai_explore_daily_limit},
    )
    await db.commit()
    if count is None:
        raise AppException(42900, "今天的探索次数已用完，明天再试")


@router.post("/explore")
async def explore_recipes(
    payload: ExploreIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    request_text = payload.text.strip()
    if len(request_text) < 2:
        raise AppException(40001, "说说你有什么食材，或想吃什么")

    existing_names = list(
        (await db.scalars(select(Food.name).where(Food.is_active.is_(True)).order_by(Food.id).limit(200))).all()
    )
    await reserve_exploration(db, user.id)
    generated = await request_json(
        EXPLORE_PROMPT,
        {"request": request_text, "existing_menu_names": existing_names},
        max_tokens=3000,
        timeout=45,
    )
    proposed = generated.get("items")
    if not isinstance(proposed, list):
        raise AppException(50300, "暂时无法生成做法，请重试")

    known_names = {normalize_name(name) for name in existing_names}
    items = []
    for raw in proposed[:4]:
        try:
            recipe = ExploredRecipe.model_validate(raw)
        except ValidationError:
            continue
        name_key = normalize_name(recipe.name)
        if name_key in known_names:
            continue
        ingredient_names = {normalize_name(ingredient.name) for ingredient in recipe.ingredients}
        if any(normalize_name(name) not in ingredient_names for name in recipe.missing_ingredients):
            continue
        known_names.add(name_key)
        items.append(recipe.model_dump())
        if len(items) == 3:
            break

    if proposed and not items:
        raise AppException(50300, "暂时没有生成合适的新做法，换个说法试试")
    return ok({"items": items, "message": "" if items else "暂时没想到合适的新做法，换个说法试试"})
