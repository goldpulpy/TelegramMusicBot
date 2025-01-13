"""Music service core module for downloading and searching music."""
import logging
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

from .data import Song, ServiceConfig
from .exceptions import MusicServiceError

logger = logging.getLogger(__name__)


class Music:
    """Service for searching and downloading music."""
    BASE_URL = "https://mp3wr.com"
    SONG_DOWNLOAD_URL = "https://cdn.mp3wr.com"

    def __init__(self, config: Optional[ServiceConfig] = None) -> None:
        """Initialize music service with optional configuration."""
        self._config = config or ServiceConfig()
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> 'Music':
        """Context manager entry point."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit point."""
        await self.disconnect()

    async def connect(self) -> None:
        """Initialize HTTP session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                headers=self._config.headers
            )

    async def disconnect(self) -> None:
        """Close HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def get_songs_list(self, keyword: str) -> list[Song]:
        """Search for music by keyword."""
        if not self._session:
            await self.connect()

        url = f"{self.BASE_URL}/search/{keyword}"
        logger.info("Searching music with keyword: %s", keyword)

        return await self._parse_songs(url, is_search=True)

    async def get_top_songs(self) -> list[Song]:
        """Get top songs."""
        url = f"{self.BASE_URL}/besthit"
        return await self._parse_songs(url)

    async def get_novelties(self) -> list[Song]:
        """Get novelties."""
        url = f"{self.BASE_URL}/newhit"
        return await self._parse_songs(url)

    async def _parse_songs(
        self, url: str, is_search: bool = False
    ) -> list[Song]:
        """Parse songs from the given URL."""
        try:
            async with self._session.get(
                url, timeout=self._config.timeout
            ) as response:
                response.raise_for_status()
                soup = BeautifulSoup(await response.text(), "html.parser")
                songs = [
                    Song.from_element(song_data, index, is_search)
                    for index, song_data in enumerate(
                        soup.find_all("item") if is_search
                        else soup.find_all("li", class_="sarki-liste")
                    )
                ]

            logger.info("Found %d songs", len(songs))
            return songs

        except (aiohttp.ClientError, TimeoutError) as e:
            raise MusicServiceError(f"Failed to search music: {str(e)}") from e

    async def _download_data(
        self, url: str, resource_type: str, song_name: str
    ) -> bytes:
        """Generic method for downloading data."""
        if not self._session:
            await self.connect()

        logger.info("Downloading %s for song: %s", resource_type, song_name)

        try:
            async with self._session.get(
                url,
                timeout=self._config.timeout
            ) as response:
                response.raise_for_status()
                return await response.read()

        except (aiohttp.ClientError, TimeoutError) as e:
            raise MusicServiceError(
                f"Failed to download {resource_type}: {str(e)}") from e

    async def get_song_bytes(self, song: Song) -> bytes:
        """Download music file."""
        url = song.audio_url
        if url.startswith("/"):
            url = f"{self.BASE_URL}{song.audio_url}"
        return await self._download_data(url, "song", song.name)

    async def get_thumbnail_bytes(self, song: Song) -> bytes:
        """Download thumbnail image."""
        url = song.thumbnail_url
        if url.startswith("/"):
            url = f"{self.BASE_URL}{song.thumbnail_url}"
        return await self._download_data(url, "thumbnail", song.name)
