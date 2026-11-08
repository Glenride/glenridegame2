"""/start command handlers and onboarding flow."""

from __future__ import annotations

from collections.abc import Iterable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    BaseHandler,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bot.constants import PRONOUN_CALLBACK_PREFIX, PRONOUN_CHOICES
from bot.logging_utils import instrument_handler
from bot.onboarding import OnboardingSanitizer, OnboardingValidationError
from bot.scenes import SceneLoader
from bot.state import StateStore, UserState, UserStats

__all__ = ["build_handlers"]

ASK_NAME, ASK_PRONOUN = range(2)
FIRST_SCENE_ID = "chapter_tutorial_intro"


def build_handlers(
    sanitizer: OnboardingSanitizer,
    state_store: StateStore,
    scene_loader: SceneLoader,
) -> list[BaseHandler[Update, ConversationHandler.END]]:
    """Return handlers for the /start onboarding flow."""

    @instrument_handler("start_command")
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.effective_user or not update.effective_chat:
            return ConversationHandler.END

        # Check if user already exists - offer to continue or restart
        existing_state = state_store.load_user_state(update.effective_user.id)
        if existing_state:
            # Verify their current scene exists
            try:
                scene_loader.get_scene(existing_state.current_scene_id)
                scene_valid = True
            except Exception:
                scene_valid = False

            if scene_valid:
                await update.effective_chat.send_message(
                    f"Welcome back, {existing_state.player_name}! ⭐️\n\n"
                    "Continuing your story..."
                )
                # Show their current scene
                from bot.handlers.scene import show_scene
                await show_scene(
                    update.effective_chat.id,
                    existing_state.current_scene_id,
                    existing_state,
                    scene_loader,
                    context,
                )
            else:
                # Scene doesn't exist - offer restart
                await update.effective_chat.send_message(
                    f"Welcome back, {existing_state.player_name}! ⭐️\n\n"
                    "⚠️ Your current scene is no longer available (content may have changed).\n\n"
                    "Use /restart to begin a new story, keeping your name and pronouns."
                )
            return ConversationHandler.END

        await update.effective_chat.send_message(
            "Welcome to Glenride ⭐️\n"
            "Tell me the name you'd like to use in Neon Nights."
        )
        return ASK_NAME

    @instrument_handler("collect_name")
    async def collect_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message:
            return ASK_NAME

        try:
            sanitized = sanitizer.sanitize_name(update.message.text or "")
        except OnboardingValidationError as exc:
            await update.message.reply_text(f"⚠️ {exc}")
            return ASK_NAME

        context.user_data["player_name"] = sanitized
        await update.message.reply_text(
            "Nice to meet you, {name}!\nChoose your pronouns.".format(name=sanitized),
            reply_markup=_build_pronoun_keyboard(),
        )
        return ASK_PRONOUN

    @instrument_handler("collect_pronoun")
    async def collect_pronoun(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.callback_query or not update.effective_user:
            return ASK_PRONOUN

        await update.callback_query.answer()
        data = update.callback_query.data or ""
        code = data.removeprefix(PRONOUN_CALLBACK_PREFIX)

        try:
            pronoun_label = sanitizer.validate_pronoun(code)
        except OnboardingValidationError as exc:
            await update.callback_query.edit_message_text(f"⚠️ {exc}")
            return ConversationHandler.END

        context.user_data["player_pronoun"] = code
        name = context.user_data.get("player_name", "Mystery Player")

        # Create and save user state
        user_state = UserState(
            user_id=update.effective_user.id,
            player_name=name,
            player_pronoun=code,
            current_scene_id=FIRST_SCENE_ID,
            current_chapter_id="chapter_tutorial",
        )
        state_store.save_user_state(user_state)

        await update.callback_query.edit_message_text(
            f"You're all set, {name} ({pronoun_label})!\n\n"
            "Your adventure in Neon City begins now..."
        )

        # Show the first scene
        from bot.handlers.scene import show_scene
        await show_scene(
            update.effective_chat.id,
            FIRST_SCENE_ID,
            user_state,
            scene_loader,
            context,
        )
        return ConversationHandler.END

    @instrument_handler("cancel_onboarding")
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.effective_chat.send_message("Onboarding canceled. Use /start to try again.")
        return ConversationHandler.END

    @instrument_handler("restart_command")
    async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Reset user's story progress while keeping their profile."""
        if not update.effective_user or not update.effective_chat:
            return

        existing_state = state_store.load_user_state(update.effective_user.id)
        if not existing_state:
            await update.effective_chat.send_message(
                "You haven't started a story yet! Use /start to begin."
            )
            return

        # Reset to first scene, keep name/pronouns/premium purchases
        existing_state.current_scene_id = FIRST_SCENE_ID
        existing_state.current_chapter_id = "chapter_tutorial"
        existing_state.stats = UserStats()  # Reset stats to defaults
        existing_state.flags = {}  # Clear story flags
        existing_state.scenes_visited = set()  # Clear visited scenes
        existing_state.total_score = 0  # Reset score
        state_store.save_user_state(existing_state)

        await update.effective_chat.send_message(
            f"🔄 Story reset, {existing_state.player_name}!\n\n"
            "Your premium purchases are preserved. Starting fresh..."
        )

        # Show first scene
        from bot.handlers.scene import show_scene
        await show_scene(
            update.effective_chat.id,
            FIRST_SCENE_ID,
            existing_state,
            scene_loader,
            context,
        )

    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_name)],
            ASK_PRONOUN: [CallbackQueryHandler(collect_pronoun, pattern=f"^{PRONOUN_CALLBACK_PREFIX}.*")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="onboarding",
        persistent=False,
    )

    return [conversation, CommandHandler("restart", restart_command)]


def _build_pronoun_keyboard() -> InlineKeyboardMarkup:
    buttons: Iterable[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text=label,
                callback_data=f"{PRONOUN_CALLBACK_PREFIX}{value}",
            )
        ]
        for value, label in PRONOUN_CHOICES
    ]
    return InlineKeyboardMarkup(buttons)
