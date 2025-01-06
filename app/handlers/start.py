"""Start for the bot."""
import logging
from aiogram import types, Router, Bot
from aiogram.filters import CommandStart
from aiogram.utils.i18n import gettext
from app.keyboards import command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_handler(message: types.Message, bot: Bot) -> None:
    """Handles the /start command."""
    try:
        await bot.set_my_commands(command.get_commands(gettext))
        await message.answer(gettext("start"))
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


def register(router: Router) -> None:
    """Registers start handler with the router."""
    router.message.register(start_handler, CommandStart())
