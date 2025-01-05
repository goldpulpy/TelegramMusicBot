"""Data classes"""
from dataclasses import dataclass
from bs4 import BeautifulSoup


@dataclass
class ServiceConfig:
    """Configuration for music service."""
    timeout: int = 30
    user_agent: str = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )


@dataclass
class Song:
    """Song data class"""

    name: str
    hash: str

    @classmethod
    def from_element(cls, element: BeautifulSoup) -> "Song":
        """Create Song from BeautifulSoup element"""
        name = element.find(class_="artist_name").text.strip()
        hash = element.find(class_="right").get("data-id").split("?h=")[-1]
        return cls(name=name, hash=hash)
