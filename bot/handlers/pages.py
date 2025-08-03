"""Pages handler for the bot."""

import logging
from typing import TYPE_CHECKING

from aiogram import F, Router, types

from bot.keyboards import inline
from bot.utils import load_tracks_from_db

if TYPE_CHECKING:
    from service.data import Track

logger = logging.getLogger(__name__)


async def pages_handler(callback: types.CallbackQuery) -> None:
    """Handle the pages navigation."""
    try:
        _, _, search_id, page = callback.data.split(":")
        tracks: list[Track] = await load_tracks_from_db(search_id)

        await callback.message.edit_reply_markup(
            reply_markup=inline.get_keyboard_of_tracks(
                tracks,
                search_id,
                int(page),
            ),
        )
    except Exception:
        logger.exception("Failed to send message")


def register(router: Router) -> None:
    """Register pages handler with the router."""
    router.callback_query.register(
        pages_handler,
        F.data.startswith("track:page"),
    )
