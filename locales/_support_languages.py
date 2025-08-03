"""Supported languages."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Language:
    """Supported language."""

    code: str
    name: str


@dataclass
class LanguageList:
    """Supported languages."""

    languages: list[Language]

    def is_supported(self, code: str | None) -> bool:
        """Check if the language is supported."""
        if code is None:
            return False
        return any(language.code == code for language in self.languages)


support_languages: LanguageList = LanguageList(
    languages=[
        Language("en", "🇬🇧 English"),
        Language("ru", "🇷🇺 Русский"),
    ],
)
