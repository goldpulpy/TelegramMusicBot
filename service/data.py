"""Data classes"""
from dataclasses import dataclass
from bs4 import BeautifulSoup


@dataclass
class ServiceConfig:
    """Configuration for music service."""
    base_url: str = "https://mp3wr.com"
    timeout: int = 30
    user_agent: str = "Mozilla/5.0"


@dataclass
class Song:
    """Song data class"""

    name: str
    download_url: str

    @classmethod
    def from_element(cls, element: BeautifulSoup) -> "Song":
        """Create Song from BeautifulSoup element"""
        name = element.find(class_="artist_name").text.strip()
        download_url = element.find(class_="right").get("data-id")
        return cls(name=name, download_url=download_url)
