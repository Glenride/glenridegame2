# Shared pytest fixtures.

from __future__ import annotations

import pytest

from bot.onboarding import OnboardingSanitizer
from bot.scenes import SceneLoader
from bot.state import StateStore


@pytest.fixture
def sanitizer(tmp_path) -> OnboardingSanitizer:
    """Provide a sanitizer wired to a temporary banned-words list."""

    banned_file = tmp_path / "banned.txt"
    banned_file.write_text("slur\n", encoding="utf-8")
    return OnboardingSanitizer(str(banned_file))


@pytest.fixture
def state_store() -> StateStore:
    """Provide an in-memory state store for testing."""
    return StateStore("sqlite:///:memory:")


@pytest.fixture
def scene_loader(tmp_path) -> SceneLoader:
    """Provide a scene loader with test scene files."""
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir()
    return SceneLoader(str(scenes_dir))
