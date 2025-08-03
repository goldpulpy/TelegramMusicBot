"""Check language filter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.filters import Filter

from locales import support_languages

if TYPE_CHECKING:
    from aiogram import types

    from database.models import User


class LanguageFilter(Filter):
    """checks if user's language matches the specified language."""

    async def __call__(
        self,
        update: types.Message | types.CallbackQuery,  # noqa: ARG002
        user: User,
    ) -> bool:
        """Check if the user's language matches the specified language."""
        language_code = user.language_code
        if language_code is None:
            return True

        return not support_languages.is_supported(language_code)
