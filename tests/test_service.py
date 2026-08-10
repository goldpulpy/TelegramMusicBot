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
        ("  Hello World  ", "https://hello-world.vuxo7.com"),
        ("Rock & Roll!", "https://rock--roll.vuxo7.com"),
        ("MiXeD CaSe", "https://mixed-case.vuxo7.com"),
        ("привет мир", "https://xn----ctbjkdxqigq.vuxo7.com"),
    ],
)
def test_build_search_query(keyword: str, expected: str) -> None:
    assert Music().build_search_query(keyword) == expected


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
        """<li><span class="playlist-name-artist"> Artist </span>
        <span class="playlist-name-title"> Song </span>
        <button class="playlist-play" data-url="https://audio"></button></li>""",
        "html.parser",
    ).li
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
        '<li><span class="playlist-name-title">Song</span></li>',
        '<li><span class="playlist-name-artist">Artist</span></li>',
    ],
)
def test_track_from_element_requires_names(markup: str) -> None:
    element = BeautifulSoup(markup, "html.parser").li
    assert element is not None
    with pytest.raises(ValueError, match="artist name"):
        Track.from_element(element, 0)


def test_track_from_element_requires_audio_element() -> None:
    element = BeautifulSoup(
        '<li><span class="playlist-name-artist">A</span>'
        '<span class="playlist-name-title">T</span></li>',
        "html.parser",
    ).li
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
        "https://hello-world.vuxo7.com",
    )
    assert music._parse_tracks.await_args_list[1].args == (
        "https://vuxo7.com",
    )


@pytest.mark.asyncio
async def test_parse_tracks_returns_ordered_tracks(
    http_response_factory: type,
) -> None:
    response = http_response_factory(
        text_body="""<ul class="playlist">
        <li><span class="playlist-name-artist">A</span>
        <span class="playlist-name-title">One</span>
        <i class="playlist-play" data-url="u1"></i></li>
        <li><span class="playlist-name-artist">B</span>
        <span class="playlist-name-title">Two</span>
        <i class="playlist-play" data-url="u2"></i></li></ul>""",
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
async def test_parse_tracks_rejects_missing_playlist(
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

    with pytest.raises(TypeError, match="playlist"):
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
