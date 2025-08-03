"""Pages handler for the bot."""

import logging
from typing import TYPE_CHECKING

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest

from bot.keyboards import inline
from bot.utils import load_tracks_from_db

if TYPE_CHECKING:
    from service.data import Track

logger = logging.getLogger(__name__)


async def pages_handler(callback: types.CallbackQuery) -> None:
    """Handle the pages navigation."""
    try:
        if not callback.data:
            await callback.answer("Invalid data")
            return

        data_parts = callback.data.split(":")
        if len(data_parts) < 4:
            await callback.answer("Invalid data format")
            return

        _, _, search_id, page = data_parts
        tracks: list[Track] = await load_tracks_from_db(int(search_id))

        if callback.message is None:
            await callback.answer("Cannot edit message")
            return

        await callback.message.edit_reply_markup(
            reply_markup=inline.get_keyboard_of_tracks(
                tracks,
                int(search_id),
                int(page),
            ),
        )
    except TelegramBadRequest:
        await callback.answer("Cannot edit message, please retry")
    except Exception:
        logger.exception("Failed to handle pages navigation")
        await callback.answer("Error occurred")


def register(router: Router) -> None:
    """Register pages handler with the router."""
    router.callback_query.register(
        pages_handler,
        F.data.startswith("track:page"),
    )
