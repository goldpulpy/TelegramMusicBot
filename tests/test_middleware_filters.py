"""Tests for authentication, localization, and access filters."""

# pyright: reportArgumentType=false

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import types
from aiogram.enums import ChatMemberStatus, ChatType

from bot.filters.is_private_chat import IsPrivateChatFilter
from bot.filters.language import LanguageFilter
from bot.filters.not_subbed import NotSubbedFilter
from bot.middlewares.auth_middleware import AuthMiddleware
from bot.middlewares.i18n_middleware import I18nMiddleware


def telegram_user(**values: object) -> SimpleNamespace:
    """Build a Telegram user-shaped object."""
    defaults = {
        "id": 1,
        "username": "tester",
        "first_name": "Test",
        "last_name": "User",
        "language_code": "en",
    }
    defaults.update(values)
    return SimpleNamespace(**defaults)


@pytest.mark.asyncio
async def test_auth_creates_new_user_and_injects_it() -> None:
    middleware = AuthMiddleware()
    crud = MagicMock()
    crud.get = AsyncMock(return_value=None)
    persisted = SimpleNamespace(id=1)
    crud.create = AsyncMock(return_value=persisted)
    middleware._get_user_crud = MagicMock(return_value=crud)
    handler = AsyncMock(return_value="handled")
    source_user = telegram_user()
    data = {"event_from_user": source_user}

    result = await middleware(handler, MagicMock(), data)

    assert result == "handled"
    crud.create.assert_awaited_once_with(
        id=1,
        username="tester",
        first_name="Test",
        last_name="User",
        language_code="en",
    )
    assert data["user"] is persisted
    handler.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_refreshes_existing_user() -> None:
    middleware = AuthMiddleware()
    existing = SimpleNamespace(id=1)
    crud = MagicMock()
    crud.get = AsyncMock(return_value=existing)
    crud.update = AsyncMock(return_value=existing)
    middleware._get_user_crud = MagicMock(return_value=crud)

    result = await middleware.ensure_user_in_db(telegram_user())

    assert result is existing
    crud.update.assert_awaited_once()
    values = crud.update.await_args.kwargs
    assert values["username"] == "tester"
    assert "updated_at" in values


@pytest.mark.asyncio
async def test_auth_propagates_persistence_failure() -> None:
    middleware = AuthMiddleware()
    crud = MagicMock()
    error = RuntimeError("db")
    crud.get = AsyncMock(side_effect=error)
    middleware._get_user_crud = MagicMock(return_value=crud)

    with pytest.raises(RuntimeError) as raised:
        await middleware.ensure_user_in_db(telegram_user())
    assert raised.value is error


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("language", "expected"),
    [("ru", "ru"), (None, "en")],
)
async def test_i18n_locale(language: str | None, expected: str) -> None:
    middleware = object.__new__(I18nMiddleware)
    result = await middleware.get_locale(
        MagicMock(),
        {"user": SimpleNamespace(language_code=language)},
    )
    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("language", "supported", "expected"),
    [(None, True, True), ("en", True, False), ("xx", False, True)],
)
async def test_language_filter(
    language: str | None,
    supported: bool,
    expected: bool,
) -> None:
    with patch(
        "bot.filters.language.support_languages.is_supported",
        return_value=supported,
    ):
        result = await LanguageFilter()(
            MagicMock(),
            SimpleNamespace(language_code=language),
        )
    assert result is expected


@pytest.mark.asyncio
async def test_not_subbed_allows_when_no_requirements() -> None:
    with patch("bot.filters.not_subbed.CRUD") as crud:
        crud.return_value.get_all = AsyncMock(return_value=[])
        result = await NotSubbedFilter()(
            MagicMock(),
            telegram_user(),
            MagicMock(),
        )
    assert result is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (ChatMemberStatus.MEMBER, False),
        (ChatMemberStatus.ADMINISTRATOR, False),
        (ChatMemberStatus.LEFT, True),
    ],
)
async def test_not_subbed_membership_status(
    status: ChatMemberStatus,
    expected: bool,
) -> None:
    subscription = SimpleNamespace(chat_id=-1)
    chat = MagicMock()
    chat.get_member = AsyncMock(return_value=SimpleNamespace(status=status))
    bot = MagicMock()
    bot.get_chat = AsyncMock(return_value=chat)

    assert (
        await NotSubbedFilter()._not_subscribe(
            subscription,
            telegram_user(),
            bot,
        )
        is expected
    )


@pytest.mark.asyncio
async def test_not_subbed_ignores_inaccessible_chat() -> None:
    bot = MagicMock()
    bot.get_chat = AsyncMock(side_effect=RuntimeError("gone"))
    result = await NotSubbedFilter()._not_subscribe(
        SimpleNamespace(chat_id=-1),
        telegram_user(),
        bot,
    )
    assert result is False


@pytest.mark.asyncio
async def test_not_subbed_blocks_failed_member_lookup() -> None:
    chat = MagicMock()
    chat.get_member = AsyncMock(side_effect=RuntimeError("forbidden"))
    bot = MagicMock()
    bot.get_chat = AsyncMock(return_value=chat)
    result = await NotSubbedFilter()._not_subscribe(
        SimpleNamespace(chat_id=-1),
        telegram_user(),
        bot,
    )
    assert result is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("chat_type", "expected"),
    [(ChatType.PRIVATE, True), (ChatType.GROUP, False)],
)
async def test_private_chat_message(
    chat_type: ChatType,
    expected: bool,
) -> None:
    message = types.Message.model_construct(
        chat=SimpleNamespace(type=chat_type),
    )
    assert await IsPrivateChatFilter()(message) is expected


@pytest.mark.asyncio
async def test_private_chat_callback_uses_message() -> None:
    message = types.Message.model_construct(
        chat=SimpleNamespace(type=ChatType.PRIVATE),
    )
    callback = types.CallbackQuery.model_construct(message=message)
    assert await IsPrivateChatFilter()(callback) is True


@pytest.mark.asyncio
async def test_private_chat_callback_without_message_is_false() -> None:
    callback = MagicMock(spec=types.CallbackQuery)
    callback.message = None
    assert await IsPrivateChatFilter()(callback) is False
