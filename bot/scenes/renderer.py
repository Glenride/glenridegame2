"""Scene renderer for Telegram messages with inline keyboards."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.state import UserState, UserStats

from .models import Choice, Scene, SceneCondition, StatEffect

__all__ = ["SceneRenderer", "SCENE_CALLBACK_PREFIX"]

SCENE_CALLBACK_PREFIX = "scene:"


class SceneRenderer:
    """Renders scenes as Telegram messages with inline keyboard choices."""

    def __init__(self, locale: str = "en") -> None:
        self._locale = locale

    def render_narrative(self, scene: Scene, state: UserState) -> str:
        """Render the narrative text with player name substitution."""
        text = scene.narrative.get(self._locale)
        return self._substitute_variables(text, state)

    def render_stats_hud(self, stats: UserStats, deltas: StatEffect | None = None) -> str:
        """Render a compact stats display."""
        lines = []

        if deltas and any(deltas.to_delta_dict().values()):
            # Show deltas inline
            parts = []
            if deltas.love_integrity:
                sign = "+" if deltas.love_integrity > 0 else ""
                parts.append(f"❤️ {sign}{deltas.love_integrity}")
            if deltas.temptation:
                sign = "+" if deltas.temptation > 0 else ""
                parts.append(f"🔥 {sign}{deltas.temptation}")
            if deltas.career_status:
                sign = "+" if deltas.career_status > 0 else ""
                parts.append(f"💼 {sign}{deltas.career_status}")
            if deltas.energy:
                sign = "+" if deltas.energy > 0 else ""
                parts.append(f"⚡ {sign}{deltas.energy}")
            lines.append(" | ".join(parts))

        lines.append(
            f"❤️ {stats.love_integrity} | 🔥 {stats.temptation} | "
            f"💼 {stats.career_status} | ⚡ {stats.energy}"
        )
        return "\n".join(lines)

    def render_keyboard(
        self, scene: Scene, state: UserState
    ) -> InlineKeyboardMarkup | None:
        """Build inline keyboard for scene choices."""
        if not scene.choices:
            return None

        buttons: list[list[InlineKeyboardButton]] = []

        for choice in scene.choices:
            available, reason = self._check_choice_available(choice, state)

            if available:
                btn = InlineKeyboardButton(
                    text=choice.format_button_text(self._locale),
                    callback_data=f"{SCENE_CALLBACK_PREFIX}{scene.id}:{choice.id}",
                )
                buttons.append([btn])
            elif choice.unavailable_text:
                # Show greyed-out unavailable option
                unavail_text = f"🚫 {choice.unavailable_text.get(self._locale)}"
                btn = InlineKeyboardButton(
                    text=unavail_text,
                    callback_data=f"{SCENE_CALLBACK_PREFIX}unavailable:{reason}",
                )
                buttons.append([btn])

        return InlineKeyboardMarkup(buttons) if buttons else None

    def _check_choice_available(
        self, choice: Choice, state: UserState
    ) -> tuple[bool, str]:
        """Check if a choice is available based on conditions."""
        if choice.condition is None:
            return True, ""

        cond = choice.condition
        stats = state.stats

        # Check stat requirements
        if cond.stat:
            stat_value = getattr(stats, cond.stat, 0)
            if cond.min_value is not None and stat_value < cond.min_value:
                return False, f"need_{cond.stat}_{cond.min_value}"
            if cond.max_value is not None and stat_value > cond.max_value:
                return False, f"max_{cond.stat}_{cond.max_value}"

        # Check flag requirements
        if cond.flag:
            actual_value = state.flags.get(cond.flag)
            if actual_value != cond.flag_value:
                return False, f"need_flag_{cond.flag}"

        # Check premium pack
        if cond.premium_pack:
            if cond.premium_pack not in state.premium_packs:
                return False, f"need_premium_{cond.premium_pack}"

        # Check premium item (individual scene/item purchase)
        if cond.premium_item:
            if cond.premium_item not in state.premium_items:
                return False, f"need_item_{cond.premium_item}"

        return True, ""

    def _substitute_variables(self, text: str, state: UserState) -> str:
        """Replace placeholders with player-specific values."""
        replacements = {
            "{player_name}": state.player_name,
            "{pronoun_subject}": self._get_pronoun(state.player_pronoun, "subject"),
            "{pronoun_object}": self._get_pronoun(state.player_pronoun, "object"),
            "{pronoun_possessive}": self._get_pronoun(state.player_pronoun, "possessive"),
        }
        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)
        return text

    def _get_pronoun(self, pronoun_code: str, form: str) -> str:
        """Get the appropriate pronoun form."""
        pronouns = {
            "she_her": {"subject": "she", "object": "her", "possessive": "her"},
            "he_him": {"subject": "he", "object": "him", "possessive": "his"},
            "they_them": {"subject": "they", "object": "them", "possessive": "their"},
        }
        return pronouns.get(pronoun_code, pronouns["they_them"]).get(form, "they")


def format_scene_message(
    scene: Scene, state: UserState, renderer: SceneRenderer, show_stats: bool = True
) -> tuple[str, InlineKeyboardMarkup | None]:
    """Format a complete scene message with narrative and optional stats."""
    parts = [renderer.render_narrative(scene, state)]

    if show_stats and scene.stat_effects.to_delta_dict():
        parts.append("")
        parts.append(renderer.render_stats_hud(state.stats, scene.stat_effects))

    message = "\n".join(parts)
    keyboard = renderer.render_keyboard(scene, state)
    return message, keyboard
