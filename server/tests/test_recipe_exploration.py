import pytest
from app.core.config import get_settings
from app.models.ai_explore_usage import AiExploreUsage
from app.models.food import Food
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def login_token(client: AsyncClient) -> str:
    result = await client.post("/api/auth/wechat-login", json={"code": "explore-test"})
    return result.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_exploration_returns_only_valid_new_recipes_without_saving_food(
    client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_session.add(Food(name="番茄炒蛋"))
    await db_session.commit()

    async def fake_request_json(
        system_prompt: str, user_data: object, max_tokens: int, timeout: int
    ) -> dict[str, object]:
        assert "番茄炒蛋" in user_data["existing_menu_names"]
        assert max_tokens == 3000
        assert timeout == 45
        recipe = {
            "name": "青椒鸡蛋饼", "reason": "用上青椒和鸡蛋", "cook_minutes": 15, "servings": 2,
            "ingredients": [{"name": "青椒", "amount": "1个"}, {"name": "鸡蛋", "amount": "2个"}],
            "steps": ["青椒切碎。", "鸡蛋打散后煎熟。"], "missing_ingredients": [],
        }
        return {"items": [{**recipe, "name": "番茄炒蛋"}, recipe, {**recipe, "name": "青椒鸡蛋饼"}]}

    monkeypatch.setattr("app.routers.recipe_exploration.request_json", fake_request_json)
    token = await login_token(client)
    response = await client.post(
        "/api/recipes/explore", json={"text": "有鸡蛋和青椒，做个快手菜"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.json()["code"] == 0
    assert [item["name"] for item in response.json()["data"]["items"]] == ["青椒鸡蛋饼"]
    assert await db_session.scalar(select(func.count()).select_from(Food)) == 1
    usage = await db_session.scalar(select(AiExploreUsage))
    assert usage is not None and usage.request_count == 1


@pytest.mark.asyncio
async def test_exploration_requires_login_and_limits_daily_calls(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    async def fake_request_json(
        system_prompt: str, user_data: object, max_tokens: int, timeout: int
    ) -> dict[str, object]:
        nonlocal calls
        calls += 1
        return {"items": []}

    monkeypatch.setattr("app.routers.recipe_exploration.request_json", fake_request_json)
    monkeypatch.setattr(get_settings(), "ai_explore_daily_limit", 1)
    payload = {"text": "想吃家常菜"}
    unauthenticated = await client.post("/api/recipes/explore", json=payload)
    assert unauthenticated.json()["code"] == 40100

    token = await login_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    first = await client.post("/api/recipes/explore", json=payload, headers=headers)
    second = await client.post("/api/recipes/explore", json=payload, headers=headers)
    assert first.json()["code"] == 0
    assert second.json()["code"] == 42900
    assert calls == 1
