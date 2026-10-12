import json
from datetime import datetime
from types import SimpleNamespace
from typing import cast

import httpx
import pytest
from app.core.config import get_settings
from app.models.dinner_plan import DinnerPlan
from app.services import dinner_plan_notifications as notifications


def make_plan() -> DinnerPlan:
    creator = SimpleNamespace(user_id=1)
    partner = SimpleNamespace(user_id=2, user=SimpleNamespace(openid="partner-openid"))
    return cast(
        DinnerPlan,
        SimpleNamespace(
            id=42,
            created_by=1,
            created_at=datetime.fromisoformat("2026-10-12T18:00:00+08:00"),
            scheduled_for=datetime.fromisoformat("2026-10-13T19:30:00+08:00"),
            items=[SimpleNamespace(quantity=2), SimpleNamespace(quantity=1)],
            group=SimpleNamespace(members=[creator, partner]),
        ),
    )


def test_template_configuration_requires_valid_fields() -> None:
    settings = get_settings().model_copy(update={
        "wechat_app_id": "appid",
        "wechat_app_secret": "secret",
        "wechat_dinner_plan_template_id": "template-id",
        "wechat_dinner_plan_template_fields": '{"thing1":"creator","thing2":"summary","time3":"meal_time"}',
    })
    assert notifications.notification_enabled(settings)
    data = notifications.notification_data(make_plan(), "小明", notifications.template_fields(settings), settings.tz)
    assert data == {
        "thing1": {"value": "小明下单了"},
        "thing2": {"value": "共3份，2道菜"},
        "time3": {"value": "2026-10-13 19:30"},
    }
    invalid = settings.model_copy(update={"wechat_dinner_plan_template_fields": '{"thing1":"meal_time"}'})
    assert not notifications.notification_enabled(invalid)


@pytest.mark.asyncio
async def test_wechat_reminder_targets_partner_and_dinner_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = get_settings().model_copy(update={
        "wechat_app_id": "appid",
        "wechat_app_secret": "secret",
        "wechat_dinner_plan_template_id": "template-id",
        "wechat_dinner_plan_template_fields": '{"thing1":"creator","time2":"meal_time"}',
    })
    monkeypatch.setattr(notifications, "get_settings", lambda: settings)
    sent: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/cgi-bin/token":
            return httpx.Response(200, json={"access_token": "test-token"})
        sent.append(json.loads(request.content))
        return httpx.Response(200, json={"errcode": 0})

    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        notifications.httpx, "AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(handler))
    )
    await notifications.send_plan_notification(make_plan(), "小明")
    assert sent == [{
        "touser": "partner-openid",
        "template_id": "template-id",
        "page": "pages/dinner-plan/index?id=42",
        "data": {"thing1": {"value": "小明下单了"}, "time2": {"value": "2026-10-13 19:30"}},
    }]
