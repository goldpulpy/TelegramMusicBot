"""Entry point of the bot application."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n import I18n
from aiogram.utils.token import TokenValidationError

from bot import handlers, middlewares
from configs import bot_config
from database.engine import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s:%(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def create_bot() -> Bot:
    """Create and return a Bot instance."""
    try:
        bot = Bot(
            token=bot_config.token,
            default=DefaultBotProperties(parse_mode="HTML"),
        )
        logger.info("Successfully created bot instance.")
        return bot
    except TokenValidationError as e:
        logger.error("Invalid token provided: %s", bot_config.token)
        raise e
    except Exception as e:
        logger.error("Failed to create bot instance: %s", str(e))
        raise e


async def main() -> None:
    """The entry point of the bot application."""
    bot = await create_bot()

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    i18n = I18n(path="locales", domain="messages")
    logger.info("Successfully created dispatcher, i18n and storage instance.")

    middlewares.setup(dp, i18n)
    logger.info("Successfully set up middleware.")

    handlers.setup(dp)
    logger.info("Successfully set up handlers.")

    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("Starting application...")
    asyncio.run(main())
