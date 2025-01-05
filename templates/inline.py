"""Inline keyboard templates."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models.song_map import Song


def get_keyboard_of_songs(
    keyword: str, songs: list[Song], page: int = 0
) -> InlineKeyboardMarkup:
    """Create paginated inline keyboard for song selection."""
    SONGS_PER_PAGE = 10
    total_pages = max((len(songs) - 1) // SONGS_PER_PAGE, 0)
    page = min(max(0, page), total_pages)

    current_page_songs = songs[
        page * SONGS_PER_PAGE:(page + 1) * SONGS_PER_PAGE
    ]

    keyboard = [
        [
            InlineKeyboardButton(
                text=song.name, callback_data=f"song:id:{song.id}")
        ] for song in current_page_songs
    ]

    if total_pages > 0:
        def create_navigation_button(is_next: bool) -> InlineKeyboardButton:
            """Create navigation button (prev/next) based on current page."""
            is_available = page < total_pages if is_next else page > 0

            return InlineKeyboardButton(
                text="➡️" if is_next else "⬅️" if is_available else "⏺️",
                callback_data=(
                    f"song:page:{page + 1 if is_next else page - 1}:{keyword}"
                    if is_available else "song:noop"
                )
            )

        keyboard.append([
            create_navigation_button(is_next=False),
            InlineKeyboardButton(
                text=f"{page + 1}/{total_pages + 1}",
                callback_data="song:noop"
            ),
            create_navigation_button(is_next=True),
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
