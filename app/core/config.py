"""
Единая конфигурация приложения.

Все настройки читаются из окружения (.env в dev, реальные env vars в
проде). Ничего не хардкодится в коде — это единственный файл, который
знает про переменные окружения; остальной код получает уже готовый
объект `settings`.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Общие ---
    app_name: str = "English App Backend"
    environment: Literal["local", "staging", "production"] = "local"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # --- База данных ---
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/english_app"
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    # --- Redis ---
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")

    # --- Безопасность / JWT ---
    secret_key: SecretStr = Field(..., description="Секрет для подписи JWT")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # --- CORS ---
    cors_allow_origins: list[str] = Field(default_factory=lambda: ["http://localhost"])

    # --- DeepSeek AI ---
    deepseek_api_key: SecretStr | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    deepseek_timeout_seconds: float = 30.0

    # --- Логирование ---
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_json: bool = True

    @field_validator("environment")
    @classmethod
    def _lower_env(cls, v: str) -> str:
        return v.lower()

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Настройки читаются один раз за процесс и кэшируются.
    Использовать через Depends(get_settings) в FastAPI или прямой вызов
    в местах вне request-контекста (например, при старте приложения).
    """
    return Settings()


settings = get_settings()
