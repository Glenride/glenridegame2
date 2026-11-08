"""Handler registration helpers."""

from __future__ import annotations

from telegram.ext import Application

from bot.onboarding import OnboardingSanitizer
from bot.scenes import SceneLoader
from bot.state import StateStore

from . import profile, scene, start, store, webapp


def register_handlers(
    application: Application,
    sanitizer: OnboardingSanitizer,
    state_store: StateStore,
    scene_loader: SceneLoader,
) -> None:
    """Register command and message handlers with the Telegram application."""

    for handler in start.build_handlers(sanitizer, state_store, scene_loader):
        application.add_handler(handler)

    for handler in profile.build_handlers(state_store):
        application.add_handler(handler)

    for handler in scene.build_handlers(state_store, scene_loader):
        application.add_handler(handler)

    for handler in store.build_handlers(state_store):
        application.add_handler(handler)

    for handler in webapp.build_handlers():
        application.add_handler(handler)


__all__ = ["register_handlers"]
