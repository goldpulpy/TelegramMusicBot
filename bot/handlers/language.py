"""Language handler for the bot."""

from __future__ import annotations

import logging

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.utils import i18n
from aiogram.utils.i18n import gettext

from bot.filters import LanguageFilter
from bot.keyboards import command, inline
from database.crud import CRUD
from database.models import User
from locales import support_languages

from .menu import menu_handler

logger = logging.getLogger(__name__)


async def language_handler(
    event: types.Message | types.CallbackQuery,
    user: User,
) -> None:
    """Language handler."""
    try:
        language_code = user.language_code
        text = (
            gettext("language_choose")
            if language_code is not None
            and support_languages.is_supported(language_code)
            else "🌎 Choose language:"
        )
        keyboard = inline.language_keyboard

        match event:
            case types.Message():
                await event.answer(text, reply_markup=keyboard)

            case types.CallbackQuery() if event.message:
                if not isinstance(event.message, types.Message):
                    await event.answer(gettext("cannot_edit_message"))
                    return

                await event.message.edit_text(text, reply_markup=keyboard)

            case _:
                await event.answer(gettext("cannot_send_message"))

    except Exception:
        logger.exception("Failed to send message")


async def language_set_handler(
    callback: types.CallbackQuery,
    user: User,
    bot: Bot,
) -> None:
    """Language set handler."""
    try:
        if callback.data:
            language_code = callback.data.split(":")[-1]

            user_crud = CRUD(User)
            await user_crud.update(user, language_code=language_code)
            i18n.get_i18n().ctx_locale.set(language_code)

            await bot.set_my_commands(command.get_commands(gettext))
            await menu_handler(callback)

    except Exception:
        logger.exception("Failed to set language")


def register(router: Router) -> None:
    """Register language handler with the router."""
    router.message.register(language_handler, LanguageFilter())
    router.message.register(language_handler, Command("language"))
    router.callback_query.register(language_handler, F.data == "language")
    router.callback_query.register(
        language_set_handler,
        F.data.startswith("language:set:"),
    )
