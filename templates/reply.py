"""Replays for the bot."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Account")],
    ],
    resize_keyboard=True
)
