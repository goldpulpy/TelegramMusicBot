"""Pages handler for the bot."""
import logging
from aiogram import types, Router, F
from service.data import Song
from templates import inline, texts
from app.utils import load_songs_from_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def pages_handler(callback: types.CallbackQuery) -> None:
    """Handles the pages navigation."""
    try:
        _, _, search_id, page, keyword = callback.data.split(":")
        songs: list[Song] = await load_songs_from_db(search_id)

        await callback.message.edit_text(
            texts.SEARCH_RESULTS.format(keyword=keyword),
            reply_markup=inline.get_keyboard_of_songs(
                keyword, songs, search_id, int(page)
            )
        )
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


def register(router: Router) -> None:
    """Registers pages handler with the router."""
    router.callback_query.register(
        pages_handler, F.data.startswith("song:page")
    )
