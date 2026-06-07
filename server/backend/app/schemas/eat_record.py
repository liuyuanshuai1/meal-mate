from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EatRecordItemCreate(BaseModel):
    food_id: int | None = None
    food_name: str = Field(min_length=1, max_length=128)
    food_image_url: str | None = None
    quantity: int = Field(gt=0)
    price: Decimal = Field(ge=0)


class EatRecordCreate(BaseModel):
    user_id: int = Field(gt=0)
    person: str | None = Field(default="default", max_length=64)
    items: list[EatRecordItemCreate] = Field(min_length=1)

    @field_validator("person")
    @classmethod
    def default_person(cls, value: str | None) -> str:
        return value or "default"


class EatRecordItemOut(EatRecordItemCreate):
    id: int
    record_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EatRecordOut(BaseModel):
    id: int
    user_id: int
    person: str
    total_price: Decimal
    eaten_at: datetime
    items: list[EatRecordItemOut]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
