import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_food_category_crud_and_soft_delete(client: AsyncClient) -> None:
    created = (
        await client.post("/api/food-categories", json={"name": "家常菜", "sort": 2})
    ).json()["data"]

    assert created["name"] == "家常菜"

    listed = (await client.get("/api/food-categories")).json()["data"]
    assert [item["name"] for item in listed] == ["家常菜"]

    updated = (
        await client.put(f"/api/food-categories/{created['id']}", json={"sort": 1, "name": "热菜"})
    ).json()["data"]
    assert updated["sort"] == 1
    assert updated["name"] == "热菜"

    deleted = (await client.delete(f"/api/food-categories/{created['id']}")).json()["data"]
    assert deleted["is_active"] is False

    assert (await client.get("/api/food-categories")).json()["data"] == []
    inactive_list = (await client.get("/api/food-categories?include_inactive=true")).json()["data"]
    assert len(inactive_list) == 1


@pytest.mark.asyncio
async def test_missing_food_category_returns_not_found_code(client: AsyncClient) -> None:
    payload = (await client.put("/api/food-categories/999", json={"name": "不存在"})).json()

    assert payload["code"] == 40004
