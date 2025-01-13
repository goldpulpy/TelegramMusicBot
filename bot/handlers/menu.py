"""Menu handler for the bot."""
import logging
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.i18n import gettext
from bot.keyboards import inline


logger = logging.getLogger(__name__)


async def menu_handler(message: types.Message) -> None:
    """Menu handler."""
    try:
        await message.answer(
            gettext("menu"),
            reply_markup=inline.get_menu_keyboard(gettext)
        )
    except Exception as e:
        logger.error("Failed to send message: %s", e)


async def menu_callback_handler(callback: types.CallbackQuery) -> None:
    """Menu callback handler."""
    await callback.message.edit_text(
        gettext("menu"),
        reply_markup=inline.get_menu_keyboard(gettext)
    )


def register(router: Router) -> None:
    """Registers start handler with the router."""
    router.message.register(menu_handler, CommandStart())
    router.message.register(menu_handler, Command("menu"))
    router.callback_query.register(menu_callback_handler, F.data == "menu")
