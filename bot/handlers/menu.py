"""Menu handler for the bot."""

from __future__ import annotations

import logging

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.utils.i18n import gettext

from bot.keyboards import inline

logger = logging.getLogger(__name__)


async def menu_handler(
    event: types.Message | types.CallbackQuery,
) -> None:
    """Menu handler."""
    try:
        text = gettext("menu")
        keyboard = inline.get_menu_keyboard(gettext)

        if isinstance(event, types.CallbackQuery):
            await event.message.edit_text(text, reply_markup=keyboard)
        else:
            await event.answer(text, reply_markup=keyboard)
    except Exception:
        logger.exception("Failed to handle menu event")


def register(router: Router) -> None:
    """Register start handler with the router."""
    router.message.register(menu_handler, CommandStart())
    router.message.register(menu_handler, Command("menu"))
    router.callback_query.register(menu_handler, F.data == "menu")
