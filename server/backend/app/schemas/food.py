from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class FoodBase(BaseModel):
    category_id: int | None = None
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    image_url: str | None = None
    price: Decimal = Field(default=Decimal("0"), ge=0)
    is_recommended: bool = False
    is_active: bool = True
    sort: int = 0


class FoodCreate(FoodBase):
    pass


class FoodUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    image_url: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    is_recommended: bool | None = None
    is_active: bool | None = None
    sort: int | None = None


class FoodOut(FoodBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ImageUploadOut(BaseModel):
    image_url: str
