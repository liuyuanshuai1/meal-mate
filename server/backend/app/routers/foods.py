from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import AppException, ok
from app.models.food import Food
from app.schemas.common import PageResult
from app.schemas.food import FoodCreate, FoodOut, FoodUpdate, ImageUploadOut
from app.services.image_upload import save_upload_image

router = APIRouter(prefix="/foods", tags=["foods"])

@router.get("")
async def list_foods(
    category_id: int | None = None,
    recommended: bool | None = None,
    keyword: str | None = None,
    include_inactive: bool = False,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    if page < 1 or page_size < 1 or page_size > 100:
        raise AppException(40001, "分页参数错误")

    stmt = select(Food)
    count_stmt = select(func.count()).select_from(Food)
    conditions = []
    if category_id is not None:
        conditions.append(Food.category_id == category_id)
    if recommended is not None:
        conditions.append(Food.is_recommended.is_(recommended))
    if keyword:
        conditions.append(Food.name.ilike(f"%{keyword}%"))
    if not include_inactive:
        conditions.append(Food.is_active.is_(True))
    for condition in conditions:
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    total = await db.scalar(count_stmt)
    rows = (
        await db.scalars(
            stmt.order_by(Food.sort.asc(), Food.id.asc()).offset((page - 1) * page_size).limit(page_size),
        )
    ).all()
    items = [FoodOut.model_validate(row).model_dump(mode="json") for row in rows]
    page_data = PageResult(items=items, total=total or 0, page=page, page_size=page_size)
    return ok(page_data.model_dump(mode="json"))


@router.get("/{food_id}")
async def get_food(food_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    food = await db.get(Food, food_id)
    if food is None or not food.is_active:
        raise AppException(40004, "菜品不存在或已下架")
    return ok(FoodOut.model_validate(food).model_dump(mode="json"))


@router.post("")
async def create_food(payload: FoodCreate, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    food = Food(**payload.model_dump())
    db.add(food)
    await db.commit()
    await db.refresh(food)
    return ok(FoodOut.model_validate(food).model_dump(mode="json"))


@router.put("/{food_id}")
async def update_food(food_id: int, payload: FoodUpdate, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    food = await db.get(Food, food_id)
    if food is None:
        raise AppException(40004, "菜品不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(food, key, value)
    await db.commit()
    await db.refresh(food)
    return ok(FoodOut.model_validate(food).model_dump(mode="json"))


@router.delete("/{food_id}")
async def delete_food(food_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    food = await db.get(Food, food_id)
    if food is None:
        raise AppException(40004, "菜品不存在")
    food.is_active = False
    await db.commit()
    await db.refresh(food)
    return ok(FoodOut.model_validate(food).model_dump(mode="json"))


@router.post("/image")
async def upload_food_image(file: UploadFile = File(...)) -> dict[str, object]:
    image_url = await save_upload_image(file)
    return ok(ImageUploadOut(image_url=image_url).model_dump())
