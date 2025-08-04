"""Utils for the bot."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.types import InputFile, URLInputFile

from database.crud import CRUD
from database.models import SearchHistory
from service.data import Track

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import User


async def load_tracks_from_db(search_id: int) -> list[Track]:
    """Get tracks from the database."""
    search_history_crud = CRUD(SearchHistory)
    search: SearchHistory | None = await search_history_crud.get(
        id=int(search_id),
    )

    if not search:
        return []

    return [Track.from_dict(track) for track in search.tracks]


async def get_user_pic(bot: Bot, user: User) -> InputFile | None:
    """Get user pic."""
    url = f"https://api.telegram.org/file/bot{bot.token}/"

    photos = await user.get_profile_photos(limit=1)

    if photos.total_count:
        best = photos.photos[0][-1]
        bot_pic = await bot.get_file(best.file_id)

        if bot_pic.file_path:
            return URLInputFile(url + bot_pic.file_path)

    return None
