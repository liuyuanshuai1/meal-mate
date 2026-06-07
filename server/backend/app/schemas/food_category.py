from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FoodCategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    sort: int = 0
    is_active: bool = True


class FoodCategoryCreate(FoodCategoryBase):
    pass


class FoodCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    sort: int | None = None
    is_active: bool | None = None


class FoodCategoryOut(FoodCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
