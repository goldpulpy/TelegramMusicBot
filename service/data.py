"""Data classes."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag

headers_path = Path(__file__).parent / "headers.json"


@dataclass
class ServiceConfig:
    """Configuration for music service."""

    timeout: int = 30
    headers: dict = field(
        default_factory=lambda: json.load(Path.open(headers_path)),
    )


@dataclass
class Track:
    """Track data class."""

    index: int
    name: str
    title: str
    performer: str
    audio_url: str
    thumbnail_url: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Track:
        """Create Track from a dictionary."""
        return cls(
            index=int(data["index"]),
            name=data["name"],
            title=data["title"],
            performer=data["performer"],
            audio_url=data["audio_url"],
            thumbnail_url=data["thumbnail_url"],
        )

    @classmethod
    def from_element(
        cls,
        element: BeautifulSoup | Tag,
        index: int,
        *,
        is_search: bool = False,
    ) -> Track:
        """Create Track from BeautifulSoup element."""
        artist_name_element = element.find(class_="artist_name")
        if artist_name_element is None or not hasattr(
            artist_name_element,
            "text",
        ):
            msg = "Could not find artist name element"
            raise TypeError(msg)

        full_name = artist_name_element.text.strip()
        if " - " not in full_name:
            performer, title = "Unknown Artist", full_name
        else:
            performer, title = full_name.split(" - ", 1)

        right_element = element.find(class_="right")
        if not isinstance(right_element, Tag):
            msg = "Could not find audio URL element"
            raise TypeError(msg)
        audio_url = right_element.get("data-id", "")

        class_name = "little_thumb" if is_search else "resim_thumb"
        thumbnail_element = element.find(class_=class_name)
        if not isinstance(thumbnail_element, Tag):
            msg = "Could not find thumbnail element"
            raise TypeError(msg)

        img_element = thumbnail_element.find("img")
        if not isinstance(img_element, Tag):
            msg = "Could not find image element"
            raise TypeError(msg)

        thumbnail_url = img_element.get("data-src", "")

        return cls(
            index=index,
            name=full_name,
            title=title,
            performer=performer,
            audio_url=audio_url,
            thumbnail_url=thumbnail_url,
        )
