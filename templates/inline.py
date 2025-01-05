"""Inline keyboard templates."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models.song_map import Song


def get_keyboard_of_songs(songs: list[Song]) -> InlineKeyboardMarkup:
    """Get songs keyboard."""
    keyboard = []
    for song in songs:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=song.name,
                    callback_data=f"song:id:{song.id}"
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
