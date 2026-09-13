"""Data classes."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bs4 import BeautifulSoup, Tag

headers_path = Path(__file__).parent / "headers.json"


@dataclass
class ServiceConfig:
    """Configuration for music service."""

    timeout: int = 30
    headers: dict = field(
        default_factory=lambda: json.load(
            Path.open(headers_path, encoding="utf-8"),
        ),
    )


@dataclass
class Track:
    """Track data class."""

    index: int
    name: str
    title: str
    performer: str
    audio_url: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Track:
        """Create Track from a dictionary."""
        return cls(
            index=int(data["index"]),
            name=data["name"],
            title=data["title"],
            performer=data["performer"],
            audio_url=data["audio_url"],
        )

    @classmethod
    def from_element(
        cls,
        element: BeautifulSoup | Tag,
        index: int,
    ) -> Track:
        """Create Track from BeautifulSoup element."""
        artist_name_element = element.find(class_="track__artist")
        track_name_element = element.find(class_="track__title")
        if artist_name_element is None or track_name_element is None:
            msg = "Could not find artist name element"
            raise ValueError(msg)

        performer = artist_name_element.text.strip()
        title = track_name_element.text.strip()

        full_name = f"{performer} - {title}"

        audio_url = element.get("data-mp3")
        if not isinstance(audio_url, str):
            msg = "Could not find audio URL element"
            raise TypeError(msg)

        return cls(
            index=index,
            name=full_name,
            title=title,
            performer=performer,
            audio_url=audio_url,
        )
