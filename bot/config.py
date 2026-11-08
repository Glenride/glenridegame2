"""Application configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_ENV_FILE_LOADED = False


def _ensure_env_file_loaded() -> None:
    global _ENV_FILE_LOADED
    if _ENV_FILE_LOADED:
        return

    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        with env_path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export ") :].strip()
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                cleaned = value.strip().strip('"').strip("'")
                os.environ.setdefault(key.strip(), cleaned)

    _ENV_FILE_LOADED = True


@dataclass(frozen=True)
class AppConfig:
    """Top-level runtime configuration."""

    bot_token: str
    app_env: str
    log_level: str
    banned_words_path: str
    scenes_dir: str
    db_url: str
    payments_provider_token: str


def _env(name: str, default: str | None = None) -> str:
    try:
        value = os.environ[name]
    except KeyError:
        if default is None:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return default
    return value.strip()


def _env_for_env(name: str, app_env: str, default: str | None = None) -> str:
    """Return environment-specific variable (e.g., NAME_DEV) falling back to NAME."""

    scoped_name = f"{name}_{app_env.upper()}"
    try:
        return _env(scoped_name)
    except RuntimeError:
        return _env(name, default)


@lru_cache(maxsize=1)
def load_config() -> AppConfig:
    """Load configuration with caching so downstream modules can import safely."""

    _ensure_env_file_loaded()
    app_env = _env("APP_ENV", "dev").lower()
    repo_root = Path(__file__).resolve().parent.parent
    default_banned_words_path = repo_root / "config" / "banned_words.txt"
    raw_banned_words_path = os.environ.get("BANNED_WORDS_PATH", "").strip()
    banned_words_path = raw_banned_words_path or str(default_banned_words_path)
    db_default = f"sqlite+aiosqlite:///./glenride_{app_env}.db"
    default_scenes_dir = repo_root / "content" / "scenes"
    scenes_dir = os.environ.get("SCENES_DIR", "").strip() or str(default_scenes_dir)
    return AppConfig(
        bot_token=_env_for_env("BOT_TOKEN", app_env),
        app_env=app_env,
        log_level=_env("LOG_LEVEL", "INFO"),
        banned_words_path=banned_words_path,
        scenes_dir=scenes_dir,
        db_url=_env_for_env("DB_URL", app_env, db_default),
        payments_provider_token=_env_for_env("PAYMENTS_PROVIDER_TOKEN", app_env, ""),
    )


__all__ = ["AppConfig", "load_config"]
