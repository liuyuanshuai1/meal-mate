from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EatRecordItemOut(BaseModel):
    id: int
    record_id: int
    food_id: int | None = None
    food_name: str
    food_image_url: str | None = None
    quantity: int
    feeding_value: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EatRecordOut(BaseModel):
    id: int
    user_id: int
    person: str
    feeding_total: int
    eaten_at: datetime
    items: list[EatRecordItemOut]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
