"""Language handler for the bot."""
import logging
from typing import Union
from aiogram import types, Router, Bot, F
from aiogram.utils import i18n
from aiogram.utils.i18n import gettext
from aiogram.filters import Command
from bot.filters import LanguageFilter
from bot.keyboards import inline, command
from database.crud import CRUD
from database.models import User
from .menu import menu_handler


logger = logging.getLogger(__name__)


async def language_handler(
    event: Union[types.Message, types.CallbackQuery]
) -> None:
    """Language handler."""
    try:
        text = "🌎 Choose language:"
        keyboard = inline.language_keyboard

        if isinstance(event, types.CallbackQuery):
            await event.message.edit_text(text, reply_markup=keyboard)
        else:
            await event.answer(text, reply_markup=keyboard)
    except Exception as e:
        logger.error("Failed to send message: %s", e)


async def language_set_handler(
    callback: types.CallbackQuery,
    user: User,
    bot: Bot
) -> None:
    """Language set handler."""
    try:
        language_code = callback.data.split(":")[-1]

        user_crud = CRUD(User)
        await user_crud.update(user, language_code=language_code)
        i18n.get_i18n().ctx_locale.set(language_code)

        await bot.set_my_commands(command.get_commands(gettext))
        await menu_handler(callback)
    except Exception as e:
        logger.error("Failed to set language: %s", e)


def register(router: Router) -> None:
    """Registers language handler with the router."""
    router.message.register(language_handler, LanguageFilter())
    router.message.register(language_handler, Command("language"))
    router.callback_query.register(language_handler, F.data == "language")
    router.callback_query.register(
        language_set_handler, F.data.startswith("language:set:")
    )
