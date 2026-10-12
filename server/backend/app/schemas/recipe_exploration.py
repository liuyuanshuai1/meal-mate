from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class ExploreIn(BaseModel):
    text: str = Field(min_length=2, max_length=200)


class ExploreIngredient(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=64)
    amount: str = Field(min_length=1, max_length=64)


class ExploredRecipe(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=1, max_length=120)
    cook_minutes: int = Field(ge=1, le=480)
    servings: int = Field(ge=1, le=8)
    ingredients: list[ExploreIngredient] = Field(min_length=1, max_length=20)
    steps: list[Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=300)]] = Field(
        min_length=2, max_length=12
    )
    missing_ingredients: list[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]] = (
        Field(max_length=20)
    )
