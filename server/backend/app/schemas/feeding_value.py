from pydantic import BaseModel, Field, field_validator


class FeedingRewardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    cost: int = Field(gt=0, le=1000000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("兑换内容不能为空")
        return normalized


class FeedingRedeem(BaseModel):
    reward_id: int = Field(gt=0)
