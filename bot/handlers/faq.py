"""FAQ handler for the bot."""

import logging

from aiogram import F, Router, types
from aiogram.utils.i18n import gettext

from bot.keyboards import inline

logger = logging.getLogger(__name__)


async def faq_handler(callback: types.CallbackQuery) -> None:
    """FAQ handler."""
    try:
        if callback.message is None:
            await callback.answer("Cannot edit message")
            return

        await callback.message.edit_text(
            gettext("faq"),
            reply_markup=inline.get_back_keyboard(gettext, "menu"),
        )
    except Exception:
        logger.exception("Failed to send message")


def register(router: Router) -> None:
    """Register FAQ handler with the router."""
    router.callback_query.register(faq_handler, F.data == "faq")
