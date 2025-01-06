"""Search handler for the bot."""
import logging
from aiogram import types, Router
from service.core import MusicService
from service.data import Song
from database.crud import CRUD
from database.models.search_history import SearchHistory
from database.models.user import User
from templates import inline, texts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_search(
    user: User, keyword: str, songs: list[Song]
) -> SearchHistory:
    """Updates the user in the database."""
    user_crud = CRUD(User)
    await user_crud.update(user, search_queries=user.search_queries + 1)

    search_history_crud = CRUD(SearchHistory)
    search = await search_history_crud.create(
        user_id=user.id,
        keyword=keyword,
        songs=[song.__dict__ for song in songs]
    )
    return search


async def search_handler(message: types.Message, user: User) -> None:
    """Handles the search."""
    try:
        keyword = message.text.replace(":", "").strip()
        search_message = await message.answer(
            texts.SEARCHING.format(keyword=keyword)
        )
        async with MusicService() as service:
            songs = await service.get_songs_list(keyword)

        search = await update_search(user, keyword, songs)
        await search_message.edit_text(
            texts.SEARCH_RESULTS.format(keyword=keyword),
            reply_markup=inline.get_keyboard_of_songs(
                keyword, songs, search.id
            )
        )
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


def register(router: Router) -> None:
    """Registers search handler with the router."""
    router.message.register(search_handler)
