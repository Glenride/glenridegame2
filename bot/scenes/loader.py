"""Scene file loader for JSON-based story content."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .models import Scene

logger = logging.getLogger(__name__)

__all__ = ["SceneLoader", "SceneNotFoundError"]


class SceneNotFoundError(Exception):
    """Raised when a requested scene cannot be found."""

    def __init__(self, scene_id: str) -> None:
        self.scene_id = scene_id
        super().__init__(f"Scene not found: {scene_id}")


class SceneLoader:
    """Loads and caches scene data from JSON files."""

    def __init__(self, scenes_dir: str | Path) -> None:
        self._scenes_dir = Path(scenes_dir)
        self._cache: dict[str, Scene] = {}
        self._loaded_files: set[str] = set()

    def load_chapter(self, chapter_id: str) -> list[Scene]:
        """Load all scenes for a chapter from its JSON file."""
        filepath = self._scenes_dir / f"{chapter_id}.json"
        if not filepath.exists():
            logger.warning("chapter_file_not_found", extra={"chapter_id": chapter_id, "path": str(filepath)})
            return []

        file_key = str(filepath)
        if file_key in self._loaded_files:
            return [s for s in self._cache.values() if s.chapter_id == chapter_id]

        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error("chapter_json_invalid", extra={"chapter_id": chapter_id, "error": str(e)})
            return []

        scenes = self._parse_chapter_data(data, chapter_id)
        self._loaded_files.add(file_key)
        return scenes

    def _parse_chapter_data(self, data: dict[str, Any], chapter_id: str) -> list[Scene]:
        """Parse chapter JSON data into Scene objects."""
        scenes: list[Scene] = []
        raw_scenes = data.get("scenes", [])

        for raw_scene in raw_scenes:
            try:
                raw_scene["chapter_id"] = chapter_id
                scene = Scene.model_validate(raw_scene)
                self._cache[scene.id] = scene
                scenes.append(scene)
            except Exception as e:
                logger.error(
                    "scene_parse_error",
                    extra={"chapter_id": chapter_id, "scene_data": raw_scene, "error": str(e)},
                )

        logger.info("chapter_loaded", extra={"chapter_id": chapter_id, "scene_count": len(scenes)})
        return scenes

    def get_scene(self, scene_id: str) -> Scene:
        """Get a scene by ID, loading its chapter if needed."""
        if scene_id in self._cache:
            return self._cache[scene_id]

        # Try to infer chapter from scene_id prefix
        # Handles patterns like: chapter_tutorial_intro -> chapter_tutorial
        #                        tutorial_jackson_preview -> chapter_tutorial (fallback)
        #                        calvin_gala -> calvin
        parts = scene_id.split("_")
        if len(parts) >= 2:
            # Try direct prefix first (e.g., chapter_tutorial)
            chapter_id = f"{parts[0]}_{parts[1]}"
            self.load_chapter(chapter_id)

        if scene_id in self._cache:
            return self._cache[scene_id]

        # Fallback: try first part only (e.g., calvin)
        if parts:
            self.load_chapter(parts[0])

        if scene_id in self._cache:
            return self._cache[scene_id]

        # Last resort: preload all and check again
        self.preload_all()

        if scene_id in self._cache:
            return self._cache[scene_id]

        raise SceneNotFoundError(scene_id)

    def get_first_scene(self, chapter_id: str) -> Scene:
        """Get the first scene of a chapter."""
        scenes = self.load_chapter(chapter_id)
        if not scenes:
            raise SceneNotFoundError(f"{chapter_id}_intro")
        return scenes[0]

    def preload_all(self) -> int:
        """Preload all scene files in the scenes directory."""
        count = 0
        if not self._scenes_dir.exists():
            return count

        for filepath in self._scenes_dir.glob("*.json"):
            chapter_id = filepath.stem
            scenes = self.load_chapter(chapter_id)
            count += len(scenes)

        return count

    def clear_cache(self) -> None:
        """Clear the scene cache (useful for hot reloading in dev)."""
        self._cache.clear()
        self._loaded_files.clear()
