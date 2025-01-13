"""Inline keyboard templates."""
from typing import Callable
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from service.data import Track
from locales import support_languages


def get_keyboard_of_tracks(
    tracks: list[Track],
    search_id: int,
    page: int = 0
) -> InlineKeyboardMarkup:
    """Create paginated inline keyboard for track selection."""
    TRACKS_PER_PAGE = 10

    total_pages = max((len(tracks) - 1) // TRACKS_PER_PAGE, 0)
    page = min(max(0, page), total_pages)

    start_indx = page * TRACKS_PER_PAGE
    end_indx = (page + 1) * TRACKS_PER_PAGE
    current_page = tracks[start_indx:end_indx]

    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{track.performer} - {track.title}",
                callback_data=f"track:get:{search_id}:{track.index}"
            )
        ] for track in current_page
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
                    f"track:page:{search_id}:"
                    f"{page + 1 if is_next else page - 1}"
                    if is_available else "track:noop"
                )
            )

        keyboard.append([
            create_navigation_button(is_next=False),
            InlineKeyboardButton(
                text=f"{page + 1}/{total_pages + 1}",
                callback_data="track:noop"
            ),
            create_navigation_button(is_next=True),
        ])
        keyboard.append([
            InlineKeyboardButton(
                text="🔽",
                callback_data=f"track:all:{search_id}:{start_indx}:{end_indx}"
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


def get_menu_keyboard(gettext: Callable[[str], str]) -> InlineKeyboardMarkup:
    """Get menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=gettext("top_hits_button"),
                    callback_data="track:list:top_hits"
                ),
                InlineKeyboardButton(
                    text=gettext("new_hits_button"),
                    callback_data="track:list:new_hits"
                )
            ],
            [
                InlineKeyboardButton(
                    text=gettext("faq_button"), callback_data="faq"
                ),
                InlineKeyboardButton(
                    text=gettext("language_button"), callback_data="language"
                )
            ],
        ]
    )


def get_back_keyboard(
    gettext: Callable[[str], str], callback_data: str
) -> InlineKeyboardMarkup:
    """Get back keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=gettext("back_button"), callback_data=callback_data
                )
            ]
        ]
    )
