"""Configurations for the app."""
import os
from dataclasses import dataclass


@dataclass
class APPConfig:
    """Configuration class for the bot."""

    # Bot token
    bot_token: str = os.getenv('BOT_TOKEN')

    # Database (SQLite)
    database_filename: str = os.getenv('DATABASE_FILENAME')
    database_url: str = (
        "sqlite+aiosqlite:///" + os.path.join('data', database_filename)
    )


app_config = APPConfig()
