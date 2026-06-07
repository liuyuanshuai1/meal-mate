from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = Field(default="MealMate API", validation_alias="APP_NAME")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    debug: bool = Field(default=True, validation_alias="DEBUG")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:15432/meal_mate",
        validation_alias="DATABASE_URL",
    )
    upload_dir: str = Field(default=str(BACKEND_DIR / "static" / "uploads"), validation_alias="UPLOAD_DIR")
    public_static_url: str = Field(default="/static/uploads", validation_alias="PUBLIC_STATIC_URL")
    tz: str = Field(default="Asia/Shanghai", validation_alias="TZ")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
