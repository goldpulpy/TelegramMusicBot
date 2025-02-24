"""Menu handler for the bot."""
import logging
from typing import Union
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.i18n import gettext
from bot.keyboards import inline


logger = logging.getLogger(__name__)


async def menu_handler(
    event: Union[types.Message, types.CallbackQuery]
) -> None:
    """Menu handler."""
    try:
        text = gettext("menu")
        keyboard = inline.get_menu_keyboard(gettext)

        if isinstance(event, types.CallbackQuery):
            await event.message.edit_text(text, reply_markup=keyboard)
        else:
            await event.answer(text, reply_markup=keyboard)
    except Exception as e:
        logger.error("Failed to handle menu event: %s", e)


def register(router: Router) -> None:
    """Registers start handler with the router."""
    router.message.register(menu_handler, CommandStart())
    router.message.register(menu_handler, Command("menu"))
    router.callback_query.register(menu_handler, F.data == "menu")
