import asyncio

from app.core.database import SessionLocal
from app.models.banner import Banner
from app.models.food import Food
from app.models.food_category import FoodCategory
from sqlalchemy import select


async def seed() -> None:
    async with SessionLocal() as db:
        existing = await db.scalar(select(FoodCategory).limit(1))
        if existing is not None:
            return

        categories = [
            FoodCategory(name="家常菜", sort=10),
            FoodCategory(name="主食", sort=20),
            FoodCategory(name="饮品", sort=30),
            FoodCategory(name="小吃", sort=40),
        ]
        db.add_all(categories)
        await db.flush()

        foods = [
            Food(
                category_id=categories[0].id,
                name="番茄炒蛋",
                description="酸甜热乎的家常菜",
                feeding_value=18,
                is_recommended=True,
                sort=10,
            ),
            Food(
                category_id=categories[1].id,
                name="牛肉面",
                description="汤面一碗，今晚稳了",
                feeding_value=28,
                is_recommended=True,
                sort=20,
            ),
            Food(category_id=categories[2].id, name="柠檬茶", description="清爽一点", feeding_value=12, sort=30),
            Food(category_id=categories[3].id, name="煎饺", description="外脆里香", feeding_value=16, sort=40),
        ]
        db.add_all(foods)
        await db.flush()

        db.add(
            Banner(
                title="今晚吃点热乎的",
                image_url="/static/uploads/default-banner.jpg",
                link_type="food",
                link_target=str(foods[0].id),
                sort=10,
            ),
        )
        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
