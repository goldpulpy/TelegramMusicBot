"""Inline keyboard templates."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from service.data import Song
from locales import support_languages


def get_keyboard_of_songs(
    songs: list[Song],
    search_id: int,
    page: int = 0
) -> InlineKeyboardMarkup:
    """Create paginated inline keyboard for song selection."""
    SONGS_PER_PAGE = 10

    total_pages = max((len(songs) - 1) // SONGS_PER_PAGE, 0)
    page = min(max(0, page), total_pages)

    start_indx = page * SONGS_PER_PAGE
    end_indx = (page + 1) * SONGS_PER_PAGE
    current_page_songs = songs[start_indx:end_indx]

    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{song.performer} - {song.title}",
                callback_data=f"song:get:{search_id}:{song.index}"
            )
        ] for song in current_page_songs
    ]

    if total_pages > 0:
        def create_navigation_button(is_next: bool) -> InlineKeyboardButton:
            """Create navigation button (prev/next) based on current page."""
            is_available = page < total_pages if is_next else page > 0

            return InlineKeyboardButton(
                text="▶️"
                if is_next and is_available else "⏺️"
                if is_next and not is_available else "◀️"
                if not is_next and is_available else "⏺️",
                callback_data=(
                    f"song:page:{search_id}:"
                    f"{page + 1 if is_next else page - 1}"
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
        keyboard.append([
            InlineKeyboardButton(
                text="🔽",
                callback_data=f"song:all:{search_id}:{start_indx}:{end_indx}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


language_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=language.name,
                callback_data=f"language:set:{language.code}"
            ) for language in support_languages.languages
        ]
    ]
)
