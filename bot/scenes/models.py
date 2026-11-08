"""Pydantic models for scene data with localization support."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class StatEffect(BaseModel):
    """Stat modification applied when a choice is selected."""

    love_integrity: int = 0
    temptation: int = 0
    career_status: int = 0
    energy: int = 0

    def to_delta_dict(self) -> dict[str, int]:
        """Return non-zero deltas as a dict for atomic update."""
        return {
            k: v
            for k, v in {
                "love_integrity": self.love_integrity,
                "temptation": self.temptation,
                "career_status": self.career_status,
                "energy": self.energy,
            }.items()
            if v != 0
        }


class SceneCondition(BaseModel):
    """Condition that must be met for a choice to be available."""

    stat: Literal["love_integrity", "temptation", "career_status", "energy"] | None = None
    min_value: int | None = None
    max_value: int | None = None
    flag: str | None = None
    flag_value: Any = True
    premium_pack: str | None = None
    premium_item: str | None = None  # For single premium scene/item purchases


class LocalizedText(BaseModel):
    """Text content with locale support."""

    en: str
    # Future locales can be added here
    # es: str | None = None
    # fr: str | None = None

    def get(self, locale: str = "en") -> str:
        """Get text for specified locale, falling back to English."""
        return getattr(self, locale, None) or self.en


class Choice(BaseModel):
    """A single choice option within a scene."""

    id: str
    text: LocalizedText
    next_scene_id: str
    effects: StatEffect = Field(default_factory=StatEffect)
    condition: SceneCondition | None = None
    unavailable_text: LocalizedText | None = None
    emoji: str | None = None
    is_premium: bool = False
    set_flags: dict[str, Any] = Field(default_factory=dict)  # Flags set when choice is selected

    def format_button_text(self, locale: str = "en") -> str:
        """Format the choice text for display on an inline button."""
        text = self.text.get(locale)
        if self.emoji:
            text = f"{self.emoji} {text}"
        if self.is_premium:
            text = f"💎 {text}"
        return text


class Scene(BaseModel):
    """A single story scene with narrative and choices."""

    id: str
    chapter_id: str
    narrative: LocalizedText
    choices: list[Choice] = Field(default_factory=list)
    is_checkpoint: bool = False
    auto_advance_to: str | None = None
    set_flags: dict[str, Any] = Field(default_factory=dict)
    stat_effects: StatEffect = Field(default_factory=StatEffect)

    def is_terminal(self) -> bool:
        """Return True if this scene has no choices (end of branch)."""
        return len(self.choices) == 0 and self.auto_advance_to is None
