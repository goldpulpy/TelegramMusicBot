"""Configurations for the app."""
import os
from dataclasses import dataclass


os.environ['TZ'] = os.getenv('TIMEZONE', 'UTC')


@dataclass
class BotConfig:
    """Configuration class for the bot."""
    token: str = os.getenv('BOT_TOKEN')


@dataclass
class DBConfig:
    """Configuration class for the database."""
    host: str = os.getenv('POSTGRES_HOST', 'db')
    port: str = os.getenv('POSTGRES_PORT', '5432')
    user: str = os.getenv('POSTGRES_USER')
    password: str = os.getenv('POSTGRES_PASSWORD')
    db: str = os.getenv('POSTGRES_DB')
    url: str = (
        "postgresql+asyncpg://"
        f"{user}:{password}@{host}:{port}/{db}"
    )


bot_config = BotConfig()
db_config = DBConfig()
