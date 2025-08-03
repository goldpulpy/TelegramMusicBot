"""Music service core module for downloading and searching music."""

import logging
import urllib.parse
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

from .data import ServiceConfig, Track
from .exceptions import MusicServiceError

logger = logging.getLogger(__name__)


class Music:
    """Service for searching and downloading music."""

    BASE_URL = "https://mp3wr.com"
    TRACK_DOWNLOAD_URL = "https://cdn.mp3wr.com"

    def __init__(self, config: Optional[ServiceConfig] = None) -> None:
        """Initialize music service with optional configuration."""
        self._config = config or ServiceConfig()
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "Music":
        """Context manager entry point."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
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
            await self.connect()

        url = urllib.parse.urljoin(self.BASE_URL, f"search/{keyword}")
        logger.info("Searching music with keyword: %s", keyword)

        return await self._parse_tracks(url, is_search=True)

    async def get_top_hits(self) -> list[Track]:
        """Get top tracks."""
        url = urllib.parse.urljoin(self.BASE_URL, "besthit")
        return await self._parse_tracks(url)

    async def get_new_hits(self) -> list[Track]:
        """Get new hits."""
        url = urllib.parse.urljoin(self.BASE_URL, "newhit")
        return await self._parse_tracks(url)

    async def _parse_tracks(
        self, url: str, is_search: bool = False,
    ) -> list[Track]:
        """Parse tracks from the given URL."""
        try:
            async with self._session.get(
                url, timeout=self._config.timeout,
            ) as response:
                response.raise_for_status()
                soup = BeautifulSoup(await response.text(), "html.parser")
                tracks = [
                    Track.from_element(track_data, index, is_search)
                    for index, track_data in enumerate(
                        soup.find_all("item")
                        if is_search
                        else soup.find_all("li", class_="sarki-liste"),
                    )
                ]

            logger.info("Found %d tracks", len(tracks))
            return tracks

        except (aiohttp.ClientError, TimeoutError) as e:
            raise MusicServiceError(f"Failed to search music: {e!s}") from e

    async def _download_data(
        self, url: str, resource_type: str, track_name: str,
    ) -> bytes:
        """Generic method for downloading data."""
        MAX_SIZE = 50 * 1024 * 1024  # 50MB

        if not self._session:
            await self.connect()

        logger.info("Downloading %s for track: %s", resource_type, track_name)

        try:
            async with self._session.get(
                url, timeout=self._config.timeout,
            ) as response:
                response.raise_for_status()
                content_length = response.content_length

                if content_length and content_length > MAX_SIZE:
                    raise MusicServiceError(
                        f"File too large: {content_length} bytes",
                    )

                return await response.read()
        except Exception as e:
            raise MusicServiceError(
                f"Failed to download {resource_type}: {e!s}",
            ) from e

    async def get_audio_bytes(self, track: Track) -> bytes:
        """Download music file."""
        url = track.audio_url
        if url.startswith("/"):
            url = urllib.parse.urljoin(self.BASE_URL, track.audio_url)
        return await self._download_data(url, "audio", track.name)

    async def get_thumbnail_bytes(self, track: Track) -> bytes:
        """Download thumbnail image."""
        url = track.thumbnail_url
        if url.startswith("/"):
            url = urllib.parse.urljoin(self.BASE_URL, track.thumbnail_url)
        return await self._download_data(url, "thumbnail", track.name)
