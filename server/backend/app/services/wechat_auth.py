import json
from urllib.parse import urlencode
from urllib.request import urlopen

from app.core.config import get_settings
from app.core.response import AppException


def exchange_code_for_openid(code: str) -> str:
    settings = get_settings()
    if settings.wechat_mock_login:
        return f"mock:{code}"
    if not settings.wechat_app_id or not settings.wechat_app_secret:
        raise AppException(50000, "微信登录尚未配置")
    query = urlencode(
        {
            "appid": settings.wechat_app_id,
            "secret": settings.wechat_app_secret,
            "js_code": code,
            "grant_type": "authorization_code",
        }
    )
    try:
        with urlopen(f"https://api.weixin.qq.com/sns/jscode2session?{query}", timeout=5) as response:  # noqa: S310
            data = json.loads(response.read())
    except (OSError, json.JSONDecodeError) as exc:
        raise AppException(50000, "微信登录服务暂不可用") from exc
    openid = data.get("openid")
    if not openid:
        raise AppException(40001, "微信登录失败")
    return str(openid)
