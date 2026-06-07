from decimal import Decimal

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_list_get_and_delete_eat_record(client: AsyncClient) -> None:
    create_payload = {
        "user_id": 1,
        "person": "",
        "items": [
            {"food_id": 10, "food_name": "番茄炒蛋", "quantity": 2, "price": "18.50"},
            {"food_id": 11, "food_name": "米饭", "quantity": 1, "price": "3.00"},
        ],
    }
    created = (await client.post("/api/eat-records", json=create_payload)).json()["data"]

    assert created["person"] == "default"
    assert Decimal(created["total_price"]) == Decimal("40.00")
    assert len(created["items"]) == 2

    records = (await client.get("/api/eat-records?user_id=1")).json()["data"]
    assert records["total"] == 1
    assert records["items"][0]["id"] == created["id"]

    other_user_detail = (await client.get(f"/api/eat-records/{created['id']}?user_id=2")).json()
    assert other_user_detail["code"] == 40004

    detail = (await client.get(f"/api/eat-records/{created['id']}?user_id=1")).json()["data"]
    assert detail["id"] == created["id"]

    deleted = (await client.delete(f"/api/eat-records/{created['id']}?user_id=1")).json()
    assert deleted["code"] == 0
    assert (await client.get("/api/eat-records?user_id=1")).json()["data"]["total"] == 0


@pytest.mark.asyncio
async def test_eat_record_rejects_empty_items(client: AsyncClient) -> None:
    payload = (await client.post("/api/eat-records", json={"user_id": 1, "items": []})).json()

    assert payload["code"] == 40001
