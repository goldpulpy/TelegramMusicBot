"""Data classes"""
import json
import os
from dataclasses import dataclass, field
from bs4 import BeautifulSoup

headers_path = os.path.join(os.path.dirname(__file__), "headers.json")


@dataclass
class ServiceConfig:
    """Configuration for music service."""
    timeout: int = 30
    headers: dict = field(
        default_factory=lambda: json.load(open(headers_path))
    )


@dataclass
class Track:
    """Track data class"""

    index: int
    name: str
    title: str
    performer: str
    audio_url: str
    thumbnail_url: str

    @classmethod
    def from_element(
        cls,
        element: BeautifulSoup,
        index: int,
        is_search: bool = False,
    ) -> "Track":
        """Create Track from BeautifulSoup element"""
        full_name = element.find(class_="artist_name").text.strip()
        performer, title = full_name.split(" - ", 1)
        audio_url = element.find(class_="right").get("data-id")
        thumbnail_element = element.find(
            class_="little_thumb" if is_search else "resim_thumb"
        )
        thumbnail_url = thumbnail_element.find("img").get("data-src")
        return cls(
            index=index,
            name=full_name,
            title=title,
            performer=performer,
            audio_url=audio_url,
            thumbnail_url=thumbnail_url,
        )
