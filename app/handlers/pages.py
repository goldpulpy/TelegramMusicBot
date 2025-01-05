"""Pages handler for the bot."""
import logging
from aiogram import types, Router, F
from service.core import MusicService
from .search import map_song_to_db
from templates import inline, texts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def pages_handler(callback: types.CallbackQuery) -> None:
    """Handles the pages navigation."""
    try:
        _, _, page, keyword = callback.data.split(":")
        page = int(page)

        async with MusicService() as service:
            songs = await service.get_songs_list(keyword)
        songs = await map_song_to_db(songs)
        await callback.message.edit_text(
            texts.SEARCH_RESULTS.format(keyword=keyword),
            reply_markup=inline.get_keyboard_of_songs(keyword, songs, page)
        )
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


def register(router: Router) -> None:
    """Registers pages handler with the router."""
    router.callback_query.register(
        pages_handler, F.data.startswith("song:page")
    )
