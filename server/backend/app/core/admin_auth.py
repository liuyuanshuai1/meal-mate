import hmac
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.config import get_settings
from app.core.response import AppException

admin_basic = HTTPBasic(auto_error=False)


def require_admin(x_admin_token: Annotated[str | None, Header()] = None) -> None:
    configured_token = get_settings().admin_token
    if not configured_token or not x_admin_token or not hmac.compare_digest(x_admin_token, configured_token):
        raise AppException(40300, "管理员认证失败")


def require_admin_basic(credentials: Annotated[HTTPBasicCredentials | None, Depends(admin_basic)]) -> None:
    configured_token = get_settings().admin_token
    valid_username = credentials is not None and hmac.compare_digest(credentials.username, "admin")
    valid_password = credentials is not None and bool(configured_token) and hmac.compare_digest(
        credentials.password, configured_token
    )
    if not valid_username or not valid_password:
        raise HTTPException(
            status_code=401,
            detail="管理员认证失败",
            headers={"WWW-Authenticate": 'Basic realm="MealMate Admin"'},
        )
