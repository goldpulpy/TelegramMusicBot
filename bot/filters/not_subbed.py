"""Check if user is subbed to the channel."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

from aiogram.enums import ChatMemberStatus
from aiogram.filters import Filter

from database.crud import CRUD
from database.models import RequiredSubscriptions, User

if TYPE_CHECKING:
    from aiogram import Bot, types

logger = logging.getLogger(__name__)


class NotSubbedFilter(Filter):
    """A filter that checks if a user is subbed to the channel."""

    ALLOWED_STATUSES: ClassVar[set[ChatMemberStatus]] = {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    }

    async def __call__(
        self,
        update: types.Message | types.CallbackQuery,  # noqa: ARG002
        user: User,
        bot: Bot,
    ) -> bool:
        """Check if the user is not subscribed to any required channels.

        Args:
            update: Update object.
            user: User object.
            bot: Bot object.

        Returns:
            True if user is NOT subscribed to ANY required channel.
            False if user is subscribed to ALL required channels.

        """
        chats = await CRUD(RequiredSubscriptions).get_all()

        if not chats:
            return False

        for chat in chats:
            if await self._not_subscribe(chat, user, bot):
                return True
        return False

    async def _not_subscribe(
        self,
        sub: RequiredSubscriptions,
        user: User,
        bot: Bot,
    ) -> bool:
        """Check if the user is subscribed to the channel.

        Args:
            sub: RequiredSubscriptions object.
            user: User object.
            bot: Bot object.

        Returns:
            True if user is NOT subscribed.
            False if user is subscribed or if channel is not accessible.

        """
        try:
            chat = await bot.get_chat(sub.chat_id)
        except Exception:
            logger.exception("Failed to get chat %s", sub.chat_id)
            return False

        try:
            member = await chat.get_member(user.id)
        except Exception:
            return True
        else:
            return member.status not in self.ALLOWED_STATUSES
