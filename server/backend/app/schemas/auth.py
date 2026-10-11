from pydantic import BaseModel, Field, field_validator


class WechatLoginIn(BaseModel):
    code: str = Field(min_length=1, max_length=256)
    nickname: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("nickname")
    @classmethod
    def normalize_nickname(cls, value: str | None) -> str | None:
        normalized = value.strip() if value else None
        if value is not None and not normalized:
            raise ValueError("昵称不能为空")
        return normalized


class NicknameUpdate(BaseModel):
    nickname: str = Field(min_length=1, max_length=64)

    @field_validator("nickname")
    @classmethod
    def normalize_nickname(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("昵称不能为空")
        return normalized


class LoginOut(BaseModel):
    access_token: str
    user_id: int
    nickname: str
