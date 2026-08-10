"""Shared hermetic fixtures for the unit test suite."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ["BOT_TOKEN"] = "1234567890:test-token-safe"
os.environ["POSTGRES_USER"] = "test"
os.environ["POSTGRES_PASSWORD"] = "test"
os.environ["POSTGRES_DB"] = "test"
os.environ["POSTGRES_HOST"] = "localhost"

from service.data import Track

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture
def track_factory() -> Callable[..., Track]:
    """Build a track with deterministic defaults."""

    def build(index: int = 0, **values: Any) -> Track:
        return Track(
            index=index,
            name=values.get("name", f"Artist {index} - Title {index}"),
            title=values.get("title", f"Title {index}"),
            performer=values.get("performer", f"Artist {index}"),
            audio_url=values.get("audio_url", f"https://audio/{index}"),
        )

    return build


@pytest.fixture
def tracks(track_factory: Callable[..., Track]) -> list[Track]:
    """Return enough tracks to exercise pagination."""
    return [track_factory(index=index) for index in range(23)]


@pytest.fixture
def telegram_event() -> MagicMock:
    """Build a Telegram-like event with asynchronous methods."""
    event = MagicMock()
    event.data = None
    event.text = None
    event.answer = AsyncMock()
    event.edit_text = AsyncMock()
    event.edit_reply_markup = AsyncMock()
    return event


@dataclass
class FakeResponse:
    """Minimal aiohttp response async context manager."""

    body: bytes = b""
    text_body: str = ""
    content_length: int | None = None
    error: Exception | None = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def raise_for_status(self) -> None:
        if self.error:
            raise self.error

    async def read(self) -> bytes:
        return self.body

    async def text(self) -> str:
        return self.text_body


@pytest.fixture
def http_response_factory() -> type[FakeResponse]:
    """Expose the controlled HTTP response builder."""
    return FakeResponse


@pytest.fixture
def async_session() -> MagicMock:
    """Return an isolated SQLAlchemy-session double."""
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def session_factory(async_session: MagicMock) -> Callable[[], MagicMock]:
    """Return a factory that always supplies the isolated session."""
    return MagicMock(return_value=async_session)


@pytest.fixture(autouse=True)
def no_external_services(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fail immediately if a test accidentally opens an aiohttp session."""

    def fail_session(*_args: object, **_kwargs: object) -> None:
        msg = "external HTTP sessions are disabled in unit tests"
        raise AssertionError(msg)

    monkeypatch.setattr("aiohttp.ClientSession", fail_session)
