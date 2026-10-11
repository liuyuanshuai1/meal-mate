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
    wechat_app_id: str = Field(default="", validation_alias="WECHAT_APP_ID")
    wechat_app_secret: str = Field(default="", validation_alias="WECHAT_APP_SECRET")
    token_secret: str = Field(default="change-me-in-production", validation_alias="TOKEN_SECRET")
    token_ttl_days: int = Field(default=30, validation_alias="TOKEN_TTL_DAYS")
    admin_token: str = Field(default="", validation_alias="ADMIN_TOKEN")
    wechat_mock_login: bool = Field(default=False, validation_alias="WECHAT_MOCK_LOGIN")
    deepseek_api_key: str = Field(default="", validation_alias="DEEPSEEK_API_KEY")
    deepseek_model: str = Field(default="deepseek-flash", validation_alias="DEEPSEEK_MODEL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
