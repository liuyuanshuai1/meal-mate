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
                cook_minutes=15,
                ingredients=[
                    {"name": "番茄", "amount": "2个"},
                    {"name": "鸡蛋", "amount": "3个"},
                    {"name": "食用油", "amount": "适量"},
                    {"name": "盐", "amount": "少许"},
                ],
                recipe_steps=[
                    "番茄切块，鸡蛋打散。",
                    "热锅加油，先炒熟鸡蛋盛出。",
                    "炒软番茄，加入鸡蛋和盐，翻匀即可。",
                ],
                recipe_status="published",
                is_recommended=True,
                sort=10,
            ),
            Food(
                category_id=categories[1].id,
                name="牛肉面",
                description="汤面一碗，今晚稳了",
                feeding_value=28,
                cook_minutes=30,
                ingredients=[
                    {"name": "面条", "amount": "2份"},
                    {"name": "牛肉", "amount": "200克"},
                    {"name": "青菜", "amount": "适量"},
                    {"name": "高汤", "amount": "适量"},
                ],
                recipe_steps=["牛肉切片，青菜洗净。", "高汤煮开后下牛肉和面条。", "面条快熟时放入青菜，调味后盛出。"],
                recipe_status="published",
                is_recommended=True,
                sort=20,
            ),
            Food(
                category_id=categories[2].id,
                name="柠檬茶",
                description="清爽一点",
                feeding_value=12,
                sort=30,
                cook_minutes=5,
                ingredients=[{"name": "柠檬", "amount": "半个"}, {"name": "红茶", "amount": "1杯"}],
                recipe_steps=["红茶泡好并放凉。", "柠檬切片，放入茶中即可。"],
                recipe_status="published",
            ),
            Food(
                category_id=categories[3].id,
                name="煎饺",
                description="外脆里香",
                feeding_value=16,
                sort=40,
                cook_minutes=12,
                ingredients=[
                    {"name": "饺子", "amount": "10个"},
                    {"name": "食用油", "amount": "少许"},
                    {"name": "水", "amount": "半碗"},
                ],
                recipe_steps=[
                    "平底锅加少许油，摆入饺子。",
                    "煎至底部微黄，倒入半碗水并盖盖焖熟。",
                    "水收干后开盖再煎一会儿即可。",
                ],
                recipe_status="published",
            ),
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
