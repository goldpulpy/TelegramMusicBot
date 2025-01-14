"""Subscription required handler for the bot."""
import logging
from aiogram import types, Router, F, Bot
from aiogram.utils.i18n import gettext
from bot.keyboards import inline
from bot.filters import NotSubbedFilter
from database.models import RequiredSubscriptions, User
from database.crud import CRUD

logger = logging.getLogger(__name__)


async def sub_required_handler(
    event: types.Message | types.CallbackQuery,
) -> None:
    """Subscription required handler."""
    try:
        required_chats = await CRUD(RequiredSubscriptions).get_all()
        text = gettext("not_subscribed")
        keyboard = inline.get_subscribe_keyboard(gettext, required_chats)

        if isinstance(event, types.Message):
            await event.answer(text, reply_markup=keyboard)
        else:
            await event.message.answer(text, reply_markup=keyboard)
    except Exception as e:
        logger.error("Failed to send message: %s", e)


async def sub_check_handler(
    callback: types.CallbackQuery, user: User, bot: Bot,
) -> None:
    """Subscription check handler."""
    sub_check = NotSubbedFilter()

    if await sub_check(callback, user, bot):
        await callback.message.answer(gettext("not_subscribed"))
    else:
        await callback.message.delete()


def register(router: Router) -> None:
    """Registers FAQ handler with the router."""
    router.callback_query.register(sub_check_handler, F.data == "sub_check")
    router.callback_query.register(sub_required_handler, NotSubbedFilter())
    router.message.register(sub_required_handler, NotSubbedFilter())
