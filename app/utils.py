"""Utils for the bot."""
from database.crud import CRUD
from database.models import SearchHistory
from service.data import Song


async def load_songs_from_db(search_id: int) -> list[Song]:
    """Get songs from the database."""
    search_history_crud = CRUD(SearchHistory)
    search: SearchHistory = await search_history_crud.get(id=int(search_id))
    return [Song(**song) for song in search.songs]
