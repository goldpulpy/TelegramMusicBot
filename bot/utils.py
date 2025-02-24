"""Utils for the bot."""
from database.crud import CRUD
from database.models import SearchHistory
from service.data import Track


async def load_tracks_from_db(search_id: int) -> list[Track]:
    """Get tracks from the database."""
    search_history_crud = CRUD(SearchHistory)
    search: SearchHistory = await search_history_crud.get(id=int(search_id))
    return [Track(**track) for track in search.tracks]
