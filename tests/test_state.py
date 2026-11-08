"""Tests covering the persistent state store scaffolding."""

from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

import pytest

from bot.state import (
    CURRENT_SCHEMA_VERSION,
    StateStore,
    StateStoreError,
    UserState,
    UserStats,
)


@pytest.mark.parametrize(
    "url",
    [
        "sqlite+aiosqlite:///:memory:",
        "sqlite:///:memory:",
    ],
)
def test_state_store_supports_memory_urls(url: str) -> None:
    store = StateStore(url)
    store.close()


def test_state_store_initialises_schema(tmp_path) -> None:
    db_path = tmp_path / "state.db"
    url = f"sqlite+aiosqlite:///{db_path}"

    store = StateStore(url)
    store.close()

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_state'")
    assert cursor.fetchone() == ("user_state",)
    cursor.execute("PRAGMA user_version")
    version = cursor.fetchone()[0]
    assert version == CURRENT_SCHEMA_VERSION
    cursor.close()
    connection.close()


def test_state_store_rejects_unknown_scheme() -> None:
    with pytest.raises(StateStoreError):
        StateStore("postgresql://example")


# Task 2.3: State transitions, energy, and persistence tests


def test_load_user_state_returns_none_for_missing_user() -> None:
    store = StateStore("sqlite:///:memory:")
    result = store.load_user_state(999)
    assert result is None
    store.close()


def test_save_and_load_user_state() -> None:
    store = StateStore("sqlite:///:memory:")
    
    state = UserState(
        user_id=123,
        player_name="Alex",
        player_pronoun="they/them",
        current_scene_id="tutorial_001",
        current_chapter_id="chapter_tutorial",
        stats=UserStats(love_integrity=60, temptation=40, career_status=55, energy=80),
        flags={"seen_intro": True, "tutorial_step": 3},
        premium_packs={"starter_pack"},
        daily_login_streak=5,
        analytics_opt_in=True,
    )
    
    store.save_user_state(state)
    loaded = store.load_user_state(123)
    
    assert loaded is not None
    assert loaded.user_id == 123
    assert loaded.player_name == "Alex"
    assert loaded.player_pronoun == "they/them"
    assert loaded.current_scene_id == "tutorial_001"
    assert loaded.current_chapter_id == "chapter_tutorial"
    assert loaded.stats.love_integrity == 60
    assert loaded.stats.temptation == 40
    assert loaded.stats.career_status == 55
    assert loaded.stats.energy == 80
    assert loaded.flags == {"seen_intro": True, "tutorial_step": 3}
    assert loaded.premium_packs == {"starter_pack"}
    assert loaded.daily_login_streak == 5
    assert loaded.analytics_opt_in is True
    
    store.close()


def test_save_user_state_updates_existing() -> None:
    store = StateStore("sqlite:///:memory:")
    
    state = UserState(
        user_id=456,
        player_name="Sam",
        player_pronoun="he/him",
        current_scene_id="scene_01",
        current_chapter_id="chapter_1",
    )
    store.save_user_state(state)
    
    # Update the state
    state.player_name = "Samuel"
    state.stats.love_integrity = 75
    state.current_scene_id = "scene_02"
    state.flags["completed_chapter_1"] = True
    
    store.save_user_state(state)
    loaded = store.load_user_state(456)
    
    assert loaded is not None
    assert loaded.player_name == "Samuel"
    assert loaded.stats.love_integrity == 75
    assert loaded.current_scene_id == "scene_02"
    assert loaded.flags.get("completed_chapter_1") is True
    
    store.close()


def test_update_stats_atomic_applies_deltas() -> None:
    store = StateStore("sqlite:///:memory:")
    
    state = UserState(
        user_id=789,
        player_name="Riley",
        player_pronoun="she/her",
        current_scene_id="scene_test",
        current_chapter_id="chapter_test",
        stats=UserStats(love_integrity=50, temptation=50, career_status=50, energy=100),
    )
    store.save_user_state(state)
    
    # Apply stat changes atomically
    updated_stats = store.update_stats_atomic(
        789, {"love_integrity": 10, "temptation": -5, "energy": -20}
    )
    
    assert updated_stats.love_integrity == 60
    assert updated_stats.temptation == 45
    assert updated_stats.career_status == 50  # unchanged
    assert updated_stats.energy == 80
    
    # Verify persistence
    loaded = store.load_user_state(789)
    assert loaded is not None
    assert loaded.stats.love_integrity == 60
    assert loaded.stats.temptation == 45
    assert loaded.stats.energy == 80
    
    store.close()


def test_update_stats_atomic_enforces_minimum_zero() -> None:
    store = StateStore("sqlite:///:memory:")
    
    state = UserState(
        user_id=111,
        player_name="Jordan",
        player_pronoun="they/them",
        current_scene_id="scene_test",
        current_chapter_id="chapter_test",
        stats=UserStats(love_integrity=10, energy=5),
    )
    store.save_user_state(state)
    
    # Try to reduce stats below zero
    updated_stats = store.update_stats_atomic(111, {"love_integrity": -50, "energy": -100})
    
    # Should clamp at 0
    assert updated_stats.love_integrity == 0
    assert updated_stats.energy == 0
    
    store.close()


def test_update_stats_atomic_fails_for_missing_user() -> None:
    store = StateStore("sqlite:///:memory:")
    
    with pytest.raises(StateStoreError, match="User 999 not found"):
        store.update_stats_atomic(999, {"energy": -10})
    
    store.close()


def test_update_stats_atomic_rejects_unknown_stat() -> None:
    store = StateStore("sqlite:///:memory:")
    
    state = UserState(
        user_id=222,
        player_name="Casey",
        player_pronoun="she/her",
        current_scene_id="scene_test",
        current_chapter_id="chapter_test",
    )
    store.save_user_state(state)
    
    with pytest.raises(ValueError, match="Unknown stat"):
        store.update_stats_atomic(222, {"invalid_stat": 10})
    
    store.close()


def test_energy_regeneration_timestamp_persists() -> None:
    store = StateStore("sqlite:///:memory:")
    
    now = datetime.now(tz=timezone.utc)
    state = UserState(
        user_id=333,
        player_name="Morgan",
        player_pronoun="they/them",
        current_scene_id="scene_test",
        current_chapter_id="chapter_test",
        energy_updated_at=now,
    )
    store.save_user_state(state)
    
    loaded = store.load_user_state(333)
    assert loaded is not None
    # Compare timestamps (allow small margin for serialization)
    assert abs((loaded.energy_updated_at - now).total_seconds()) < 1
    
    store.close()


def test_last_login_timestamp_nullable() -> None:
    store = StateStore("sqlite:///:memory:")
    
    # User with no last login
    state = UserState(
        user_id=444,
        player_name="Quinn",
        player_pronoun="he/him",
        current_scene_id="scene_test",
        current_chapter_id="chapter_test",
        last_login_at=None,
    )
    store.save_user_state(state)
    
    loaded = store.load_user_state(444)
    assert loaded is not None
    assert loaded.last_login_at is None
    
    # Update with login time
    login_time = datetime.now(tz=timezone.utc)
    state.last_login_at = login_time
    store.save_user_state(state)
    
    loaded = store.load_user_state(444)
    assert loaded is not None
    assert loaded.last_login_at is not None
    assert abs((loaded.last_login_at - login_time).total_seconds()) < 1
    
    store.close()


def test_premium_packs_as_set() -> None:
    store = StateStore("sqlite:///:memory:")
    
    state = UserState(
        user_id=555,
        player_name="Taylor",
        player_pronoun="she/her",
        current_scene_id="scene_test",
        current_chapter_id="chapter_test",
        premium_packs={"pack_1", "pack_2", "pack_3"},
    )
    store.save_user_state(state)
    
    loaded = store.load_user_state(555)
    assert loaded is not None
    assert loaded.premium_packs == {"pack_1", "pack_2", "pack_3"}
    
    # Add more packs
    state.premium_packs.add("pack_4")
    store.save_user_state(state)
    
    loaded = store.load_user_state(555)
    assert loaded is not None
    assert "pack_4" in loaded.premium_packs
    assert len(loaded.premium_packs) == 4
    
    store.close()


def test_flags_dictionary_persists() -> None:
    store = StateStore("sqlite:///:memory:")
    
    state = UserState(
        user_id=666,
        player_name="Avery",
        player_pronoun="they/them",
        current_scene_id="scene_test",
        current_chapter_id="chapter_test",
        flags={"flag_a": True, "flag_b": False, "counter": 42, "name": "value"},
    )
    store.save_user_state(state)
    
    loaded = store.load_user_state(666)
    assert loaded is not None
    assert loaded.flags == {"flag_a": True, "flag_b": False, "counter": 42, "name": "value"}
    
    store.close()


def test_daily_login_streak_increments() -> None:
    store = StateStore("sqlite:///:memory:")
    
    state = UserState(
        user_id=777,
        player_name="River",
        player_pronoun="he/him",
        current_scene_id="scene_test",
        current_chapter_id="chapter_test",
        daily_login_streak=0,
    )
    store.save_user_state(state)
    
    # Simulate daily logins
    for day in range(1, 8):
        state.daily_login_streak = day
        state.last_login_at = datetime.now(tz=timezone.utc)
        store.save_user_state(state)
        
        loaded = store.load_user_state(777)
        assert loaded is not None
        assert loaded.daily_login_streak == day
    
    store.close()


def test_add_score_awards_points_for_new_scenes() -> None:
    store = StateStore("sqlite:///:memory:")
    
    state = UserState(
        user_id=888,
        player_name="Skylar",
        player_pronoun="they/them",
        current_scene_id="scene_1",
        current_chapter_id="chapter_test",
    )
    store.save_user_state(state)
    
    # Award points for first scene visit
    new_score = store.add_score(888, 10, "scene_1")
    assert new_score == 10
    
    # Second scene visit
    new_score = store.add_score(888, 10, "scene_2")
    assert new_score == 20
    
    # Revisiting scene_1 should not award points
    new_score = store.add_score(888, 10, "scene_1")
    assert new_score == 20
    
    store.close()


def test_get_leaderboard_returns_top_players() -> None:
    store = StateStore("sqlite:///:memory:")
    
    # Create 3 players with different scores
    for i, (name, score) in enumerate([("Alice", 100), ("Bob", 50), ("Charlie", 75)], start=1):
        state = UserState(
            user_id=i,
            player_name=name,
            player_pronoun="they/them",
            current_scene_id="scene_1",
            current_chapter_id="chapter_test",
            total_score=score,
        )
        store.save_user_state(state)
    
    leaderboard = store.get_leaderboard(limit=10)
    assert len(leaderboard) == 3
    assert leaderboard[0]["player_name"] == "Alice"
    assert leaderboard[0]["rank"] == 1
    assert leaderboard[1]["player_name"] == "Charlie"
    assert leaderboard[1]["rank"] == 2
    assert leaderboard[2]["player_name"] == "Bob"
    assert leaderboard[2]["rank"] == 3
    
    store.close()


def test_get_user_rank_returns_correct_position() -> None:
    store = StateStore("sqlite:///:memory:")
    
    for i, score in enumerate([100, 75, 50, 25], start=1):
        state = UserState(
            user_id=i,
            player_name=f"Player{i}",
            player_pronoun="they/them",
            current_scene_id="scene_1",
            current_chapter_id="chapter_test",
            total_score=score,
        )
        store.save_user_state(state)
    
    # Player with 100 points should be rank 1
    assert store.get_user_rank(1) == 1
    # Player with 50 points should be rank 3
    assert store.get_user_rank(3) == 3
    
    store.close()
