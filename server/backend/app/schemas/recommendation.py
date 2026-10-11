from pydantic import BaseModel, Field


class RecommendIn(BaseModel):
    text: str = Field(min_length=2, max_length=200)
