"""Utilities to sanitize and validate onboarding inputs."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Iterable

from bot.constants import PRONOUN_LABELS

__all__ = ["OnboardingSanitizer", "OnboardingValidationError"]


class OnboardingValidationError(ValueError):
    """Raised when onboarding data fails validation."""


class OnboardingSanitizer:
    """Sanitize player-provided names and pronoun selections."""

    MIN_LENGTH = 2
    MAX_LENGTH = 20
    _MARKDOWN_PATTERN = re.compile(r"[*_`~>\[\]()|]")
    _HTML_TAG_PATTERN = re.compile(r"<[^>]+>")

    def __init__(self, banned_words_path: str) -> None:
        self._banned_words = tuple(self._load_banned_words(Path(banned_words_path)))

    @staticmethod
    def _load_banned_words(path: Path) -> Iterable[str]:
        if not path.exists():
            return ()
        with path.open("r", encoding="utf-8") as handle:
            return tuple(
                line.strip().lower()
                for line in handle
                if line.strip() and not line.startswith("#")
            )

    def sanitize_name(self, raw_name: str | None) -> str:
        """Strip markup, enforce length, and block banned words."""

        if not raw_name:
            raise OnboardingValidationError("Name is required")

        decoded = html.unescape(raw_name)
        without_tags = self._HTML_TAG_PATTERN.sub("", decoded)
        no_markup = self._MARKDOWN_PATTERN.sub("", without_tags)
        collapsed = re.sub(r"\s+", " ", no_markup).strip()

        if not (self.MIN_LENGTH <= len(collapsed) <= self.MAX_LENGTH):
            raise OnboardingValidationError(
                f"Name must be {self.MIN_LENGTH}-{self.MAX_LENGTH} characters"
            )

        lowered = collapsed.casefold()
        for banned in self._banned_words:
            if banned and banned in lowered:
                raise OnboardingValidationError("Name contains blocked language")

        return collapsed

    def validate_pronoun(self, pronoun_code: str | None) -> str:
        """Ensure pronoun selection is from the approved list."""

        if pronoun_code is None:
            raise OnboardingValidationError("Pronoun selection is required")

        try:
            return PRONOUN_LABELS[pronoun_code]
        except KeyError as exc:
            raise OnboardingValidationError("Invalid pronoun selection") from exc

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"OnboardingSanitizer(banned_words={len(self._banned_words)})"
