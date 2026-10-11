import pytest
from app.core.timezone import now_tz
from app.models.eat_record import EatRecord, EatRecordItem
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def login(client: AsyncClient, code: str) -> dict[str, str]:
    data = (await client.post("/api/auth/wechat-login", json={"code": code})).json()["data"]
    return {"Authorization": f"Bearer {data['access_token']}"}


@pytest.mark.asyncio
async def test_eat_records_use_logged_in_user(client: AsyncClient, db_session: AsyncSession) -> None:
    user_headers = await login(client, "user-1")
    other_headers = await login(client, "user-2")
    record = EatRecord(
        user_id=1,
        person="饭搭子",
        eaten_at=now_tz(),
        items=[EatRecordItem(food_name="番茄炒蛋", quantity=2, feeding_value=20)],
    )
    db_session.add(record)
    await db_session.commit()

    records = (await client.get("/api/eat-records", headers=user_headers)).json()["data"]
    assert records["total"] == 1
    assert records["items"][0]["id"] == record.id
    assert records["items"][0]["feeding_total"] == 40

    hidden = (await client.get(f"/api/eat-records/{record.id}", headers=other_headers)).json()
    assert hidden["code"] == 40004

    detail = (await client.get(f"/api/eat-records/{record.id}", headers=user_headers)).json()["data"]
    assert detail["id"] == record.id
    assert detail["feeding_total"] == 40

    deleted = (await client.delete(f"/api/eat-records/{record.id}", headers=user_headers)).json()
    assert deleted["code"] == 0
    assert (await client.get("/api/eat-records", headers=user_headers)).json()["data"]["total"] == 0


@pytest.mark.asyncio
async def test_eat_records_require_login(client: AsyncClient) -> None:
    payload = (await client.get("/api/eat-records")).json()

    assert payload["code"] == 40100
    invalid = (await client.get("/api/eat-records", headers={"Authorization": "Bearer bad.token"})).json()
    assert invalid["code"] == 40100
