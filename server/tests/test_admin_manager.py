from datetime import UTC, datetime, timedelta

import pytest
from app.core.admin_auth import require_admin_basic
from app.main import app
from app.models.banner import Banner
from app.models.eat_record import EatRecord, EatRecordItem
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
async def test_admin_requires_basic_auth(client: AsyncClient) -> None:
    override = app.dependency_overrides.pop(require_admin_basic)
    try:
        response = await client.get("/admin")
        authenticated = await client.get("/admin", auth=("admin", "test-admin-token"))
    finally:
        app.dependency_overrides[require_admin_basic] = override

    assert response.status_code == 401
    assert response.headers["www-authenticate"].startswith("Basic")
    assert authenticated.status_code == 200


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
    admin_headers: dict[str, str],
) -> None:
    category = (
        await client.post("/api/food-categories", json={"name": "主食", "sort": 1}, headers=admin_headers)
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
            "feeding_value": "28",
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
    assert food.feeding_value == 28
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
            "feeding_value": "30",
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
    assert food.feeding_value == 30
    assert food.is_recommended is False
    assert food.is_active is False

    await client.post(
        f"/admin/foods/{food.id}/update",
        data={"name": "番茄牛肉面", "feeding_value": "30", "is_recommended": "1", "is_active": "1", "sort": "1"},
        files={"image_file": ("food.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        follow_redirects=True,
    )
    await db_session.refresh(food)
    assert food.image_url is not None
    assert food.image_url.startswith("/static/uploads/")
    assert food.image_url.endswith(".png")

    invalid_upload = await client.post(
        f"/admin/foods/{food.id}/update",
        data={"name": "番茄牛肉面", "feeding_value": "30", "is_active": "1"},
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
async def test_admin_eat_records_list_detail_delete_and_user_filter(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    record_user_1 = EatRecord(
        user_id=1,
        person="甲用户",
        eaten_at=datetime.now(UTC),
        items=[EatRecordItem(food_name="番茄炒蛋", quantity=2, feeding_value=12)],
    )
    record_user_2 = EatRecord(
        user_id=2,
        person="乙用户",
        eaten_at=datetime.now(UTC),
        items=[EatRecordItem(food_name="米饭", quantity=1, feeding_value=3)],
    )
    db_session.add_all([record_user_1, record_user_2])
    await db_session.commit()

    default_page = await client.get("/admin/eat-records")
    assert default_page.status_code == 200
    assert "番茄炒蛋" not in default_page.text
    assert "甲用户" in default_page.text
    assert "乙用户" not in default_page.text

    user_2_page = await client.get("/admin/eat-records?user_id=2")
    assert user_2_page.status_code == 200
    assert "乙用户" in user_2_page.text
    assert "甲用户" not in user_2_page.text
    assert f"/admin/eat-records/{record_user_2.id}?user_id=2" in user_2_page.text

    detail = await client.get(f"/admin/eat-records/{record_user_1.id}?user_id=1")
    assert detail.status_code == 200
    assert "番茄炒蛋" in detail.text
    assert "24" in detail.text

    invalid_user = await client.get("/admin/eat-records?user_id=abc")
    assert invalid_user.status_code == 400
    assert "参数错误" in invalid_user.text

    deleted_page = await client.post(
        f"/admin/eat-records/{record_user_1.id}/delete",
        data={"user_id": "1"},
        follow_redirects=True,
    )
    assert deleted_page.status_code == 200
    assert "甲用户" not in deleted_page.text
    assert await db_session.get(EatRecord, record_user_1.id) is None


@pytest.mark.asyncio
async def test_admin_eat_records_are_paginated(client: AsyncClient, db_session: AsyncSession) -> None:
    started_at = datetime.now(UTC)
    db_session.add_all(
        [
            EatRecord(
                user_id=1,
                person=f"记录-{index:02d}",
                eaten_at=started_at + timedelta(minutes=index),
            )
            for index in range(51)
        ]
    )
    await db_session.commit()

    first_page = await client.get("/admin/eat-records?user_id=1")
    second_page = await client.get("/admin/eat-records?user_id=1&page=2")

    assert "记录-50" in first_page.text
    assert "记录-00" not in first_page.text
    assert "记录-00" in second_page.text
    assert "第 2 / 2 页" in second_page.text
