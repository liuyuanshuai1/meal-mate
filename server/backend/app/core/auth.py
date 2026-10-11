import base64
import binascii
import hashlib
import hmac
import json
import time

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.response import AppException
from app.models.user import User


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    if settings.app_env == "production" and settings.token_secret == "change-me-in-production":
        raise AppException(50000, "TOKEN_SECRET 尚未配置")
    payload = {"uid": user_id, "exp": int(time.time()) + settings.token_ttl_days * 86400}
    encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(settings.token_secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def decode_access_token(token: str) -> int:
    settings = get_settings()
    try:
        encoded, signature = token.split(".", 1)
        expected = hmac.new(settings.token_secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        padded = encoded + "=" * (-len(encoded) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded).decode())
        if int(payload["exp"]) < int(time.time()):
            raise ValueError
        return int(payload["uid"])
    except (ValueError, KeyError, TypeError, UnicodeDecodeError, binascii.Error, json.JSONDecodeError) as exc:
        raise AppException(40100, "登录已失效") from exc


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppException(40100, "请先登录")
    user = await db.get(User, decode_access_token(authorization[7:]))
    if user is None:
        raise AppException(40100, "用户不存在")
    return user
