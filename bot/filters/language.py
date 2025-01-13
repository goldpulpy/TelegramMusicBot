"""Check language filter."""

from aiogram import types
from aiogram.filters import Filter
from database.models import User
from locales import support_languages


class LanguageFilter(Filter):
    """
    A filter that checks if a user's language matches the specified language.
    """

    async def __call__(
        self, update: types.Message | types.CallbackQuery, user: User
    ) -> bool:
        """
        Check if the user's language matches the specified language.
        """
        return not support_languages.is_supported(user.language_code)
