from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.response import AppException, ok
from app.models.food import Food
from app.models.user import User
from app.schemas.recommendation import RecommendIn
from app.services.deepseek import request_json

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

RECOMMEND_PROMPT = """你是家常菜推荐助手。用户会给出想法和候选菜品 JSON。
只从候选菜品中选最多 3 道符合要求的菜，不能创造菜品或修改食材。
优先使用用户已有食材；如果用户说只用现有食材，则不要推荐需要额外食材的菜。
如果用户明确说不能吃某种食材，必须排除含该食材的菜。
如果没有合适菜品，返回空数组。用简短自然的中文解释每个选择。
仅返回 JSON，例如 {"recommendations":[{"food_id":1,"reason":"鸡蛋和番茄都能用上"}]}。"""


@router.post("")
async def recommend_foods(
    payload: RecommendIn,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    text = payload.text.strip()
    if len(text) < 2:
        raise AppException(40001, "请说说你想吃什么")
    foods = list(
        (
            await db.scalars(
                select(Food)
                .where(Food.is_active.is_(True), Food.recipe_status == "published")
                .order_by(Food.is_recommended.desc(), Food.sort.asc(), Food.id.asc())
                .limit(60)
            )
        ).all()
    )
    foods = [food for food in foods if food.cook_minutes and food.ingredients and food.recipe_steps]
    if not foods:
        return ok({"items": [], "message": "还没有可推荐的菜谱，请先在后台发布做法"})
    candidates = [
        {
            "food_id": food.id,
            "name": food.name,
            "description": food.description,
            "cook_minutes": food.cook_minutes,
            "ingredients": [item["name"] for item in food.ingredients],
        }
        for food in foods
    ]
    result = await request_json(RECOMMEND_PROMPT, {"request": text, "candidates": candidates})
    suggested = result.get("recommendations")
    if not isinstance(suggested, list):
        raise AppException(50300, "推荐结果暂不可用，请重试")
    food_map = {food.id: food for food in foods}
    items = []
    seen = set()
    for item in suggested[:3]:
        if not isinstance(item, dict):
            continue
        food_id, reason = item.get("food_id"), item.get("reason")
        if not isinstance(food_id, int) or food_id not in food_map or food_id in seen:
            continue
        if not isinstance(reason, str) or not reason.strip():
            continue
        seen.add(food_id)
        food = food_map[food_id]
        items.append(
            {
                "food_id": food.id,
                "name": food.name,
                "image_url": food.image_url,
                "cook_minutes": food.cook_minutes,
                "reason": reason.strip()[:100],
            }
        )
    if suggested and not items:
        raise AppException(50300, "推荐结果暂不可用，请重试")
    return ok({"items": items, "message": "" if items else "暂时没有符合要求的菜，换个说法试试"})
