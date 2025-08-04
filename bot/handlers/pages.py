"""Pages handler for the bot."""

import logging
from typing import TYPE_CHECKING

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.i18n import gettext

from bot.keyboards import inline
from bot.utils import load_tracks_from_db

if TYPE_CHECKING:
    from service.data import Track

logger = logging.getLogger(__name__)


async def pages_handler(callback: types.CallbackQuery) -> None:
    """Handle the pages navigation."""
    try:
        if not callback.data:
            await callback.answer(gettext("invalid_data"))
            return

        _, _, search_id, page = callback.data.split(":")
        tracks: list[Track] = await load_tracks_from_db(int(search_id))

        if not isinstance(callback.message, types.Message):
            await callback.answer(gettext("cannot_edit_message"))
            return

        await callback.message.edit_reply_markup(
            reply_markup=inline.get_keyboard_of_tracks(
                tracks,
                int(search_id),
                int(page),
            ),
        )
    except TelegramBadRequest:
        await callback.answer(gettext("cannot_edit_message"))

    except Exception:
        logger.exception("Failed to handle pages navigation")
        await callback.answer(gettext("error_occurred"))


def register(router: Router) -> None:
    """Register pages handler with the router."""
    router.callback_query.register(
        pages_handler,
        F.data.startswith("track:page"),
    )
