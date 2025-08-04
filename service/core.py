"""Music service core module for downloading and searching music."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

import aiohttp
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup, Tag
from tenacity import retry, stop_after_attempt, wait_exponential
from typing_extensions import Self

from .data import ServiceConfig, Track
from .exceptions import MusicServiceError

if TYPE_CHECKING:
    from types import TracebackType

logger = logging.getLogger(__name__)


class Music:
    """Service for searching and downloading music."""

    BASE_URL = "vuxo7.com"

    def __init__(self, config: ServiceConfig | None = None) -> None:
        """Initialize music service with optional configuration."""
        self._config = config or ServiceConfig()
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> Self:
        """Context manager entry point."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit point."""
        await self.disconnect()

    async def connect(self) -> None:
        """Initialize HTTP session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self._config.headers)

    async def disconnect(self) -> None:
        """Close HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def search(self, keyword: str) -> list[Track]:
        """Search for music by keyword."""
        if not self._session:
            msg = "Failed to initialize session"
            raise MusicServiceError(msg)

        url = self.build_search_query(keyword)
        logger.info("Searching music with keyword: %s", keyword)

        return await self._parse_tracks(url)

    async def get_top_hits(self) -> list[Track]:
        """Get top tracks."""
        return await self._parse_tracks(f"https://{self.BASE_URL}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
    )
    async def _parse_tracks(self, url: str) -> list[Track]:
        """Parse tracks from the given URL."""
        try:
            if not self._session:
                msg = "Failed to initialize session"
                raise MusicServiceError(msg)

            async with self._session.get(
                url,
                timeout=ClientTimeout(total=self._config.timeout),
            ) as response:
                response.raise_for_status()
                soup = BeautifulSoup(await response.text(), "html.parser")
                playlist = soup.find("ul", class_="playlist")

                if not isinstance(playlist, Tag):
                    msg = "Could not find playlist element"
                    raise TypeError(msg)

                tracks = [
                    Track.from_element(track_data, index)
                    for index, track_data in enumerate(
                        playlist.find_all("li"),
                    )
                ]

            logger.info("Found %d tracks", len(tracks))

        except (aiohttp.ClientError, TimeoutError) as e:
            msg = f"Failed to search music: {e!s}"
            raise MusicServiceError(msg) from e

        return tracks

    def _raise_file_too_large_error(self, content_length: int) -> None:
        """Raise an error for files that are too large."""
        msg = f"File too large: {content_length} bytes"
        raise MusicServiceError(msg)

    async def _download_data(
        self,
        url: str,
        resource_type: str,
        track_name: str,
    ) -> bytes:
        """Download data."""
        max_size = 50 * 1024 * 1024  # 50MB

        if not self._session:
            msg = "Failed to initialize session"
            raise MusicServiceError(msg)

        logger.info("Downloading %s for track: %s", resource_type, track_name)

        try:
            async with self._session.get(
                url,
                timeout=ClientTimeout(total=self._config.timeout),
            ) as response:
                response.raise_for_status()
                content_length = response.content_length

                if content_length and content_length > max_size:
                    self._raise_file_too_large_error(content_length)

                return await response.read()

        except (aiohttp.ClientError, TimeoutError) as e:
            msg = f"Failed to download {resource_type}"
            raise MusicServiceError(msg) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
    )
    async def get_audio_bytes(self, track: Track) -> bytes:
        """Download music file."""
        return await self._download_data(track.audio_url, "audio", track.name)

    def build_search_query(self, keyword: str) -> str:
        """Build search query with cleaned keyword."""
        cleaned = re.sub(r"[^\w\s]", "", keyword)
        query = cleaned.strip().lower().replace(" ", "-")

        try:
            subdomain = query.encode("idna").decode("ascii")
        except UnicodeError:
            subdomain = query

        return f"https://{subdomain}.{self.BASE_URL}"
