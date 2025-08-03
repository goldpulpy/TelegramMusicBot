"""Configurations for the app."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

os.environ["TZ"] = os.getenv("TIMEZONE", "UTC")
time.tzset()


@dataclass
class BotConfig:
    """Configuration class for the bot."""

    token: str | None = os.getenv("BOT_TOKEN")

    def __post_init__(self) -> None:
        """Post-init method for the bot configuration."""
        if not self.token:
            msg = "Bot token is not set"
            raise ValueError(msg)


@dataclass
class DBConfig:
    """Configuration class for the database."""

    host: str = os.getenv("POSTGRES_HOST", "db")
    port: str = os.getenv("POSTGRES_PORT", "5432")
    user: str | None = os.getenv("POSTGRES_USER")
    password: str | None = os.getenv("POSTGRES_PASSWORD")
    db: str | None = os.getenv("POSTGRES_DB")

    def __post_init__(self) -> None:
        """Post-init method for the database configuration."""
        if not self.user or not self.password or not self.db:
            msg = "Database configuration is incomplete"
            raise ValueError(msg)

    @property
    def url(self) -> str:
        """Construct and return the database URL using instance attributes."""
        return (
            "postgresql+asyncpg://"
            f"{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        )


bot_config = BotConfig()
db_config = DBConfig()
