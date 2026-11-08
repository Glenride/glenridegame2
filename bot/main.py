"""Bot entrypoint for Glenride Telegram romance simulation."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from telegram.ext import Application

from bot.config import AppConfig, load_config
from bot.handlers import register_handlers
from bot.onboarding import OnboardingSanitizer
from bot.scenes import SceneLoader
from bot.state import StateStore

__all__ = ["build_application", "run"]


class _AppEnvFilter(logging.Filter):
    def __init__(self, app_env: str) -> None:
        super().__init__()
        self._app_env = app_env

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - simple data inject
        record.app_env = self._app_env
        return True


@dataclass(slots=True)
class BotRuntime:
    config: AppConfig
    sanitizer: OnboardingSanitizer
    state_store: StateStore
    scene_loader: SceneLoader
    application: Application


def configure_logging(app_env: str, log_level: str) -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)
    env_filter = _AppEnvFilter(app_env)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s app_env=%(app_env)s",
    )
    root_logger = logging.getLogger()
    root_logger.addFilter(env_filter)
    for handler in root_logger.handlers:
        handler.addFilter(env_filter)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def build_runtime() -> BotRuntime:
    config = load_config()
    configure_logging(config.app_env, config.log_level)
    sanitizer = OnboardingSanitizer(config.banned_words_path)
    state_store = StateStore(config.db_url)
    scene_loader = SceneLoader(config.scenes_dir)

    # Preload scenes in production for faster responses
    if config.app_env == "prod":
        scene_count = scene_loader.preload_all()
        logging.getLogger(__name__).info("scenes_preloaded", extra={"count": scene_count})

    application = Application.builder().token(config.bot_token).build()
    register_handlers(application, sanitizer, state_store, scene_loader)
    return BotRuntime(
        config=config,
        sanitizer=sanitizer,
        state_store=state_store,
        scene_loader=scene_loader,
        application=application,
    )


def build_application() -> Application:
    return build_runtime().application


def run() -> None:
    runtime = build_runtime()
    logger = logging.getLogger("bot.main")
    logger.info(
        "starting_bot",
        extra={"app_env": runtime.config.app_env},
    )
    runtime.application.run_polling()


if __name__ == "__main__":
    run()
