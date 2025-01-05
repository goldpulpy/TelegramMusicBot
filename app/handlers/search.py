"""Search handler for the bot."""
import logging
from aiogram import types, Router
from service.core import MusicService
from database.crud import CRUD
from database.models.song_map import Song
from database.models.search_history import SearchHistory
from database.models.user import User
from templates import inline, texts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def map_song_to_db(songs: list[Song]) -> list[Song]:
    """Maps songs to the database, creating new entries if they don't exist."""
    song_crud = CRUD(Song)
    songs_from_db = []

    for song in songs:
        songs_from_db.append(
            await song_crud.get(hash=song.hash) or
            await song_crud.create(**song.__dict__)
        )

    return songs_from_db


async def update_search_stat(user: User, keyword: str) -> None:
    """Updates the user in the database."""
    user_crud = CRUD(User)
    await user_crud.update(user, search_queries=user.search_queries + 1)

    search_history_crud = CRUD(SearchHistory)
    await search_history_crud.create(user_id=user.id, keyword=keyword)


async def search_handler(message: types.Message, user: User) -> None:
    """Handles the search."""
    try:
        keyword = message.text.replace(":", "").strip()
        search_message = await message.answer(texts.SEARCHING)
        async with MusicService() as service:
            songs = await service.get_songs_list(keyword)

        songs = await map_song_to_db(songs)
        await search_message.edit_text(
            texts.SEARCH_RESULTS.format(keyword=keyword),
            reply_markup=inline.get_keyboard_of_songs(keyword, songs)
        )
        await update_search_stat(user, keyword)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


def register(router: Router) -> None:
    """Registers search handler with the router."""
    router.message.register(search_handler)
