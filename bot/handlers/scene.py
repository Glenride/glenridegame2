"""Scene callback handler for story progression."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import BaseHandler, CallbackQueryHandler, ContextTypes

from bot.logging_utils import instrument_handler
from bot.scenes import SceneLoader, SceneNotFoundError, SceneRenderer
from bot.scenes.renderer import SCENE_CALLBACK_PREFIX
from bot.state import StateStore, UserState

__all__ = ["build_handlers", "show_scene"]

logger = logging.getLogger(__name__)


def build_handlers(
    state_store: StateStore, scene_loader: SceneLoader
) -> list[BaseHandler]:
    """Return handlers for scene callbacks."""
    renderer = SceneRenderer()

    @instrument_handler("scene_choice")
    async def handle_scene_choice(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle a choice selection callback."""
        if not update.callback_query:
            return

        query = update.callback_query
        await query.answer()

        data = (query.data or "").removeprefix(SCENE_CALLBACK_PREFIX)

        # Handle unavailable choice clicks
        if data.startswith("unavailable:"):
            reason = data.removeprefix("unavailable:")
            await query.answer(
                _get_unavailable_message(reason), show_alert=True
            )
            return

        # Parse scene_id:choice_id
        parts = data.split(":")
        if len(parts) != 2:
            logger.warning("invalid_callback_data", extra={"data": query.data})
            return

        scene_id, choice_id = parts
        user_id = query.from_user.id

        # Load current state
        state = state_store.load_user_state(user_id)
        if state is None:
            await query.edit_message_text(
                "⚠️ Session not found. Use /start to begin."
            )
            return

        # Load scene and find choice
        try:
            scene = scene_loader.get_scene(scene_id)
        except SceneNotFoundError:
            logger.error("scene_not_found", extra={"scene_id": scene_id})
            await query.answer("Scene not found. Please /start again.", show_alert=True)
            return

        choice = next((c for c in scene.choices if c.id == choice_id), None)
        if choice is None:
            logger.error("choice_not_found", extra={"scene_id": scene_id, "choice_id": choice_id})
            return

        # Apply stat effects
        deltas = choice.effects.to_delta_dict()
        if deltas:
            new_stats = state_store.update_stats_atomic(user_id, deltas)
            state.stats = new_stats

        # Apply choice-level flags
        if choice.set_flags:
            state.flags.update(choice.set_flags)

        # Update scene and save
        state.current_scene_id = choice.next_scene_id
        state_store.save_user_state(state)

        # Load and show next scene
        try:
            next_scene = scene_loader.get_scene(choice.next_scene_id)
        except SceneNotFoundError:
            logger.error("next_scene_not_found", extra={"next_scene_id": choice.next_scene_id})
            await query.edit_message_text(
                "🚧 Content coming soon! Check back later."
            )
            return

        # Award points for visiting a new scene (10 points per scene)
        POINTS_PER_SCENE = 10
        new_score = state_store.add_score(user_id, POINTS_PER_SCENE, choice.next_scene_id)
        state.total_score = new_score
        state.scenes_visited.add(choice.next_scene_id)

        # Apply any scene-level stat effects
        scene_deltas = next_scene.stat_effects.to_delta_dict()
        if scene_deltas:
            new_stats = state_store.update_stats_atomic(user_id, scene_deltas)
            state.stats = new_stats

        # Set any flags from the scene
        if next_scene.set_flags:
            state.flags.update(next_scene.set_flags)
            state_store.save_user_state(state)

        # Update chapter if changed
        if next_scene.chapter_id != state.current_chapter_id:
            state.current_chapter_id = next_scene.chapter_id
            state_store.save_user_state(state)

        # Render and send
        message, keyboard = _format_scene_with_stats(next_scene, state, renderer, choice.effects)
        await query.edit_message_text(message, reply_markup=keyboard)

        # Handle auto-advance if no choices
        if next_scene.auto_advance_to:
            state.current_scene_id = next_scene.auto_advance_to
            state_store.save_user_state(state)

    pattern = f"^{SCENE_CALLBACK_PREFIX}"
    return [CallbackQueryHandler(handle_scene_choice, pattern=pattern)]


async def show_scene(
    chat_id: int,
    scene_id: str,
    state: UserState,
    scene_loader: SceneLoader,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Send a scene message to start the story."""
    renderer = SceneRenderer()

    try:
        scene = scene_loader.get_scene(scene_id)
    except SceneNotFoundError:
        await context.bot.send_message(chat_id, "🚧 Scene not found. Please try /start again.")
        return

    message = renderer.render_narrative(scene, state)

    # Show initial stats
    stats_line = renderer.render_stats_hud(state.stats)
    message = f"{message}\n\n{stats_line}"

    keyboard = renderer.render_keyboard(scene, state)
    await context.bot.send_message(chat_id, message, reply_markup=keyboard)


def _format_scene_with_stats(
    scene, state: UserState, renderer: SceneRenderer, effects=None
) -> tuple[str, ...]:
    """Format scene with stat changes shown."""
    parts = [renderer.render_narrative(scene, state)]

    if effects and effects.to_delta_dict():
        parts.append("")
        parts.append(renderer.render_stats_hud(state.stats, effects))
    else:
        parts.append("")
        parts.append(renderer.render_stats_hud(state.stats))

    message = "\n".join(parts)
    keyboard = renderer.render_keyboard(scene, state)
    return message, keyboard


def _get_unavailable_message(reason: str) -> str:
    """Get user-friendly message for unavailable choice reasons."""
    if reason.startswith("need_premium_"):
        pack_id = reason.removeprefix("need_premium_")
        from bot.products import get_product
        product = get_product(pack_id)
        name = product.name if product else "a premium pack"
        return f"💎 This requires {name}. Check /store for options!"
    if reason.startswith("need_item_"):
        item_id = reason.removeprefix("need_item_")
        from bot.products import get_product
        product = get_product(item_id)
        name = product.name if product else "a premium item"
        return f"💎 This is a premium choice. Unlock '{name}' to continue."
    if reason.startswith("need_flag_"):
        return "🔒 This option requires completing specific story events first."
    if reason.startswith("need_"):
        parts = reason.split("_")
        if len(parts) >= 3:
            stat = parts[1]
            value = parts[2]
            stat_emoji = {
                "love": "❤️",
                "temptation": "🔥",
                "career": "💼",
                "energy": "⚡",
            }
            emoji = stat_emoji.get(stat.split("_")[0], "📊")
            return f"{emoji} Requires {stat.replace('_', ' ')} of at least {value}"
    return "This option is not available right now."
