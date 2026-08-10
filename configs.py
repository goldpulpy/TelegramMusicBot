"""Configurations for the app."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    """Bot config class."""

    token: str = Field(..., min_length=16)

    model_config = SettingsConfigDict(
        extra="ignore",
        frozen=True,
        env_prefix="BOT_",
    )


class DBConfig(BaseSettings):
    """Database config class."""

    host: str = "localhost"
    port: int = Field(default=5432, ge=1, le=65535)
    user: str
    password: str
    db: str

    model_config = SettingsConfigDict(
        extra="ignore",
        frozen=True,
        env_prefix="POSTGRES_",
    )

    @property
    def url(self) -> str:
        """DB URL."""
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.db}"
        )


bot_config = BotConfig()  # type: ignore[call-arg]
db_config = DBConfig()  # type: ignore[call-arg]
