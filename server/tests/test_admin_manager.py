from decimal import Decimal

import pytest
from app.models.banner import Banner
from app.models.food import Food
from app.models.food_category import FoodCategory
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_admin_index_has_module_links(client: AsyncClient) -> None:
    response = await client.get("/admin")

    assert response.status_code == 200
    assert "/admin/categories" in response.text
    assert "/admin/foods" in response.text
    assert "/admin/banners" in response.text
    assert "/admin/eat-records" in response.text


@pytest.mark.asyncio
async def test_admin_category_create_update_delete_and_api_filter(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    assert (await client.get("/admin/categories")).status_code == 200

    created_page = await client.post(
        "/admin/categories",
        data={"name": "  热菜  ", "sort": "2", "is_active": "1"},
        follow_redirects=True,
    )
    assert created_page.status_code == 200
    assert "热菜" in created_page.text

    category = await db_session.scalar(select(FoodCategory).where(FoodCategory.name == "热菜"))
    assert category is not None

    updated_page = await client.post(
        f"/admin/categories/{category.id}/update",
        data={"name": "家常菜", "sort": "5"},
        follow_redirects=True,
    )
    assert updated_page.status_code == 200
    await db_session.refresh(category)
    assert category.name == "家常菜"
    assert category.sort == 5
    assert category.is_active is False

    await client.post(
        f"/admin/categories/{category.id}/update",
        data={"name": "家常菜", "sort": "5", "is_active": "1"},
        follow_redirects=True,
    )
    await db_session.refresh(category)
    assert category.is_active is True

    deleted_page = await client.post(f"/admin/categories/{category.id}/delete", follow_redirects=True)
    assert deleted_page.status_code == 200
    await db_session.refresh(category)
    assert category.is_active is False

    api_categories = (await client.get("/api/food-categories")).json()["data"]
    assert all(item["id"] != category.id for item in api_categories)


@pytest.mark.asyncio
async def test_admin_food_create_update_upload_delete_and_api_filters(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    category = (
        await client.post("/api/food-categories", json={"name": "主食", "sort": 1})
    ).json()["data"]

    list_page = await client.get("/admin/foods")
    assert list_page.status_code == 200

    created_page = await client.post(
        "/admin/foods",
        data={
            "category_id": str(category["id"]),
            "name": "牛肉面",
            "description": "热乎",
            "image_url": "/static/uploads/noodle.jpg",
            "price": "28.50",
            "is_recommended": "1",
            "is_active": "1",
            "sort": "3",
        },
        follow_redirects=True,
    )
    assert created_page.status_code == 200
    assert "牛肉面" in created_page.text

    food = await db_session.scalar(select(Food).where(Food.name == "牛肉面"))
    assert food is not None
    assert food.category_id == category["id"]
    assert food.price == Decimal("28.50")
    assert food.is_recommended is True
    assert food.is_active is True
    assert food.sort == 3

    updated_page = await client.post(
        f"/admin/foods/{food.id}/update",
        data={
            "category_id": "",
            "name": "番茄牛肉面",
            "description": "",
            "image_url": "",
            "price": "30",
            "sort": "1",
        },
        follow_redirects=True,
    )
    assert updated_page.status_code == 200
    await db_session.refresh(food)
    assert food.name == "番茄牛肉面"
    assert food.category_id is None
    assert food.description is None
    assert food.image_url is None
    assert food.price == Decimal("30.00")
    assert food.is_recommended is False
    assert food.is_active is False

    await client.post(
        f"/admin/foods/{food.id}/update",
        data={"name": "番茄牛肉面", "price": "30", "is_recommended": "1", "is_active": "1", "sort": "1"},
        files={"image_file": ("food.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        follow_redirects=True,
    )
    await db_session.refresh(food)
    assert food.image_url is not None
    assert food.image_url.startswith("/static/uploads/")
    assert food.image_url.endswith(".png")

    invalid_upload = await client.post(
        f"/admin/foods/{food.id}/update",
        data={"name": "番茄牛肉面", "price": "30", "is_active": "1"},
        files={"image_file": ("food.gif", b"gif", "image/gif")},
    )
    assert invalid_upload.status_code == 200
    assert "只允许上传 jpg、png 或 webp 图片" in invalid_upload.text

    recommended = (await client.get("/api/foods?recommended=true")).json()["data"]
    assert [item["id"] for item in recommended["items"]] == [food.id]

    deleted_page = await client.post(f"/admin/foods/{food.id}/delete", follow_redirects=True)
    assert deleted_page.status_code == 200
    assert "番茄牛肉面" not in deleted_page.text
    await db_session.refresh(food)
    assert food.is_active is False
    api_foods = (await client.get("/api/foods")).json()["data"]
    assert all(item["id"] != food.id for item in api_foods["items"])


@pytest.mark.asyncio
async def test_admin_banner_create_update_invalid_link_type_delete_and_api_filter(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    assert (await client.get("/admin/banners")).status_code == 200

    created_page = await client.post(
        "/admin/banners",
        data={
            "title": "今晚推荐",
            "image_url": "/static/uploads/banner.jpg",
            "link_type": "food",
            "link_target": "1",
            "sort": "2",
            "is_active": "1",
        },
        follow_redirects=True,
    )
    assert created_page.status_code == 200
    assert "今晚推荐" in created_page.text

    banner = await db_session.scalar(select(Banner).where(Banner.title == "今晚推荐"))
    assert banner is not None

    updated_page = await client.post(
        f"/admin/banners/{banner.id}/update",
        data={
            "title": "周末推荐",
            "image_url": "/static/uploads/weekend.jpg",
            "link_type": "url",
            "link_target": "https://example.com",
            "sort": "8",
        },
        follow_redirects=True,
    )
    assert updated_page.status_code == 200
    await db_session.refresh(banner)
    assert banner.title == "周末推荐"
    assert banner.link_type == "url"
    assert banner.link_target == "https://example.com"
    assert banner.sort == 8
    assert banner.is_active is False

    invalid = await client.post(
        f"/admin/banners/{banner.id}/update",
        data={"title": "坏跳转", "image_url": "/x.jpg", "link_type": "bad"},
    )
    assert invalid.status_code == 200
    assert "参数错误" in invalid.text

    await client.post(f"/admin/banners/{banner.id}/delete", follow_redirects=True)
    await db_session.refresh(banner)
    assert banner.is_active is False
    assert (await client.get("/api/banners")).json()["data"] == []


@pytest.mark.asyncio
async def test_admin_eat_records_list_detail_delete_and_user_filter(client: AsyncClient) -> None:
    record_user_1 = (
        await client.post(
                "/api/eat-records",
                json={
                    "user_id": 1,
                    "person": "甲用户",
                    "items": [{"food_id": 1, "food_name": "番茄炒蛋", "quantity": 2, "price": "12.50"}],
                },
            )
    ).json()["data"]
    record_user_2 = (
        await client.post(
                "/api/eat-records",
                json={
                    "user_id": 2,
                    "person": "乙用户",
                    "items": [{"food_id": 2, "food_name": "米饭", "quantity": 1, "price": "3.00"}],
                },
            )
    ).json()["data"]

    default_page = await client.get("/admin/eat-records")
    assert default_page.status_code == 200
    assert "番茄炒蛋" not in default_page.text
    assert "甲用户" in default_page.text
    assert "乙用户" not in default_page.text

    user_2_page = await client.get("/admin/eat-records?user_id=2")
    assert user_2_page.status_code == 200
    assert "乙用户" in user_2_page.text
    assert "甲用户" not in user_2_page.text
    assert f"/admin/eat-records/{record_user_2['id']}?user_id=2" in user_2_page.text

    detail = await client.get(f"/admin/eat-records/{record_user_1['id']}?user_id=1")
    assert detail.status_code == 200
    assert "番茄炒蛋" in detail.text
    assert "25.00" in detail.text

    invalid_user = await client.get("/admin/eat-records?user_id=abc")
    assert invalid_user.status_code == 400
    assert "参数错误" in invalid_user.text

    deleted_page = await client.post(
        f"/admin/eat-records/{record_user_1['id']}/delete",
        data={"user_id": "1"},
        follow_redirects=True,
    )
    assert deleted_page.status_code == 200
    assert "甲用户" not in deleted_page.text
    assert (await client.get("/api/eat-records?user_id=1")).json()["data"]["total"] == 0
