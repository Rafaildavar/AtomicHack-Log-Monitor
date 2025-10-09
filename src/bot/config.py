"""Конфигурация приложения Telegram-бота."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки бота, читаемые из переменных окружения или файла .env."""

    bot_token: str = Field(..., alias="BOT_TOKEN", description="Токен Telegram-бота")
    log_level: str = Field("INFO", alias="LOG_LEVEL", description="Уровень логирования")
    webhook_url: str | None = Field(
        None,
        alias="WEBHOOK_URL",
        description="URL для вебхука, если используется режим webhook",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )


settings = Settings()

