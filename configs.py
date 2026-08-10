"""Configurations for the app."""

from __future__ import annotations

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base config with shared settings behavior."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )


class BotConfig(BaseConfig):
    """Bot config class."""

    token: SecretStr = Field(..., min_length=16)

    model_config = SettingsConfigDict(env_prefix="BOT_")


class DBConfig(BaseConfig):
    """Database config class."""

    host: str = "localhost"
    port: int = Field(default=5432, ge=1, le=65535)
    user: str
    password: SecretStr
    db: str

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    @property
    def url(self) -> str:
        """DB URL."""
        return (
            f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.db}"
        )


bot_config = BotConfig()  # type: ignore[call-arg]
db_config = DBConfig()  # type: ignore[call-arg]