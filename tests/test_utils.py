"""Tests for bot utility boundaries."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import URLInputFile

from bot.utils import get_user_pic, load_tracks_from_db

if TYPE_CHECKING:
    from collections.abc import Callable

    from service.data import Track


@pytest.mark.asyncio
async def test_load_tracks_reconstructs_typed_tracks(
    track_factory: Callable[..., Track],
) -> None:
    expected = track_factory(index=3)
    history = SimpleNamespace(tracks=[expected.__dict__])
    with patch("bot.utils.CRUD") as crud:
        crud.return_value.get = AsyncMock(return_value=history)
        result = await load_tracks_from_db(8)

    assert result == [expected]
    crud.return_value.get.assert_awaited_once_with(id=8)


@pytest.mark.asyncio
async def test_load_tracks_returns_empty_for_missing_history() -> None:
    with patch("bot.utils.CRUD") as crud:
        crud.return_value.get = AsyncMock(return_value=None)
        assert await load_tracks_from_db(9) == []


@pytest.mark.asyncio
async def test_get_user_pic_builds_telegram_file_url() -> None:
    bot = MagicMock(token="token")
    bot.get_file = AsyncMock(
        return_value=SimpleNamespace(file_path="photos/a.jpg"),
    )
    user = MagicMock()
    user.get_profile_photos = AsyncMock(
        return_value=SimpleNamespace(
            total_count=1,
            photos=[[SimpleNamespace(file_id="large")]],
        ),
    )

    result = await get_user_pic(bot, user)

    assert isinstance(result, URLInputFile)
    assert result.url == "https://api.telegram.org/file/bottoken/photos/a.jpg"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("photos", "file_path"),
    [
        (SimpleNamespace(total_count=0, photos=[]), None),
        (
            SimpleNamespace(
                total_count=1,
                photos=[[SimpleNamespace(file_id="large")]],
            ),
            None,
        ),
    ],
)
async def test_get_user_pic_returns_none_without_available_path(
    photos: SimpleNamespace,
    file_path: str | None,
) -> None:
    bot = MagicMock(token="token")
    bot.get_file = AsyncMock(return_value=SimpleNamespace(file_path=file_path))
    user = MagicMock()
    user.get_profile_photos = AsyncMock(return_value=photos)

    assert await get_user_pic(bot, user) is None
