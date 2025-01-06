"""Configurations for the app."""
import os
from dataclasses import dataclass


@dataclass
class APPConfig:
    """Configuration class for the bot."""

    # Bot token
    bot_token: str = os.getenv('BOT_TOKEN')

    # Database Postgres
    db_user: str = os.getenv('POSTGRES_USER')
    db_password: str = os.getenv('POSTGRES_PASSWORD')
    db_name: str = os.getenv('POSTGRES_DB')
    db_url: str = (
        f"postgresql+asyncpg://{db_user}:{db_password}@db:5432/{db_name}"
    )


app_config = APPConfig()
