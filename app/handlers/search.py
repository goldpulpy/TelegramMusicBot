"""Search handler for the bot."""
import logging
from aiogram import types, Router, F
from aiogram.utils.i18n import gettext
from service.core import MusicService
from service.data import Song
from database.crud import CRUD
from database.models.search_history import SearchHistory
from database.models.user import User
from app.keyboards import inline

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
            gettext("searching").format(keyword=keyword)
        )
        async with MusicService() as service:
            songs = await service.get_songs_list(keyword)

        search = await update_search(user, keyword, songs)
        await search_message.edit_text(
            gettext("search_result").format(keyword=keyword),
            reply_markup=inline.get_keyboard_of_songs(
                songs, search.id
            )
        )
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


async def get_song_list(list_type: str) -> list[Song]:
    """Gets the song list."""
    async with MusicService() as service:
        map_list_type = {
            "top": service.get_top_songs,
            "novelties": service.get_novelties
        }
        return await map_list_type[list_type]()


async def song_lists_handler(
    callback: types.CallbackQuery,
    user: User
) -> None:
    """Handles the song lists."""
    _, _, list_type = callback.data.split(":")
    songs = await get_song_list(list_type)
    search = await update_search(user, list_type, songs)
    await callback.message.answer(
        gettext(list_type),
        reply_markup=inline.get_keyboard_of_songs(
            songs, search.id
        )
    )


def register(router: Router) -> None:
    """Registers search handler with the router."""
    router.message.register(search_handler)
    router.callback_query.register(
        song_lists_handler, F.data.startswith("song:list:")
    )
