"""Search handler for the bot."""
import logging
from aiogram import types, Router, F
from aiogram.utils.i18n import gettext
from service import Music, Track
from database.crud import CRUD
from database.models import SearchHistory, User
from app.keyboards import inline


logger = logging.getLogger(__name__)


async def update_search(
    user: User, keyword: str, tracks: list[Track]
) -> SearchHistory:
    """Updates the user in the database."""
    user_crud = CRUD(User)
    await user_crud.update(user, search_queries=user.search_queries + 1)

    search_history_crud = CRUD(SearchHistory)
    search = await search_history_crud.create(
        user_id=user.id,
        keyword=keyword,
        tracks=[track.__dict__ for track in tracks]
    )
    return search


async def search_handler(message: types.Message, user: User) -> None:
    """Handles the search."""
    try:
        keyword = message.text.replace(":", "").strip()
        search_message = await message.answer(
            gettext("searching").format(keyword=keyword)
        )
        async with Music() as service:
            tracks = await service.search(keyword)

        search = await update_search(user, keyword, tracks)
        await search_message.edit_text(
            gettext("search_result").format(keyword=keyword),
            reply_markup=inline.get_keyboard_of_tracks(tracks, search.id)
        )
    except Exception as e:
        logger.error("Failed to send message: %s", e)


async def get_track_list(list_type: str) -> list[Track]:
    """Gets the track list."""
    async with Music() as service:
        map_list_type = {
            "top_hits": service.get_top_hits,
            "new_hits": service.get_new_hits
        }
        return await map_list_type[list_type]()


async def track_lists_handler(
    callback: types.CallbackQuery,
    user: User
) -> None:
    """Handles the track lists."""
    _, _, list_type = callback.data.split(":")
    tracks = await get_track_list(list_type)
    search = await update_search(user, list_type, tracks)
    await callback.message.answer(
        gettext(list_type),
        reply_markup=inline.get_keyboard_of_tracks(
            tracks, search.id
        )
    )


def register(router: Router) -> None:
    """Registers search handler with the router."""
    router.message.register(search_handler)
    router.callback_query.register(
        track_lists_handler, F.data.startswith("track:list:")
    )
