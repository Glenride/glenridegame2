"""Static constants for the Glenride bot."""

from __future__ import annotations

from typing import Final, List, Tuple

PronounChoice = Tuple[str, str]

PRONOUN_CHOICES: Final[List[PronounChoice]] = [
    ("she_her", "She / Her"),
    ("he_him", "He / Him"),
    ("they_them", "They / Them"),
]

PRONOUN_CALLBACK_PREFIX: Final[str] = "pronoun:"

PRONOUN_LABELS: Final[dict[str, str]] = {value: label for value, label in PRONOUN_CHOICES}

__all__ = ["PRONOUN_CHOICES", "PRONOUN_LABELS", "PRONOUN_CALLBACK_PREFIX", "PronounChoice"]
