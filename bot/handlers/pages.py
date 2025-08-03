"""Pages handler for the bot."""

import logging

from aiogram import F, Router, types

from bot.keyboards import inline
from bot.utils import load_tracks_from_db
from service.data import Track

logger = logging.getLogger(__name__)


async def pages_handler(callback: types.CallbackQuery) -> None:
    """Handles the pages navigation."""
    try:
        _, _, search_id, page = callback.data.split(":")
        tracks: list[Track] = await load_tracks_from_db(search_id)

        await callback.message.edit_reply_markup(
            reply_markup=inline.get_keyboard_of_tracks(
                tracks, search_id, int(page),
            ),
        )
    except Exception as e:
        logger.error("Failed to send message: %s", e)


def register(router: Router) -> None:
    """Registers pages handler with the router."""
    router.callback_query.register(
        pages_handler, F.data.startswith("track:page"),
    )
