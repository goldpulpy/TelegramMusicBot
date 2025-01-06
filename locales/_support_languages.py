"""Supported languages."""
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

    def is_supported(self, code: str) -> bool:
        """Check if the language is supported."""
        return any(language.code == code for language in self.languages)


support_languages: LanguageList = LanguageList(
    languages=[
        Language('en', '🇬🇧 English'),
        Language('ru', '🇷🇺 Русский')
    ]
)
