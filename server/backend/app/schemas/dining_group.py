from pydantic import BaseModel, Field, field_validator


class DiningGroupCreate(BaseModel):
    name: str = Field(default="我们的饭搭子", min_length=1, max_length=64)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("饭搭子名称不能为空")
        return normalized


class DiningGroupJoin(BaseModel):
    invite_token: str = Field(min_length=16, max_length=128)


class DiningGroupMemberOut(BaseModel):
    user_id: int
    nickname: str
    role: str


class DiningGroupMemberNameUpdate(BaseModel):
    user_id: int | None = Field(default=None, gt=0)
    nickname: str = Field(min_length=1, max_length=64)

    @field_validator("nickname")
    @classmethod
    def normalize_nickname(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("昵称不能为空")
        return normalized


class DiningGroupOut(BaseModel):
    id: int
    name: str
    invite_token: str
    members: list[DiningGroupMemberOut]
