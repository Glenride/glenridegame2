"""/profile command handlers."""

from __future__ import annotations

from telegram import Update
from telegram.ext import BaseHandler, CommandHandler, ContextTypes

from bot.constants import PRONOUN_LABELS
from bot.logging_utils import instrument_handler
from bot.state import StateStore

__all__ = ["build_handlers"]


def build_handlers(state_store: StateStore) -> list[BaseHandler]:
    """Return handlers related to the /profile command."""

    @instrument_handler("profile_command")
    async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        user = update.effective_user
        if not chat or not user:
            return

        # Load state from database
        state = state_store.load_user_state(user.id)
        if not state:
            await chat.send_message(
                "You haven't started your story yet! Use /start to begin."
            )
            return

        pronoun_label = PRONOUN_LABELS.get(state.player_pronoun, "Unset pronouns")

        # Format stats
        stats_lines = [
            f"❤️ Love Integrity: {state.stats.love_integrity}",
            f"🔥 Temptation: {state.stats.temptation}",
            f"💼 Career Status: {state.stats.career_status}",
            f"⚡ Night Cycles: {state.stats.energy}",
        ]

        # Build profile message
        parts = [
            f"**Profile: {state.player_name}**",
            f"Pronouns: {pronoun_label}",
        ]

        # Show active title if set
        if state.active_title:
            parts.append(f"Title: 🏷️ {state.active_title}")

        parts.append("")
        parts.append("━━━ Stats ━━━")
        parts.extend(stats_lines)

        # Show chapter progress and score
        parts.append("")
        parts.append("━━━ Progress ━━━")
        parts.append(f"📍 Chapter: {_format_chapter(state.current_chapter_id)}")
        parts.append(f"⭐ Score: {state.total_score} pts")

        # Show premium status
        if state.premium_packs or state.premium_items:
            parts.append("")
            parts.append("━━━ Premium ━━━")
            if state.premium_packs:
                for pack in state.premium_packs:
                    parts.append(f"📦 {_format_product_name(pack)}")
            if state.premium_items:
                for item in state.premium_items:
                    parts.append(f"💎 {_format_product_name(item)}")

        # Show owned titles
        if state.titles:
            parts.append("")
            parts.append("━━━ Titles ━━━")
            for title in state.titles:
                marker = "✓" if title == state.active_title else "○"
                parts.append(f"{marker} {title}")

        await chat.send_message("\n".join(parts), parse_mode="Markdown")

    @instrument_handler("leaderboard_command")
    async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        user = update.effective_user
        if not chat or not user:
            return

        # Get top 10 players
        leaderboard = state_store.get_leaderboard(limit=10)
        
        if not leaderboard:
            await chat.send_message(
                "🏆 **Leaderboard**\n\n"
                "No scores yet! Be the first to make some choices.",
                parse_mode="Markdown"
            )
            return

        # Format leaderboard
        parts = ["🏆 **Neon City Leaderboard**", ""]
        
        rank_emojis = {1: "🥇", 2: "🥈", 3: "🥉"}
        
        for entry in leaderboard:
            rank = entry["rank"]
            emoji = rank_emojis.get(rank, f"{rank}.")
            name = entry["player_name"]
            score = entry["total_score"]
            title = f" [{entry['active_title']}]" if entry["active_title"] else ""
            
            parts.append(f"{emoji} **{name}**{title} — {score} pts")

        # Show current user's rank if not in top 10
        user_in_top = any(e["user_id"] == user.id for e in leaderboard)
        if not user_in_top:
            user_rank = state_store.get_user_rank(user.id)
            user_state = state_store.load_user_state(user.id)
            if user_state and user_rank:
                parts.append("")
                parts.append("━━━━━━━━━━")
                parts.append(f"📍 Your rank: #{user_rank} — {user_state.total_score} pts")

        await chat.send_message("\n".join(parts), parse_mode="Markdown")

    return [
        CommandHandler("profile", profile_command),
        CommandHandler("leaderboard", leaderboard_command),
    ]


def _format_chapter(chapter_id: str) -> str:
    """Format chapter ID for display."""
    chapter_names = {
        "chapter_tutorial": "Tutorial",
        "calvin": "Calvin - Glass Towers",
        "jackson": "Jackson - Low Level, High Voltage",
    }
    return chapter_names.get(chapter_id, chapter_id.replace("_", " ").title())


def _format_product_name(product_id: str) -> str:
    """Format product ID for display."""
    # Import here to avoid circular imports
    from bot.products import get_product
    product = get_product(product_id)
    return product.name if product else product_id
