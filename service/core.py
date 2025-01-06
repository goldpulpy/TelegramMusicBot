"""Music service core module for downloading and searching music."""
import logging
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

from .data import Song, ServiceConfig
from .exceptions import MusicServiceError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MusicService:
    """Service for searching and downloading music."""
    BASE_URL = "https://mp3wr.com"
    SONG_DOWNLOAD_URL = "https://cdn.mp3wr.com"
    THUMBNAIL_URL = "https://lh3.googleusercontent.com"

    def __init__(self, config: Optional[ServiceConfig] = None) -> None:
        """Initialize music service with optional configuration."""
        self._config = config or ServiceConfig()
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> 'MusicService':
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
                headers={"User-Agent": self._config.user_agent}
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

        try:
            async with self._session.get(
                url, timeout=self._config.timeout
            ) as response:
                response.raise_for_status()
                soup = BeautifulSoup(await response.text(), "html.parser")
                songs = [
                    Song.from_element(song_data, index)
                    for index, song_data in enumerate(soup.find_all("item"))
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
        url = f"{self.SONG_DOWNLOAD_URL}/?h={song.hash}"
        return await self._download_data(url, "song", song.name)

    async def get_thumbnail_bytes(self, song: Song) -> bytes:
        """Download thumbnail image."""
        url = f"{self.THUMBNAIL_URL}/{song.thumbnail_hash}"
        return await self._download_data(url, "thumbnail", song.name)
