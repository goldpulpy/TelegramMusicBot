"""Custom i18n middleware (language selection)."""
from aiogram.types import Message
from aiogram.utils.i18n.middleware import I18nMiddleware as BaseI18nMiddleware
from database.models import User


class I18nMiddleware(BaseI18nMiddleware):
    """Custom i18n middleware for the bot."""

    async def get_locale(self, event: Message, data: dict) -> str:
        """Get user locale."""
        user: User = data['user']
        return user.language_code
