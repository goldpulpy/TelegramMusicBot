"""Music service core module for downloading and searching music."""
import logging
from io import BytesIO
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
    DOWNLOAD_URL = "https://cdn.mp3wr.com"

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

    async def get_music_list(self, keyword: str) -> list[Song]:
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
                    Song.from_element(song_data)
                    for song_data in soup.find_all(class_="song_datas")
                ]

            logger.info("Found %d songs", len(songs))
            return songs

        except (aiohttp.ClientError, TimeoutError) as e:
            raise MusicServiceError(f"Failed to search music: {str(e)}") from e

    async def download_music(self, song: Song) -> BytesIO:
        """Download music file."""
        if not self._session:
            await self.connect()

        logger.info("Downloading song: %s", song.name)

        try:
            async with self._session.get(
                f"{self.DOWNLOAD_URL}/?h={song.hash}",
                timeout=self._config.timeout
            ) as response:
                response.raise_for_status()
                file = BytesIO(await response.read())
                file.name = f"{song.name}.mp3"
                return file

        except (aiohttp.ClientError, TimeoutError) as e:
            raise MusicServiceError(
                f"Failed to download music: {str(e)}") from e
