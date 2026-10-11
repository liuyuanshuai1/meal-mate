import io
import json

import pytest
from app.core.config import get_settings
from app.models.food import Food
from app.services.deepseek import _request_json
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_recommendation_uses_only_published_active_recipes(
    client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    published = Food(
        name="番茄炒蛋",
        cook_minutes=15,
        ingredients=[{"name": "番茄", "amount": "2个"}, {"name": "鸡蛋", "amount": "3个"}],
        recipe_steps=["炒熟鸡蛋和番茄。"],
        recipe_status="published",
    )
    draft = Food(name="草稿菜", recipe_status="draft")
    inactive = Food(
        name="下架菜", is_active=False, cook_minutes=10,
        ingredients=[{"name": "鸡蛋", "amount": "1个"}], recipe_steps=["煮熟。"], recipe_status="published",
    )
    db_session.add_all([published, draft, inactive])
    await db_session.commit()

    async def fake_request_json(system_prompt: str, user_data: object) -> dict[str, object]:
        assert isinstance(user_data, dict)
        assert [item["food_id"] for item in user_data["candidates"]] == [published.id]
        return {"recommendations": [
            {"food_id": draft.id, "reason": "草稿"},
            {"food_id": published.id, "reason": "用得上番茄和鸡蛋"},
            {"food_id": inactive.id, "reason": "下架"},
        ]}

    monkeypatch.setattr("app.routers.recommendations.request_json", fake_request_json)
    login = (await client.post("/api/auth/wechat-login", json={"code": "recommend-test"})).json()
    token = login["data"]["access_token"]
    result = await client.post(
        "/api/recommendations",
        json={"text": "冰箱里有番茄和鸡蛋"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert result.json()["code"] == 0
    assert result.json()["data"]["items"] == [{
        "food_id": published.id,
        "name": "番茄炒蛋",
        "image_url": None,
        "cook_minutes": 15,
        "reason": "用得上番茄和鸡蛋",
    }]


@pytest.mark.asyncio
async def test_recipe_must_be_complete_before_publication(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/api/foods",
        json={"name": "缺步骤的菜", "recipe_status": "published", "cook_minutes": 10},
        headers=admin_headers,
    )
    assert response.json()["code"] == 40001


@pytest.mark.asyncio
async def test_admin_ai_recipe_stays_draft_until_review(
    client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    food = Food(name="香菇炒青菜", is_active=True)
    db_session.add(food)
    await db_session.commit()

    async def fake_request_json(system_prompt: str, user_data: object, max_tokens: int) -> dict[str, object]:
        return {
            "cook_minutes": 12,
            "ingredients": [{"name": "香菇", "amount": "100克"}, {"name": "青菜", "amount": "200克"}],
            "steps": ["香菇切片，青菜洗净。", "热锅炒熟并调味。"],
        }

    monkeypatch.setattr("app.routers.admin.request_json", fake_request_json)
    response = await client.post(f"/admin/foods/{food.id}/recipe-draft", follow_redirects=True)
    assert response.status_code == 200
    saved = await db_session.scalar(select(Food).where(Food.id == food.id))
    assert saved is not None
    await db_session.refresh(saved)
    assert saved.recipe_status == "draft"
    assert saved.ingredients[0]["name"] == "香菇"

    published = await client.post(
        f"/admin/foods/{food.id}/update",
        data={
            "name": "香菇炒青菜",
            "feeding_value": "0",
            "cook_minutes": "12",
            "ingredients_text": "香菇|100克\n青菜|200克",
            "steps_text": "香菇切片，青菜洗净。\n热锅炒熟并调味。",
            "recipe_status": "published",
            "is_active": "1",
        },
        follow_redirects=True,
    )
    assert published.status_code == 200
    await db_session.refresh(saved)
    assert saved.recipe_status == "published"


def test_deepseek_request_keeps_key_on_server(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "deepseek_api_key", "test-only-key")

    def fake_urlopen(request: object, timeout: int) -> io.BytesIO:
        assert timeout == 20
        assert request.get_header("Authorization") == "Bearer test-only-key"
        body = json.loads(request.data)
        assert body["thinking"] == {"type": "disabled"}
        assert body["response_format"] == {"type": "json_object"}
        return io.BytesIO(json.dumps({
            "choices": [{"finish_reason": "stop", "message": {"content": '{"recommendations":[]}'}}]
        }).encode())

    monkeypatch.setattr("app.services.deepseek.urlopen", fake_urlopen)
    assert _request_json("JSON only", {"request": "想吃番茄"}, 200) == {"recommendations": []}
