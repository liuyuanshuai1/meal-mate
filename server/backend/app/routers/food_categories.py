from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import AppException, ok
from app.models.food_category import FoodCategory
from app.schemas.food_category import FoodCategoryCreate, FoodCategoryOut, FoodCategoryUpdate

router = APIRouter(prefix="/food-categories", tags=["food-categories"])


@router.get("")
async def list_food_categories(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    stmt = select(FoodCategory)
    if not include_inactive:
        stmt = stmt.where(FoodCategory.is_active.is_(True))
    stmt = stmt.order_by(FoodCategory.sort.asc(), FoodCategory.id.asc())
    rows = (await db.scalars(stmt)).all()
    data = [FoodCategoryOut.model_validate(row).model_dump(mode="json") for row in rows]
    return ok(data)


@router.post("")
async def create_food_category(payload: FoodCategoryCreate, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    category = FoodCategory(**payload.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return ok(FoodCategoryOut.model_validate(category).model_dump(mode="json"))


@router.put("/{category_id}")
async def update_food_category(
    category_id: int,
    payload: FoodCategoryUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    category = await db.get(FoodCategory, category_id)
    if category is None:
        raise AppException(40004, "分类不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return ok(FoodCategoryOut.model_validate(category).model_dump(mode="json"))


@router.delete("/{category_id}")
async def delete_food_category(category_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    category = await db.get(FoodCategory, category_id)
    if category is None:
        raise AppException(40004, "分类不存在")
    category.is_active = False
    await db.commit()
    await db.refresh(category)
    return ok(FoodCategoryOut.model_validate(category).model_dump(mode="json"))
