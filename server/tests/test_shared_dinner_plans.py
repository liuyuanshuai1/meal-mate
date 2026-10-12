from datetime import timedelta

import pytest
from app.core.timezone import now_tz
from app.models.user import User
from httpx import AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession


async def login(client: AsyncClient, code: str) -> tuple[dict[str, str], int]:
    data = (await client.post("/api/auth/wechat-login", json={"code": code})).json()["data"]
    return {"Authorization": f"Bearer {data['access_token']}"}, data["user_id"]


@pytest.mark.asyncio
async def test_two_people_share_and_complete_dinner_plan(
    client: AsyncClient, db_session: AsyncSession, admin_headers: dict[str, str]
) -> None:
    owner, owner_id = await login(client, "owner")
    partner, partner_id = await login(client, "partner")
    third, _ = await login(client, "third")

    group = (await client.post("/api/dining-groups", json={}, headers=owner)).json()["data"]
    not_ready = (
        await client.post(
            "/api/dinner-plans",
            json={"items": [{"food_id": 999, "quantity": 1, "cook_user_id": owner_id}]},
            headers=owner,
        )
    ).json()
    assert not_ready["code"] == 40001

    joined = (
        await client.post(
            "/api/dining-groups/join",
            json={"invite_token": group["invite_token"]},
            headers=partner,
        )
    ).json()["data"]
    assert {item["user_id"] for item in joined["members"]} == {owner_id, partner_id}

    renamed_self = (
        await client.patch("/api/dining-groups/me", json={"nickname": "小明本人"}, headers=owner)
    ).json()["data"]
    assert next(item for item in renamed_self["members"] if item["user_id"] == owner_id)["nickname"] == "小明本人"
    renamed_partner = (
        await client.patch(
            "/api/dining-groups/me", json={"user_id": partner_id, "nickname": "小红本人"}, headers=owner
        )
    ).json()["data"]
    assert next(item for item in renamed_partner["members"] if item["user_id"] == partner_id)["nickname"] == "小红本人"
    blank_name = (
        await client.patch("/api/dining-groups/me", json={"nickname": "   "}, headers=owner)
    ).json()
    assert blank_name["code"] == 40001

    full = (
        await client.post(
            "/api/dining-groups/join",
            json={"invite_token": group["invite_token"]},
            headers=third,
        )
    ).json()
    assert full["code"] == 40001

    owner_user = await db_session.get(User, owner_id)
    partner_user = await db_session.get(User, partner_id)
    assert owner_user is not None
    assert partner_user is not None

    category = (
        await client.post("/api/food-categories", json={"name": "热菜"}, headers=admin_headers)
    ).json()["data"]
    food = (
        await client.post(
            "/api/foods",
            json={
                "category_id": category["id"], "name": "番茄炒蛋", "feeding_value": 12,
                "recipe_status": "published", "cook_minutes": 15,
                "ingredients": [{"name": "番茄", "amount": "2个"}, {"name": "鸡蛋", "amount": "3个"}],
                "recipe_steps": ["番茄切块，鸡蛋打散。", "先炒鸡蛋，再加入番茄炒熟。"],
            },
            headers=admin_headers,
        )
    ).json()["data"]
    second_food = (
        await client.post(
            "/api/foods",
            json={"category_id": category["id"], "name": "米饭", "feeding_value": 3},
            headers=admin_headers,
        )
    ).json()["data"]
    plan = (
        await client.post(
            "/api/dinner-plans",
            json={
                "items": [
                    {"food_id": food["id"], "quantity": 2, "cook_user_id": owner_id},
                    {"food_id": second_food["id"], "quantity": 1, "cook_user_id": partner_id},
                ]
            },
            headers=owner,
        )
    ).json()["data"]
    assert [item["cook_user_id"] for item in plan["items"]] == [owner_id, partner_id]
    assert plan["items"][0]["feeding_value"] == 12
    assert plan["items"][0]["recipe_cook_minutes"] == 15
    assert plan["items"][0]["recipe_ingredients"][0] == {"name": "番茄", "amount": "2个"}
    assert plan["items"][0]["recipe_steps"][1] == "先炒鸡蛋，再加入番茄炒熟。"
    assert plan["items"][1]["recipe_steps"] == []
    assert plan["feeding_total"] == 27

    partner_plan = (await client.get("/api/dinner-plans/current", headers=partner)).json()["data"]
    assert partner_plan["id"] == plan["id"]
    assert partner_plan["creator_name"] == "小明本人"
    assert partner_plan["items"][0]["recipe_steps"] == plan["items"][0]["recipe_steps"]
    assert partner_plan["notification_unread"] is True
    assert plan["notification_unread"] is False
    seen = (await client.post(f"/api/dinner-plans/{plan['id']}/seen", headers=partner)).json()["data"]
    assert seen["notification_unread"] is False
    refreshed_partner_plan = (await client.get("/api/dinner-plans/current", headers=partner)).json()["data"]
    assert refreshed_partner_plan["notification_unread"] is False

    changed = await client.put(
        f"/api/foods/{food['id']}",
        json={"recipe_steps": ["新版做法。"]},
        headers=admin_headers,
    )
    assert changed.json()["code"] == 0
    still_original = (await client.get(f"/api/dinner-plans/{plan['id']}", headers=partner)).json()["data"]
    assert still_original["items"][0]["recipe_steps"] == plan["items"][0]["recipe_steps"]

    select_count = 0

    def count_selects(*args: object) -> None:
        nonlocal select_count
        statement = args[2]
        if isinstance(statement, str) and statement.lstrip().upper().startswith("SELECT"):
            select_count += 1

    assert db_session.bind is not None
    sync_engine = db_session.bind.sync_engine
    event.listen(sync_engine, "before_cursor_execute", count_selects)
    try:
        completed = (
            await client.post(f"/api/dinner-plans/{plan['id']}/complete", headers=partner)
        ).json()["data"]
    finally:
        event.remove(sync_engine, "before_cursor_execute", count_selects)

    assert completed["status"] == "completed"
    feeding = (await client.get("/api/feeding-values", headers=owner)).json()["data"]
    assert next(item for item in feeding["balances"] if item["user_id"] == owner_id)["balance"] == 24
    assert next(item for item in feeding["balances"] if item["user_id"] == partner_id)["balance"] == 3
    assert select_count <= 7
    assert (await client.get("/api/dinner-plans/current", headers=owner)).json()["data"] == {}

    owner_records = (await client.get("/api/eat-records", headers=owner)).json()["data"]
    partner_records = (await client.get("/api/eat-records", headers=partner)).json()["data"]
    assert owner_records["total"] == 1
    assert partner_records["total"] == 1
    assert owner_records["items"][0]["items"][0]["food_name"] == "番茄炒蛋"
    assert owner_records["items"][0]["person"] == "小红本人"
    assert partner_records["items"][0]["person"] == "小明本人"


@pytest.mark.asyncio
async def test_group_name_rejects_whitespace(client: AsyncClient) -> None:
    owner, _ = await login(client, "blank-group-owner")

    response = (await client.post("/api/dining-groups", json={"name": "   "}, headers=owner)).json()

    assert response["code"] == 40001


@pytest.mark.asyncio
async def test_dinner_plan_can_be_reserved_for_both_diners(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    owner, owner_id = await login(client, "booking-owner")
    partner, _ = await login(client, "booking-partner")
    group = (await client.post("/api/dining-groups", json={}, headers=owner)).json()["data"]
    await client.post("/api/dining-groups/join", json={"invite_token": group["invite_token"]}, headers=partner)
    food = (await client.post(
        "/api/foods", json={"name": "预约的菜", "feeding_value": 8}, headers=admin_headers
    )).json()["data"]
    items = [{"food_id": food["id"], "quantity": 1, "cook_user_id": owner_id}]
    invalid = (await client.post(
        "/api/dinner-plans", json={"items": items, "scheduled_for": "2026-10-15T18:00:00"}, headers=owner
    )).json()
    assert invalid["code"] == 40001

    scheduled_for = now_tz() + timedelta(days=2)
    booked = (await client.post(
        "/api/dinner-plans", json={"items": items, "scheduled_for": scheduled_for.isoformat()}, headers=owner
    )).json()["data"]
    assert booked["status"] == "pending"
    assert booked["scheduled_for"] is not None
    assert booked["notification_unread"] is False
    partner_plan = (await client.get("/api/dinner-plans/current", headers=partner)).json()["data"]
    assert partner_plan["id"] == booked["id"]
    assert partner_plan["scheduled_for"] == booked["scheduled_for"]
    assert partner_plan["notification_unread"] is True
    next_week = now_tz() + timedelta(days=4)
    second = (await client.post(
        "/api/dinner-plans", json={"items": items, "scheduled_for": next_week.isoformat()}, headers=partner
    )).json()["data"]
    upcoming_owner = (await client.get("/api/dinner-plans/upcoming", headers=owner)).json()["data"]
    upcoming_partner = (await client.get("/api/dinner-plans/upcoming", headers=partner)).json()["data"]
    assert [plan["id"] for plan in upcoming_owner] == [booked["id"], second["id"]]
    assert [plan["id"] for plan in upcoming_partner] == [booked["id"], second["id"]]
    assert upcoming_owner[1]["notification_unread"] is True
    assert upcoming_partner[0]["notification_unread"] is True


@pytest.mark.asyncio
async def test_login_reuses_wechat_user(client: AsyncClient) -> None:
    _, first_id = await login(client, "same-code")
    _, second_id = await login(client, "same-code")

    assert first_id == second_id
