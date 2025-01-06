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

    index: int
    name: str
    title: str
    performer: str
    hash: str
    thumbnail_hash: str

    @classmethod
    def from_element(cls, element: BeautifulSoup, index: int) -> "Song":
        """Create Song from BeautifulSoup element"""
        full_name = element.find(class_="artist_name").text.strip()
        performer, title = full_name.split(" - ", 1)
        hash = element.find(class_="right").get("data-id").split("?h=")[-1]
        thumbnail = element.find(class_="little_thumb")
        thumbnail_hash = thumbnail.find("img").get("data-src").split("/")[-1]
        return cls(
            index=index,
            name=full_name,
            title=title,
            performer=performer,
            hash=hash,
            thumbnail_hash=thumbnail_hash,
        )
