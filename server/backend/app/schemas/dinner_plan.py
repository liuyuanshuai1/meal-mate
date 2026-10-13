from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DinnerPlanItemCreate(BaseModel):
    food_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=99)
    cook_user_id: int = Field(gt=0)


class DinnerPlanCreate(BaseModel):
    items: list[DinnerPlanItemCreate] = Field(min_length=1, max_length=30)
    scheduled_for: datetime | None = None


class DinnerPlanUpdate(BaseModel):
    items: list[DinnerPlanItemCreate] = Field(min_length=1, max_length=30)


class DinnerPlanItemOut(BaseModel):
    id: int
    food_id: int
    food_name: str
    food_image_url: str | None
    recipe_cook_minutes: int | None
    recipe_ingredients: list[dict[str, str]]
    recipe_steps: list[str]
    quantity: int
    feeding_value: int
    cook_user_id: int
    cook_name: str

    model_config = ConfigDict(from_attributes=True)


class DinnerPlanOut(BaseModel):
    id: int
    group_id: int
    created_by: int
    creator_name: str
    status: str
    feeding_total: int
    scheduled_for: datetime | None
    notification_unread: bool
    created_at: datetime
    completed_at: datetime | None
    items: list[DinnerPlanItemOut]
