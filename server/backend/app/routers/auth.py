import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models.user import User
from app.schemas.auth import LoginOut, NicknameUpdate, WechatLoginIn
from app.services.wechat_auth import exchange_code_for_openid

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/wechat-login")
async def wechat_login(payload: WechatLoginIn, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    openid = await asyncio.to_thread(exchange_code_for_openid, payload.code)
    user = await db.scalar(select(User).where(User.openid == openid))
    if user is None:
        user = User(openid=openid, nickname=payload.nickname.strip() if payload.nickname else "饭搭子")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif payload.nickname and payload.nickname.strip():
        user.nickname = payload.nickname.strip()
        await db.commit()
    data = LoginOut(access_token=create_access_token(user.id), user_id=user.id, nickname=user.nickname)
    return ok(data.model_dump())


@router.patch("/me")
async def update_profile(
    payload: NicknameUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    user.nickname = payload.nickname.strip()
    await db.commit()
    return ok({"user_id": user.id, "nickname": user.nickname})
