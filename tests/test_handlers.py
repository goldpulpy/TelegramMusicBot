"""Tests for core search, pagination, and track delivery handlers."""

# pyright: reportArgumentType=false

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from aiogram import types
from aiogram.exceptions import TelegramBadRequest

from bot.handlers.get_track import (
    get_all_from_page_handler,
    get_track_handler,
    send_track,
)
from bot.handlers.pages import pages_handler
from bot.handlers.search import (
    search_handler,
    track_lists_handler,
    update_search,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from service.data import Track


def message_double(text: str | None = None) -> MagicMock:
    """Build a Message instance-shaped mock with async methods."""
    message = MagicMock(spec=types.Message)
    message.text = text
    message.answer = AsyncMock()
    message.edit_text = AsyncMock()
    message.edit_reply_markup = AsyncMock()
    message.answer_audio = AsyncMock()
    message.chat = SimpleNamespace(id=42)
    return message


def callback_double(
    data: str | None,
    message: MagicMock | None = None,
) -> MagicMock:
    """Build a callback query instance-shaped mock."""
    callback = MagicMock(spec=types.CallbackQuery)
    callback.data = data
    callback.message = message
    callback.answer = AsyncMock()
    return callback


def music_context(service: MagicMock) -> MagicMock:
    """Wrap a service double in an async context manager."""
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=service)
    context.__aexit__ = AsyncMock(return_value=None)
    return context


@pytest.mark.asyncio
async def test_update_search_updates_user_and_serializes_tracks(
    track_factory: Callable[..., Track],
) -> None:
    user = SimpleNamespace(id=2, search_queries=4)
    track = track_factory(0)
    user_crud = MagicMock()
    user_crud.update = AsyncMock()
    history = SimpleNamespace(id=9)
    history_crud = MagicMock()
    history_crud.create = AsyncMock(return_value=history)

    with patch(
        "bot.handlers.search.CRUD",
        side_effect=[user_crud, history_crud],
    ):
        result = await update_search(user, "term", [track])

    assert result is history
    user_crud.update.assert_awaited_once_with(user, search_queries=5)
    history_crud.create.assert_awaited_once_with(
        user_id=2,
        keyword="term",
        tracks=[track.__dict__],
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("text", [None, "   ", "x" * 101])
async def test_search_rejects_invalid_text(text: str | None) -> None:
    message = message_double(text)
    with (
        patch("bot.handlers.search.gettext", side_effect=lambda key: key),
        patch("bot.handlers.search.Music") as music,
    ):
        await search_handler(message, SimpleNamespace())

    message.answer.assert_awaited_once_with("search_query_error")
    music.assert_not_called()


@pytest.mark.asyncio
async def test_search_valid_flow_renders_results(
    track_factory: Callable[..., Track],
) -> None:
    message = message_double("  a song  ")
    progress = message_double()
    message.answer.return_value = progress
    track = track_factory(0)
    service = MagicMock()
    service.search = AsyncMock(return_value=[track])
    history = SimpleNamespace(id=11)
    keyboard = MagicMock()
    user = SimpleNamespace(id=2)

    with (
        patch(
            "bot.handlers.search.gettext",
            side_effect=lambda key: key + " {keyword}",
        ),
        patch(
            "bot.handlers.search.Music",
            return_value=music_context(service),
        ),
        patch(
            "bot.handlers.search.update_search",
            AsyncMock(return_value=history),
        ) as update,
        patch(
            "bot.handlers.search.inline.get_keyboard_of_tracks",
            return_value=keyboard,
        ) as get_keyboard,
    ):
        await search_handler(message, user)

    message.answer.assert_awaited_once_with("searching a song")
    service.search.assert_awaited_once_with("a song")
    update.assert_awaited_once_with(user, "a song", [track])
    get_keyboard.assert_called_once_with([track], 11)
    progress.edit_text.assert_awaited_once_with(
        "search_result a song",
        reply_markup=keyboard,
    )


@pytest.mark.asyncio
async def test_search_failure_is_contained() -> None:
    message = message_double("song")
    message.answer.side_effect = RuntimeError("telegram")
    await search_handler(message, SimpleNamespace())


@pytest.mark.asyncio
async def test_track_list_rejects_missing_data() -> None:
    callback = callback_double(None)
    with patch("bot.handlers.search.gettext", side_effect=lambda key: key):
        await track_lists_handler(callback, SimpleNamespace())
    callback.answer.assert_awaited_once_with("invalid_data")


@pytest.mark.asyncio
async def test_track_list_sends_keyboard(
    track_factory: Callable[..., Track],
) -> None:
    message = message_double()
    callback = callback_double("track:list:top_hits", message)
    tracks = [track_factory(0)]
    history = SimpleNamespace(id=3)
    keyboard = MagicMock()

    with (
        patch("bot.handlers.search.gettext", side_effect=lambda key: key),
        patch(
            "bot.handlers.search.get_track_list",
            AsyncMock(return_value=tracks),
        ),
        patch(
            "bot.handlers.search.update_search",
            AsyncMock(return_value=history),
        ),
        patch(
            "bot.handlers.search.inline.get_keyboard_of_tracks",
            return_value=keyboard,
        ),
    ):
        await track_lists_handler(callback, SimpleNamespace())

    message.answer.assert_awaited_once_with("top_hits", reply_markup=keyboard)


@pytest.mark.asyncio
async def test_track_list_without_editable_message_uses_fallback() -> None:
    callback = callback_double("track:list:top_hits", None)
    with (
        patch("bot.handlers.search.gettext", side_effect=lambda key: key),
        patch(
            "bot.handlers.search.get_track_list",
            AsyncMock(return_value=[]),
        ),
        patch(
            "bot.handlers.search.update_search",
            AsyncMock(return_value=SimpleNamespace(id=1)),
        ),
    ):
        await track_lists_handler(callback, SimpleNamespace())
    callback.answer.assert_awaited_once_with("cannot_send_message")


@pytest.mark.asyncio
async def test_pages_rejects_missing_data() -> None:
    callback = callback_double(None)
    with patch("bot.handlers.pages.gettext", side_effect=lambda key: key):
        await pages_handler(callback)
    callback.answer.assert_awaited_once_with("invalid_data")


@pytest.mark.asyncio
async def test_pages_edits_markup(track_factory: Callable[..., Track]) -> None:
    message = message_double()
    callback = callback_double("track:page:4:2", message)
    tracks = [track_factory(0)]
    keyboard = MagicMock()
    with (
        patch(
            "bot.handlers.pages.load_tracks_from_db",
            AsyncMock(return_value=tracks),
        ) as load,
        patch(
            "bot.handlers.pages.inline.get_keyboard_of_tracks",
            return_value=keyboard,
        ) as build,
    ):
        await pages_handler(callback)
    load.assert_awaited_once_with(4)
    build.assert_called_once_with(tracks, 4, 2)
    message.edit_reply_markup.assert_awaited_once_with(reply_markup=keyboard)


@pytest.mark.asyncio
async def test_pages_without_message_uses_fallback() -> None:
    callback = callback_double("track:page:4:0", None)
    with (
        patch("bot.handlers.pages.gettext", side_effect=lambda key: key),
        patch(
            "bot.handlers.pages.load_tracks_from_db",
            AsyncMock(return_value=[]),
        ),
    ):
        await pages_handler(callback)
    callback.answer.assert_awaited_once_with("cannot_edit_message")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    [
        TelegramBadRequest(method=MagicMock(), message="bad edit"),
        ValueError("malformed"),
    ],
)
async def test_pages_errors_use_user_fallback(error: Exception) -> None:
    message = message_double()
    message.edit_reply_markup.side_effect = error
    callback = callback_double("track:page:4:0", message)
    with (
        patch("bot.handlers.pages.gettext", side_effect=lambda key: key),
        patch(
            "bot.handlers.pages.load_tracks_from_db",
            AsyncMock(return_value=[]),
        ),
    ):
        await pages_handler(callback)
    expected = (
        "cannot_edit_message"
        if isinstance(error, TelegramBadRequest)
        else "error_occurred"
    )
    callback.answer.assert_awaited_once_with(expected)


@pytest.mark.asyncio
async def test_get_track_acknowledges_and_delivers(
    track_factory: Callable[..., Track],
) -> None:
    track = track_factory(0)
    callback = callback_double("track:get:3:0", message_double())
    bot = MagicMock()
    with (
        patch("bot.handlers.get_track.gettext", side_effect=lambda key: key),
        patch(
            "bot.handlers.get_track.load_tracks_from_db",
            AsyncMock(return_value=[track]),
        ),
        patch("bot.handlers.get_track.send_track", AsyncMock()) as deliver,
    ):
        await get_track_handler(callback, bot)
    callback.answer.assert_awaited_once_with("track_sending")
    deliver.assert_awaited_once_with(callback, bot, track)


@pytest.mark.asyncio
async def test_get_all_uses_bounded_slice(
    track_factory: Callable[..., Track],
) -> None:
    tracks = [track_factory(index) for index in range(15)]
    callback = callback_double("track:all:3:10:20", message_double())
    bot = MagicMock()
    with (
        patch("bot.handlers.get_track.gettext", side_effect=lambda key: key),
        patch(
            "bot.handlers.get_track.load_tracks_from_db",
            AsyncMock(return_value=tracks),
        ),
        patch("bot.handlers.get_track.send_track", AsyncMock()) as deliver,
    ):
        await get_all_from_page_handler(callback, bot)
    callback.answer.assert_awaited_once_with("track_sending")
    assert deliver.await_args_list == [
        call(callback, bot, track) for track in tracks[10:]
    ]


@pytest.mark.asyncio
async def test_delivery_sends_audio_metadata(
    track_factory: Callable[..., Track],
) -> None:
    track = track_factory(0)
    message = message_double()
    callback = callback_double("track:get:3:0", message)
    bot = MagicMock()
    bot.send_chat_action = AsyncMock()
    bot.get_me = AsyncMock(return_value=SimpleNamespace(username="musicbot"))
    service = MagicMock()
    service.get_audio_bytes = AsyncMock(return_value=b"audio")
    thumbnail = MagicMock()
    with (
        patch(
            "bot.handlers.get_track.gettext",
            side_effect=lambda key: key + " {username}",
        ),
        patch(
            "bot.handlers.get_track.Music",
            return_value=music_context(service),
        ),
        patch(
            "bot.handlers.get_track.get_user_pic",
            AsyncMock(return_value=thumbnail),
        ),
    ):
        await send_track(callback, bot, track)

    bot.send_chat_action.assert_awaited_once_with(42, "upload_document")
    audio = message.answer_audio.await_args
    assert audio.kwargs["title"] == track.title
    assert audio.kwargs["performer"] == track.performer
    assert audio.kwargs["caption"] == "promo_caption musicbot"
    assert audio.kwargs["thumbnail"] is thumbnail


@pytest.mark.asyncio
async def test_delivery_without_chat_uses_fallback(
    track_factory: Callable[..., Track],
) -> None:
    callback = callback_double("track:get:3:0", None)
    with patch("bot.handlers.get_track.gettext", side_effect=lambda key: key):
        await send_track(callback, MagicMock(), track_factory(0))
    callback.answer.assert_awaited_once_with("cannot_access_chat")


@pytest.mark.asyncio
async def test_delivery_failure_is_contained(
    track_factory: Callable[..., Track],
) -> None:
    message = message_double()
    callback = callback_double("track:get:3:0", message)
    bot = MagicMock()
    bot.send_chat_action = AsyncMock(side_effect=RuntimeError("telegram"))
    with patch("bot.handlers.get_track.gettext", side_effect=lambda key: key):
        await send_track(callback, bot, track_factory(0))
    message.answer.assert_awaited_once_with("send_track_error")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("data", "loads_tracks"),
    [
        (None, False),
        ("bad", False),
        ("track:get:3:99", True),
    ],
)
async def test_get_track_invalid_inputs_use_fallback(
    data: str | None,
    loads_tracks: bool,
) -> None:
    callback = callback_double(data, message_double())
    with (
        patch("bot.handlers.get_track.gettext", side_effect=lambda key: key),
        patch(
            "bot.handlers.get_track.load_tracks_from_db",
            AsyncMock(return_value=[]),
        ) as load_tracks,
        patch("bot.handlers.get_track.send_track", AsyncMock()) as deliver,
    ):
        await get_track_handler(callback, MagicMock())
    callback.answer.assert_awaited_once_with("invalid_data")
    deliver.assert_not_awaited()
    assert bool(load_tracks.await_count) is loads_tracks
