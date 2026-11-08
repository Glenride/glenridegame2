"""Handlers for launching the web app."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import CommandHandler, ContextTypes


async def webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a button to launch the mini app."""
    # Replace with your actual deployed URL or a tunneling URL (e.g. ngrok)
    web_app_url = "https://ste-suspension-calibration-cigarettes.trycloudflare.com" 
    
    await update.message.reply_text(
        "Launch the Glenride Mini App:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "Open App",
                web_app=WebAppInfo(url=web_app_url)
            )]
        ])
    )


def build_handlers() -> list:
    return [CommandHandler("app", webapp_command)]
