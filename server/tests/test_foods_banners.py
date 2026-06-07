import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_food_list_filters_and_detail_down_shelf(client: AsyncClient) -> None:
    category = (
        await client.post("/api/food-categories", json={"name": "主食", "sort": 1})
    ).json()["data"]
    food = (
        await client.post(
            "/api/foods",
            json={
                "category_id": category["id"],
                "name": "牛肉面",
                "price": "28.50",
                "is_recommended": True,
                "sort": 1,
            },
        )
    ).json()["data"]

    recommended = (await client.get("/api/foods?recommended=true&keyword=牛肉")).json()["data"]
    assert recommended["total"] == 1
    assert recommended["items"][0]["id"] == food["id"]

    detail = (await client.get(f"/api/foods/{food['id']}")).json()
    assert detail["code"] == 0

    await client.delete(f"/api/foods/{food['id']}")
    missing = (await client.get(f"/api/foods/{food['id']}")).json()
    assert missing["code"] == 40004


@pytest.mark.asyncio
async def test_banner_crud_and_link_type_validation(client: AsyncClient) -> None:
    invalid = (await client.post("/api/banners", json={"image_url": "/x.jpg", "link_type": "bad"})).json()
    assert invalid["code"] == 40001

    banner = (
        await client.post(
            "/api/banners",
            json={"title": "今晚吃啥", "image_url": "/x.jpg", "link_type": "food", "link_target": "1"},
        )
    ).json()["data"]
    assert banner["link_type"] == "food"

    await client.delete(f"/api/banners/{banner['id']}")
    assert (await client.get("/api/banners")).json()["data"] == []
