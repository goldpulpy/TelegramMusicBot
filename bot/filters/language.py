"""Check language filter."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.filters import Filter

from locales import support_languages

if TYPE_CHECKING:
    from aiogram import types

    from database.models import User


class LanguageFilter(Filter):
    """A filter that checks if a user's language matches the specified language."""

    async def __call__(
        self, update: types.Message | types.CallbackQuery, user: User,
    ) -> bool:
        """Check if the user's language matches the specified language."""
        return not support_languages.is_supported(user.language_code)
