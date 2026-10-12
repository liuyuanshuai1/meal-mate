import json
import logging
import re
from zoneinfo import ZoneInfo

import httpx

from app.core.config import Settings, get_settings
from app.models.dinner_plan import DinnerPlan

logger = logging.getLogger(__name__)
FIELD_KEY = re.compile(r"^(?:thing|name|phrase|character_string|time|date|number)\d+$")
FIELD_VALUES = {"creator", "summary", "meal_time"}


def template_fields(settings: Settings) -> dict[str, str]:
    if not settings.wechat_dinner_plan_template_id or not settings.wechat_dinner_plan_template_fields:
        return {}
    try:
        fields = json.loads(settings.wechat_dinner_plan_template_fields)
    except json.JSONDecodeError:
        return {}
    if not isinstance(fields, dict) or not fields:
        return {}
    if any(
        not isinstance(key, str)
        or not FIELD_KEY.fullmatch(key)
        or not isinstance(value, str)
        or value not in FIELD_VALUES
        or (value == "meal_time" and not key.startswith(("time", "date")))
        for key, value in fields.items()
    ):
        return {}
    return fields


def notification_enabled(settings: Settings) -> bool:
    return bool(
        settings.wechat_app_id
        and settings.wechat_app_secret
        and settings.wechat_dinner_plan_template_id
        and template_fields(settings)
    )


def notification_data(
    plan: DinnerPlan, creator_name: str, fields: dict[str, str], tz: str
) -> dict[str, dict[str, str]]:
    meal_time = plan.scheduled_for or plan.created_at
    if meal_time.tzinfo is None:
        meal_time = meal_time.replace(tzinfo=ZoneInfo(tz))
    values = {
        "creator": f"{creator_name}下单了"[:20],
        "summary": f"共{sum(item.quantity for item in plan.items)}份，{len(plan.items)}道菜"[:20],
        "meal_time": meal_time.astimezone(ZoneInfo(tz)).strftime("%Y-%m-%d %H:%M"),
    }
    return {key: {"value": values[value]} for key, value in fields.items()}


async def send_plan_notification(plan: DinnerPlan, creator_name: str) -> None:
    settings = get_settings()
    if not notification_enabled(settings):
        return
    partner = next((member for member in plan.group.members if member.user_id != plan.created_by), None)
    if partner is None or not partner.user.openid:
        return

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            token_response = await client.get(
                "https://api.weixin.qq.com/cgi-bin/token",
                params={
                    "grant_type": "client_credential",
                    "appid": settings.wechat_app_id,
                    "secret": settings.wechat_app_secret,
                },
            )
            token_response.raise_for_status()
            token_result = token_response.json()
            token = token_result.get("access_token") if isinstance(token_result, dict) else None
            if not token:
                logger.warning("WeChat access token unavailable for dinner plan reminder")
                return

            response = await client.post(
                "https://api.weixin.qq.com/cgi-bin/message/subscribe/send",
                params={"access_token": token},
                json={
                    "touser": partner.user.openid,
                    "template_id": settings.wechat_dinner_plan_template_id,
                    "page": f"pages/dinner-plan/index?id={plan.id}",
                    "data": notification_data(plan, creator_name, template_fields(settings), settings.tz),
                },
            )
            response.raise_for_status()
            result = response.json()
            if not isinstance(result, dict) or result.get("errcode") != 0:
                code = result.get("errcode") if isinstance(result, dict) else None
                logger.warning("WeChat dinner plan reminder rejected: errcode=%s", code)
    except Exception as exc:
        logger.warning("WeChat dinner plan reminder failed: %s", type(exc).__name__)
