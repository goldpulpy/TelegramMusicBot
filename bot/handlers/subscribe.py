"""Subscription required handler for the bot."""

from __future__ import annotations

import logging

from aiogram import Bot, F, Router, types
from aiogram.utils.i18n import gettext

from bot.filters import NotSubbedFilter
from bot.keyboards import inline
from database.crud import CRUD
from database.models import RequiredSubscriptions, User

logger = logging.getLogger(__name__)


async def sub_required_handler(
    event: types.Message | types.CallbackQuery,
) -> None:
    """Subscription required handler."""
    try:
        required_chats: list[RequiredSubscriptions] = await CRUD(
            RequiredSubscriptions,
        ).get_all()
        text = gettext("not_subscribed")
        keyboard = inline.get_subscribe_keyboard(gettext, required_chats)

        match event:
            case types.Message():
                await event.answer(text, reply_markup=keyboard)

            case types.CallbackQuery() if event.message:
                await event.message.answer(text, reply_markup=keyboard)

            case _:
                await event.answer(gettext("cannot_send_message"))

    except Exception:
        logger.exception("Failed to send message")


async def sub_check_handler(
    callback: types.CallbackQuery,
    user: User,
    bot: Bot,
) -> None:
    """Subscription check handler."""
    sub_check = NotSubbedFilter()
    if not isinstance(callback.message, types.Message):
        await callback.answer(gettext("cannot_send_message"))
        return

    if await sub_check(callback, user, bot):
        await callback.message.answer(gettext("not_subscribed"))
    else:
        await callback.message.delete()


def register(router: Router) -> None:
    """Register subscription check handler with the router."""
    router.callback_query.register(sub_check_handler, F.data == "sub_check")
    router.callback_query.register(sub_required_handler, NotSubbedFilter())
    router.message.register(sub_required_handler, NotSubbedFilter())
