"""Tests for the scene engine: models, loader, and renderer."""

from __future__ import annotations

import json

import pytest

from bot.scenes import SceneLoader, SceneNotFoundError, SceneRenderer
from bot.scenes.models import Choice, LocalizedText, Scene, SceneCondition, StatEffect
from bot.state import UserState, UserStats


# --- Model Tests ---

def test_stat_effect_to_delta_dict_excludes_zeros():
    effect = StatEffect(love_integrity=5, temptation=0, career_status=-3, energy=0)
    deltas = effect.to_delta_dict()
    
    assert deltas == {"love_integrity": 5, "career_status": -3}
    assert "temptation" not in deltas
    assert "energy" not in deltas


def test_localized_text_fallback_to_english():
    text = LocalizedText(en="Hello World")
    
    assert text.get("en") == "Hello World"
    assert text.get("es") == "Hello World"  # Falls back to en


def test_choice_format_button_text_with_emoji():
    choice = Choice(
        id="test",
        text=LocalizedText(en="Go forward"),
        next_scene_id="next",
        emoji="🚀"
    )
    
    assert choice.format_button_text() == "🚀 Go forward"


def test_choice_format_button_text_premium():
    choice = Choice(
        id="test",
        text=LocalizedText(en="Secret path"),
        next_scene_id="next",
        is_premium=True
    )
    
    assert "💎" in choice.format_button_text()


def test_scene_is_terminal_with_no_choices():
    scene = Scene(
        id="end_scene",
        chapter_id="chapter_1",
        narrative=LocalizedText(en="The end."),
        choices=[]
    )
    
    assert scene.is_terminal() is True


def test_scene_is_not_terminal_with_choices():
    scene = Scene(
        id="mid_scene",
        chapter_id="chapter_1",
        narrative=LocalizedText(en="Choose wisely."),
        choices=[
            Choice(id="c1", text=LocalizedText(en="Option 1"), next_scene_id="next")
        ]
    )
    
    assert scene.is_terminal() is False


def test_scene_is_not_terminal_with_auto_advance():
    scene = Scene(
        id="transition",
        chapter_id="chapter_1",
        narrative=LocalizedText(en="Loading..."),
        choices=[],
        auto_advance_to="next_scene"
    )
    
    assert scene.is_terminal() is False


# --- Loader Tests ---

def test_scene_loader_loads_chapter_from_json(tmp_path):
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir()
    
    chapter_data = {
        "scenes": [
            {
                "id": "test_chapter_scene1",
                "narrative": {"en": "First scene"},
                "choices": [
                    {"id": "c1", "text": {"en": "Continue"}, "next_scene_id": "test_chapter_scene2"}
                ]
            },
            {
                "id": "test_chapter_scene2",
                "narrative": {"en": "Second scene"},
                "choices": []
            }
        ]
    }
    
    chapter_file = scenes_dir / "test_chapter.json"
    chapter_file.write_text(json.dumps(chapter_data), encoding="utf-8")
    
    loader = SceneLoader(str(scenes_dir))
    scenes = loader.load_chapter("test_chapter")
    
    assert len(scenes) == 2
    assert scenes[0].id == "test_chapter_scene1"
    assert scenes[1].id == "test_chapter_scene2"


def test_scene_loader_get_scene_by_id(tmp_path):
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir()
    
    chapter_data = {
        "scenes": [
            {"id": "chapter_test_intro", "narrative": {"en": "Welcome!"}, "choices": []}
        ]
    }
    
    chapter_file = scenes_dir / "chapter_test.json"
    chapter_file.write_text(json.dumps(chapter_data), encoding="utf-8")
    
    loader = SceneLoader(str(scenes_dir))
    scene = loader.get_scene("chapter_test_intro")
    
    assert scene.id == "chapter_test_intro"
    assert scene.narrative.en == "Welcome!"


def test_scene_loader_raises_for_missing_scene(tmp_path):
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir()
    
    loader = SceneLoader(str(scenes_dir))
    
    with pytest.raises(SceneNotFoundError) as exc_info:
        loader.get_scene("nonexistent_scene")
    
    assert "nonexistent_scene" in str(exc_info.value)


def test_scene_loader_caches_scenes(tmp_path):
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir()
    
    chapter_data = {
        "scenes": [
            {"id": "chapter_cache_test", "narrative": {"en": "Cached"}, "choices": []}
        ]
    }
    
    chapter_file = scenes_dir / "chapter_cache.json"
    chapter_file.write_text(json.dumps(chapter_data), encoding="utf-8")
    
    loader = SceneLoader(str(scenes_dir))
    scene1 = loader.get_scene("chapter_cache_test")
    scene2 = loader.get_scene("chapter_cache_test")
    
    assert scene1 is scene2  # Same object from cache


def test_scene_loader_clear_cache(tmp_path):
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir()
    
    chapter_data = {
        "scenes": [
            {"id": "chapter_clear_test", "narrative": {"en": "Test"}, "choices": []}
        ]
    }
    
    chapter_file = scenes_dir / "chapter_clear.json"
    chapter_file.write_text(json.dumps(chapter_data), encoding="utf-8")
    
    loader = SceneLoader(str(scenes_dir))
    loader.get_scene("chapter_clear_test")
    loader.clear_cache()
    
    # Should reload from file after cache clear
    scene = loader.get_scene("chapter_clear_test")
    assert scene.id == "chapter_clear_test"


# --- Renderer Tests ---

@pytest.fixture
def sample_user_state():
    return UserState(
        user_id=123,
        player_name="Nova",
        player_pronoun="she_her",
        current_scene_id="test_scene",
        stats=UserStats(love_integrity=60, temptation=40, career_status=50, energy=80)
    )


def test_renderer_substitutes_player_name(sample_user_state):
    scene = Scene(
        id="test",
        chapter_id="chapter_1",
        narrative=LocalizedText(en="Hello, {player_name}!"),
        choices=[]
    )
    
    renderer = SceneRenderer()
    result = renderer.render_narrative(scene, sample_user_state)
    
    assert "Hello, Nova!" in result


def test_renderer_substitutes_pronouns(sample_user_state):
    scene = Scene(
        id="test",
        chapter_id="chapter_1",
        narrative=LocalizedText(
            en="{pronoun_subject} walked in. Everyone looked at {pronoun_object}."
        ),
        choices=[]
    )
    
    renderer = SceneRenderer()
    result = renderer.render_narrative(scene, sample_user_state)
    
    assert "she walked in" in result.lower()
    assert "looked at her" in result.lower()


def test_renderer_stats_hud_shows_all_stats(sample_user_state):
    renderer = SceneRenderer()
    hud = renderer.render_stats_hud(sample_user_state.stats)
    
    assert "60" in hud  # love_integrity
    assert "40" in hud  # temptation
    assert "50" in hud  # career_status
    assert "80" in hud  # energy
    assert "❤️" in hud
    assert "🔥" in hud
    assert "💼" in hud
    assert "⚡" in hud


def test_renderer_stats_hud_shows_deltas():
    stats = UserStats(love_integrity=60, temptation=40, career_status=50, energy=80)
    deltas = StatEffect(love_integrity=5, temptation=-3)
    
    renderer = SceneRenderer()
    hud = renderer.render_stats_hud(stats, deltas)
    
    assert "+5" in hud
    assert "-3" in hud


def test_renderer_builds_keyboard_for_choices(sample_user_state):
    scene = Scene(
        id="test",
        chapter_id="chapter_1",
        narrative=LocalizedText(en="Choose:"),
        choices=[
            Choice(id="a", text=LocalizedText(en="Option A"), next_scene_id="next_a"),
            Choice(id="b", text=LocalizedText(en="Option B"), next_scene_id="next_b"),
        ]
    )
    
    renderer = SceneRenderer()
    keyboard = renderer.render_keyboard(scene, sample_user_state)
    
    assert keyboard is not None
    assert len(keyboard.inline_keyboard) == 2
    assert "Option A" in keyboard.inline_keyboard[0][0].text
    assert "Option B" in keyboard.inline_keyboard[1][0].text


def test_renderer_hides_unavailable_choices_without_fallback_text(sample_user_state):
    sample_user_state.stats.love_integrity = 30  # Below requirement
    
    scene = Scene(
        id="test",
        chapter_id="chapter_1",
        narrative=LocalizedText(en="Choose:"),
        choices=[
            Choice(
                id="locked",
                text=LocalizedText(en="High integrity option"),
                next_scene_id="next",
                condition=SceneCondition(stat="love_integrity", min_value=50)
                # No unavailable_text, so it should be hidden
            ),
            Choice(id="open", text=LocalizedText(en="Open option"), next_scene_id="next2"),
        ]
    )
    
    renderer = SceneRenderer()
    keyboard = renderer.render_keyboard(scene, sample_user_state)
    
    assert keyboard is not None
    assert len(keyboard.inline_keyboard) == 1
    assert "Open option" in keyboard.inline_keyboard[0][0].text


def test_renderer_shows_unavailable_text_when_provided(sample_user_state):
    sample_user_state.stats.love_integrity = 30
    
    scene = Scene(
        id="test",
        chapter_id="chapter_1",
        narrative=LocalizedText(en="Choose:"),
        choices=[
            Choice(
                id="locked",
                text=LocalizedText(en="High integrity option"),
                next_scene_id="next",
                condition=SceneCondition(stat="love_integrity", min_value=50),
                unavailable_text=LocalizedText(en="Requires more integrity")
            ),
        ]
    )
    
    renderer = SceneRenderer()
    keyboard = renderer.render_keyboard(scene, sample_user_state)
    
    assert keyboard is not None
    assert len(keyboard.inline_keyboard) == 1
    assert "🚫" in keyboard.inline_keyboard[0][0].text


def test_renderer_checks_premium_condition(sample_user_state):
    scene = Scene(
        id="test",
        chapter_id="chapter_1",
        narrative=LocalizedText(en="Choose:"),
        choices=[
            Choice(
                id="premium",
                text=LocalizedText(en="Premium content"),
                next_scene_id="next",
                condition=SceneCondition(premium_pack="vip_pack"),
                unavailable_text=LocalizedText(en="Requires VIP")
            ),
        ]
    )
    
    # Without premium pack
    renderer = SceneRenderer()
    keyboard = renderer.render_keyboard(scene, sample_user_state)
    assert "🚫" in keyboard.inline_keyboard[0][0].text
    
    # With premium pack
    sample_user_state.premium_packs.add("vip_pack")
    keyboard = renderer.render_keyboard(scene, sample_user_state)
    assert "Premium content" in keyboard.inline_keyboard[0][0].text


def test_renderer_checks_flag_condition(sample_user_state):
    scene = Scene(
        id="test",
        chapter_id="chapter_1",
        narrative=LocalizedText(en="Choose:"),
        choices=[
            Choice(
                id="flag_choice",
                text=LocalizedText(en="Secret option"),
                next_scene_id="next",
                condition=SceneCondition(flag="met_alex", flag_value=True),
                unavailable_text=LocalizedText(en="You haven't met Alex yet")
            ),
        ]
    )
    
    # Without flag
    renderer = SceneRenderer()
    keyboard = renderer.render_keyboard(scene, sample_user_state)
    assert "🚫" in keyboard.inline_keyboard[0][0].text
    
    # With flag set
    sample_user_state.flags["met_alex"] = True
    keyboard = renderer.render_keyboard(scene, sample_user_state)
    assert "Secret option" in keyboard.inline_keyboard[0][0].text
