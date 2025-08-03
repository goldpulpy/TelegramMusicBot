"""Filter for checking if the chat is private."""

from __future__ import annotations

from aiogram.enums import ChatType
from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message


class IsPrivateChatFilter(Filter):
    """Filter for checking if the chat is private."""

    async def __call__(
        self,
        event: Message | CallbackQuery,
    ) -> bool:
        """Check if the chat is private."""
        if isinstance(event, CallbackQuery):
            message = event.message
            if not isinstance(message, Message):
                return False
        else:
            message = event

        return message.chat.type == ChatType.PRIVATE
