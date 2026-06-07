from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

LINK_TYPES = {"none", "food", "url"}


class BannerBase(BaseModel):
    title: str | None = Field(default=None, max_length=128)
    image_url: str = Field(min_length=1)
    link_type: str = "none"
    link_target: str | None = Field(default=None, max_length=256)
    sort: int = 0
    is_active: bool = True

    @field_validator("link_type")
    @classmethod
    def validate_link_type(cls, value: str) -> str:
        if value not in LINK_TYPES:
            raise ValueError("link_type must be one of none, food, url")
        return value


class BannerCreate(BannerBase):
    pass


class BannerUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=128)
    image_url: str | None = Field(default=None, min_length=1)
    link_type: str | None = None
    link_target: str | None = Field(default=None, max_length=256)
    sort: int | None = None
    is_active: bool | None = None

    @field_validator("link_type")
    @classmethod
    def validate_link_type(cls, value: str | None) -> str | None:
        if value is not None and value not in LINK_TYPES:
            raise ValueError("link_type must be one of none, food, url")
        return value


class BannerOut(BannerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
