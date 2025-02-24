"""FAQ handler for the bot."""
import logging
from aiogram import types, Router, F
from aiogram.utils.i18n import gettext
from bot.keyboards import inline

logger = logging.getLogger(__name__)


async def faq_handler(callback: types.CallbackQuery) -> None:
    """FAQ handler."""
    try:
        await callback.message.edit_text(
            gettext("faq"),
            reply_markup=inline.get_back_keyboard(gettext, "menu")
        )
    except Exception as e:
        logger.error("Failed to send message: %s", e)


def register(router: Router) -> None:
    """Registers FAQ handler with the router."""
    router.callback_query.register(faq_handler, F.data == "faq")
