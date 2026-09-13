"""Tests for music-provider data conversion and service behavior."""

# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from bs4 import BeautifulSoup
from tenacity import wait_none

from service.core import Music
from service.data import ServiceConfig, Track
from service.exceptions import MusicServiceError

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.parametrize(
    ("keyword", "expected"),
    [
        (
            "  Hello World  ",
            "https://dydki.net/?mp3=%20%20Hello%20World%20%20",
        ),
        (
            "Rock & Roll!",
            "https://dydki.net/?mp3=Rock%20%26%20Roll%21",
        ),
        ("MiXeD CaSe", "https://dydki.net/?mp3=MiXeD%20CaSe"),
        (
            "привет мир",
            (
                "https://dydki.net/?mp3="
                "%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82%20"
                "%D0%BC%D0%B8%D1%80"
            ),
        ),
    ],
)
def test_build_search_query(keyword: str, expected: str) -> None:
    assert Music().build_search_query(keyword) == expected


def test_build_search_query_derives_no_host() -> None:
    url = Music().build_search_query("evil.example.com")
    assert url == "https://dydki.net/?mp3=evil.example.com"


def test_track_from_dict_converts_index() -> None:
    track = Track.from_dict(
        {
            "index": "2",
            "name": "Artist - Song",
            "title": "Song",
            "performer": "Artist",
            "audio_url": "https://audio",
        },
    )
    assert track.index == 2
    assert track.name == "Artist - Song"


def test_track_from_element_reads_metadata() -> None:
    element = BeautifulSoup(
        """<div class="chkd" data-mp3="https://audio">
        <span class="track__artist"> Artist </span>
        <span class="track__title"> Song </span></div>""",
        "html.parser",
    ).div
    assert element is not None

    track = Track.from_element(element, 4)

    assert track == Track(
        4,
        "Artist - Song",
        "Song",
        "Artist",
        "https://audio",
    )


@pytest.mark.parametrize(
    "markup",
    [
        '<div class="chkd"><span class="track__title">Song</span></div>',
        '<div class="chkd"><span class="track__artist">Artist</span></div>',
    ],
)
def test_track_from_element_requires_names(markup: str) -> None:
    element = BeautifulSoup(markup, "html.parser").div
    assert element is not None
    with pytest.raises(ValueError, match="artist name"):
        Track.from_element(element, 0)


def test_track_from_element_requires_audio_element() -> None:
    element = BeautifulSoup(
        '<div class="chkd"><span class="track__artist">A</span>'
        '<span class="track__title">T</span></div>',
        "html.parser",
    ).div
    assert element is not None
    with pytest.raises(TypeError, match="audio URL"):
        Track.from_element(element, 0)


@pytest.mark.asyncio
async def test_connect_disconnect_session_lifecycle() -> None:
    session = MagicMock()
    session.close = AsyncMock()
    with patch(
        "service.core.aiohttp.ClientSession",
        return_value=session,
    ) as factory:
        music = Music(ServiceConfig(headers={}))
        await music.connect()
        await music.connect()
        await music.disconnect()

    factory.assert_called_once_with(headers={})
    session.close.assert_awaited_once()
    assert music._session is None


@pytest.mark.asyncio
async def test_search_requires_session() -> None:
    with pytest.raises(MusicServiceError, match="initialize session"):
        await Music().search("song")


@pytest.mark.asyncio
async def test_search_and_top_hits_use_expected_urls() -> None:
    music = Music()
    music._session = MagicMock()
    music._parse_tracks = AsyncMock(return_value=[])

    await music.search("Hello World")
    await music.get_top_hits()

    assert music._parse_tracks.await_args_list[0].args == (
        "https://dydki.net/?mp3=Hello%20World",
    )
    assert music._parse_tracks.await_args_list[1].args == (
        "https://dydki.net/",
    )


@pytest.mark.asyncio
async def test_parse_tracks_returns_ordered_tracks(
    http_response_factory: type,
) -> None:
    response = http_response_factory(
        text_body="""<div class="results">
        <div class="chkd" data-mp3="u1">
        <span class="track__artist">A</span>
        <span class="track__title">One</span></div>
        <div class="chkd" data-mp3="u2">
        <span class="track__artist">B</span>
        <span class="track__title">Two</span></div></div>""",
    )
    music = Music()
    music._session = MagicMock()
    music._session.get.return_value = response

    result = await music._parse_tracks("https://provider")

    assert [(track.index, track.name) for track in result] == [
        (0, "A - One"),
        (1, "B - Two"),
    ]


@pytest.mark.asyncio
async def test_parse_tracks_empty_results_returns_empty_list(
    http_response_factory: type,
) -> None:
    music = Music()
    music._session = MagicMock()
    music._session.get.return_value = http_response_factory(
        text_body='<div class="results"></div>',
    )

    assert await music._parse_tracks("https://provider") == []


@pytest.mark.asyncio
async def test_parse_tracks_rejects_missing_results(
    http_response_factory: type,
) -> None:
    music = Music()
    music._session = MagicMock()
    music._session.get.return_value = http_response_factory(
        text_body="<html />",
    )
    parse_once = music._parse_tracks.retry_with(
        stop=lambda _state: True,
        wait=wait_none(),
        reraise=True,
    )

    with pytest.raises(TypeError, match="results"):
        await parse_once(music, "https://provider")


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [aiohttp.ClientError("bad"), TimeoutError()])
async def test_parse_tracks_translates_network_errors_without_delay(
    http_response_factory: type,
    error: Exception,
) -> None:
    music = Music()
    music._session = MagicMock()
    music._session.get.return_value = http_response_factory(error=error)
    parse_once = music._parse_tracks.retry_with(
        stop=lambda _state: True,
        wait=wait_none(),
        reraise=True,
    )

    with pytest.raises(MusicServiceError, match="Failed to search music"):
        await parse_once(music, "https://provider")


@pytest.mark.asyncio
async def test_download_returns_bytes(
    track_factory: Callable[..., Track],
    http_response_factory: type,
) -> None:
    music = Music()
    music._session = MagicMock()
    music._session.get.return_value = http_response_factory(body=b"audio")

    assert await music._download_data("url", "audio", "name") == b"audio"


@pytest.mark.asyncio
async def test_download_rejects_declared_oversize(
    http_response_factory: type,
) -> None:
    music = Music()
    music._session = MagicMock()
    music._session.get.return_value = http_response_factory(
        content_length=50 * 1024 * 1024 + 1,
    )

    with pytest.raises(MusicServiceError, match="File too large"):
        await music._download_data("url", "audio", "name")


@pytest.mark.asyncio
async def test_download_translates_network_error(
    http_response_factory: type,
) -> None:
    music = Music()
    music._session = MagicMock()
    music._session.get.return_value = http_response_factory(
        error=aiohttp.ClientError("bad"),
    )

    with pytest.raises(MusicServiceError, match="Failed to download audio"):
        await music._download_data("url", "audio", "name")
