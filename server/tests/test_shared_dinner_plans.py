import pytest
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
async def test_login_reuses_wechat_user(client: AsyncClient) -> None:
    _, first_id = await login(client, "same-code")
    _, second_id = await login(client, "same-code")

    assert first_id == second_id
