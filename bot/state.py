"""Persistent user state schema and storage helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import sqlite3
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "StateStore",
    "StateStoreError",
    "UserState",
    "UserStats",
]


CURRENT_SCHEMA_VERSION = 4


class StateStoreError(RuntimeError):
    """Raised when storage initialisation or access fails."""


class UserStats(BaseModel):
    """Core numerical stats tracked for each player."""

    love_integrity: int = Field(default=50, ge=0)
    temptation: int = Field(default=50, ge=0)
    career_status: int = Field(default=50, ge=0)
    energy: int = Field(default=100, ge=0)


class UserState(BaseModel):
    """Materialised snapshot of a user's progress in the story."""

    user_id: int
    player_name: str
    player_pronoun: str
    current_scene_id: str
    current_chapter_id: str = "chapter_tutorial"
    stats: UserStats = Field(default_factory=UserStats)
    energy_updated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    flags: dict[str, Any] = Field(default_factory=dict)
    premium_packs: set[str] = Field(default_factory=set)
    premium_items: set[str] = Field(default_factory=set)  # Individual purchased items/scenes
    titles: set[str] = Field(default_factory=set)  # Cosmetic titles owned
    active_title: str | None = None  # Currently displayed title
    total_score: int = 0  # Cumulative points from choices
    scenes_visited: set[str] = Field(default_factory=set)  # Track visited scenes for scoring
    daily_login_streak: int = 0
    last_login_at: datetime | None = None
    analytics_opt_in: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


@dataclass(slots=True)
class _SQLiteConfig:
    path: str
    is_memory: bool


def _resolve_sqlite_config(db_url: str) -> _SQLiteConfig:
    """Translate a supported sqlite URL into a filesystem path."""

    supported_prefixes = (
        "sqlite+aiosqlite:///",
        "sqlite:///",
    )
    if db_url.endswith(":memory:"):
        return _SQLiteConfig(path=":memory:", is_memory=True)

    for prefix in supported_prefixes:
        if db_url.startswith(prefix):
            raw_path = db_url[len(prefix) :]
            break
    else:  # pragma: no cover - guarded by tests
        raise StateStoreError(f"Unsupported DB URL for state store: {db_url}")

    path = Path(raw_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return _SQLiteConfig(path=str(path), is_memory=False)


class StateStore:
    """Lightweight wrapper around sqlite for persisting player progress."""

    def __init__(self, db_url: str) -> None:
        config = _resolve_sqlite_config(db_url)
        try:
            self._connection = sqlite3.connect(
                config.path,
                timeout=30,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
        except sqlite3.Error as exc:  # pragma: no cover - sqlite failure rare
            raise StateStoreError("Unable to open user state database") from exc

        self._connection.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cursor = self._connection.cursor()
        current_version = cursor.execute("PRAGMA user_version").fetchone()[0]
        if current_version == 0:
            self._apply_v1_schema(cursor)
        if current_version < 3:
            self._apply_v3_migration(cursor)
        if current_version < 4:
            self._apply_v4_migration(cursor)
        if current_version > CURRENT_SCHEMA_VERSION:
            raise StateStoreError(
                "Database schema is newer than the application knows how to handle"
            )
        cursor.close()

    def _apply_v1_schema(self, cursor: sqlite3.Cursor) -> None:
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS user_state (
                user_id INTEGER PRIMARY KEY,
                player_name TEXT NOT NULL,
                player_pronoun TEXT NOT NULL,
                current_scene_id TEXT NOT NULL,
                current_chapter_id TEXT NOT NULL,
                love_integrity INTEGER NOT NULL DEFAULT 50,
                temptation INTEGER NOT NULL DEFAULT 50,
                career_status INTEGER NOT NULL DEFAULT 50,
                energy INTEGER NOT NULL DEFAULT 100,
                energy_updated_at TEXT NOT NULL,
                flags_json TEXT NOT NULL,
                premium_packs_json TEXT NOT NULL,
                premium_items_json TEXT NOT NULL DEFAULT '[]',
                titles_json TEXT NOT NULL DEFAULT '[]',
                active_title TEXT,
                daily_login_streak INTEGER NOT NULL DEFAULT 0,
                last_login_at TEXT,
                analytics_opt_in INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_user_state_chapter
            ON user_state(current_chapter_id);
            """
        )
        cursor.execute(f"PRAGMA user_version = {CURRENT_SCHEMA_VERSION}")
        self._connection.commit()

    def _apply_v3_migration(self, cursor: sqlite3.Cursor) -> None:
        """Add premium_items, titles, and active_title columns."""
        # Check if columns already exist
        existing_cols = {
            row[1] for row in cursor.execute("PRAGMA table_info(user_state)").fetchall()
        }
        
        if "premium_items_json" not in existing_cols:
            cursor.execute(
                "ALTER TABLE user_state ADD COLUMN premium_items_json TEXT NOT NULL DEFAULT '[]'"
            )
        if "titles_json" not in existing_cols:
            cursor.execute(
                "ALTER TABLE user_state ADD COLUMN titles_json TEXT NOT NULL DEFAULT '[]'"
            )
        if "active_title" not in existing_cols:
            cursor.execute(
                "ALTER TABLE user_state ADD COLUMN active_title TEXT"
            )
        
        cursor.execute(f"PRAGMA user_version = {CURRENT_SCHEMA_VERSION}")
        self._connection.commit()

    def _apply_v4_migration(self, cursor: sqlite3.Cursor) -> None:
        """Add total_score and scenes_visited columns for leaderboard."""
        existing_cols = {
            row[1] for row in cursor.execute("PRAGMA table_info(user_state)").fetchall()
        }
        
        if "total_score" not in existing_cols:
            cursor.execute(
                "ALTER TABLE user_state ADD COLUMN total_score INTEGER NOT NULL DEFAULT 0"
            )
        if "scenes_visited_json" not in existing_cols:
            cursor.execute(
                "ALTER TABLE user_state ADD COLUMN scenes_visited_json TEXT NOT NULL DEFAULT '[]'"
            )
        
        # Create index for leaderboard queries
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_state_score ON user_state(total_score DESC)"
        )
        
        cursor.execute(f"PRAGMA user_version = {CURRENT_SCHEMA_VERSION}")
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    def load_user_state(self, user_id: int) -> UserState | None:
        """Load user state from database, or None if not found."""
        cursor = self._connection.cursor()
        try:
            row = cursor.execute(
                "SELECT * FROM user_state WHERE user_id = ?", (user_id,)
            ).fetchone()
            if row is None:
                return None

            return UserState(
                user_id=row["user_id"],
                player_name=row["player_name"],
                player_pronoun=row["player_pronoun"],
                current_scene_id=row["current_scene_id"],
                current_chapter_id=row["current_chapter_id"],
                stats=UserStats(
                    love_integrity=row["love_integrity"],
                    temptation=row["temptation"],
                    career_status=row["career_status"],
                    energy=row["energy"],
                ),
                energy_updated_at=datetime.fromisoformat(row["energy_updated_at"]),
                flags=_json_loads(row["flags_json"]),
                premium_packs=set(_json_loads(row["premium_packs_json"])),
                premium_items=set(_json_loads(row["premium_items_json"] or "[]")),
                titles=set(_json_loads(row["titles_json"] or "[]")),
                active_title=row["active_title"],
                total_score=row["total_score"] if "total_score" in row.keys() else 0,
                scenes_visited=set(_json_loads(row["scenes_visited_json"] or "[]") if "scenes_visited_json" in row.keys() else []),
                daily_login_streak=row["daily_login_streak"],
                last_login_at=(
                    datetime.fromisoformat(row["last_login_at"])
                    if row["last_login_at"]
                    else None
                ),
                analytics_opt_in=bool(row["analytics_opt_in"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
        finally:
            cursor.close()

    def save_user_state(self, state: UserState) -> None:
        """Insert or update user state with optimistic concurrency control."""
        # Update timestamp on every save
        state.updated_at = datetime.now(tz=timezone.utc)

        cursor = self._connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO user_state (
                    user_id, player_name, player_pronoun,
                    current_scene_id, current_chapter_id,
                    love_integrity, temptation, career_status, energy,
                    energy_updated_at, flags_json, premium_packs_json,
                    premium_items_json, titles_json, active_title,
                    total_score, scenes_visited_json,
                    daily_login_streak, last_login_at, analytics_opt_in,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    player_name = excluded.player_name,
                    player_pronoun = excluded.player_pronoun,
                    current_scene_id = excluded.current_scene_id,
                    current_chapter_id = excluded.current_chapter_id,
                    love_integrity = excluded.love_integrity,
                    temptation = excluded.temptation,
                    career_status = excluded.career_status,
                    energy = excluded.energy,
                    energy_updated_at = excluded.energy_updated_at,
                    flags_json = excluded.flags_json,
                    premium_packs_json = excluded.premium_packs_json,
                    premium_items_json = excluded.premium_items_json,
                    titles_json = excluded.titles_json,
                    active_title = excluded.active_title,
                    total_score = excluded.total_score,
                    scenes_visited_json = excluded.scenes_visited_json,
                    daily_login_streak = excluded.daily_login_streak,
                    last_login_at = excluded.last_login_at,
                    analytics_opt_in = excluded.analytics_opt_in,
                    updated_at = excluded.updated_at
                """,
                (
                    state.user_id,
                    state.player_name,
                    state.player_pronoun,
                    state.current_scene_id,
                    state.current_chapter_id,
                    state.stats.love_integrity,
                    state.stats.temptation,
                    state.stats.career_status,
                    state.stats.energy,
                    state.energy_updated_at.isoformat(),
                    _json_dumps(state.flags),
                    _json_dumps(list(state.premium_packs)),
                    _json_dumps(list(state.premium_items)),
                    _json_dumps(list(state.titles)),
                    state.active_title,
                    state.total_score,
                    _json_dumps(list(state.scenes_visited)),
                    state.daily_login_streak,
                    state.last_login_at.isoformat() if state.last_login_at else None,
                    int(state.analytics_opt_in),
                    state.created_at.isoformat(),
                    state.updated_at.isoformat(),
                ),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            self._connection.rollback()
            raise StateStoreError("Failed to save user state") from exc
        finally:
            cursor.close()

    def update_stats_atomic(
        self, user_id: int, stat_deltas: dict[str, int]
    ) -> UserStats:
        """
        Atomically update specific stats for a user and return new values.
        
        Args:
            user_id: User to update
            stat_deltas: Dict of stat names to delta values (e.g., {"love_integrity": 5, "energy": -10})
            
        Returns:
            Updated UserStats object
            
        Raises:
            StateStoreError: If user not found or update fails
        """
        cursor = self._connection.cursor()
        try:
            # Build dynamic UPDATE statement for only the stats being changed
            updates = []
            params = []
            for stat_name, delta in stat_deltas.items():
                if stat_name not in ("love_integrity", "temptation", "career_status", "energy"):
                    raise ValueError(f"Unknown stat: {stat_name}")
                updates.append(f"{stat_name} = MAX(0, {stat_name} + ?)")
                params.append(delta)
            
            if not updates:
                # No stats to update, just return current stats
                state = self.load_user_state(user_id)
                if state is None:
                    raise StateStoreError(f"User {user_id} not found")
                return state.stats
            
            # Add user_id to params and update timestamp
            params.append(datetime.now(tz=timezone.utc).isoformat())
            params.append(user_id)
            
            cursor.execute(
                f"""
                UPDATE user_state
                SET {', '.join(updates)}, updated_at = ?
                WHERE user_id = ?
                """,
                params,
            )
            
            if cursor.rowcount == 0:
                raise StateStoreError(f"User {user_id} not found")
            
            # Fetch updated stats
            row = cursor.execute(
                """
                SELECT love_integrity, temptation, career_status, energy
                FROM user_state WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
            
            self._connection.commit()
            
            return UserStats(
                love_integrity=row["love_integrity"],
                temptation=row["temptation"],
                career_status=row["career_status"],
                energy=row["energy"],
            )
        except sqlite3.Error as exc:
            self._connection.rollback()
            raise StateStoreError("Failed to update stats atomically") from exc
        finally:
            cursor.close()

    def add_score(self, user_id: int, points: int, scene_id: str) -> int:
        """
        Add points to a user's total score (only if scene not already visited).
        
        Args:
            user_id: User to update
            points: Points to add
            scene_id: Scene that awarded these points
            
        Returns:
            New total score
        """
        cursor = self._connection.cursor()
        try:
            # Get current scenes_visited
            row = cursor.execute(
                "SELECT total_score, scenes_visited_json FROM user_state WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            
            if row is None:
                raise StateStoreError(f"User {user_id} not found")
            
            scenes_visited = set(_json_loads(row["scenes_visited_json"] or "[]"))
            
            # Only award points for first-time scene visits
            if scene_id in scenes_visited:
                return row["total_score"]
            
            scenes_visited.add(scene_id)
            new_score = row["total_score"] + points
            
            cursor.execute(
                """
                UPDATE user_state
                SET total_score = ?, scenes_visited_json = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (
                    new_score,
                    _json_dumps(list(scenes_visited)),
                    datetime.now(tz=timezone.utc).isoformat(),
                    user_id,
                ),
            )
            self._connection.commit()
            return new_score
        except sqlite3.Error as exc:
            self._connection.rollback()
            raise StateStoreError("Failed to add score") from exc
        finally:
            cursor.close()

    def get_leaderboard(self, limit: int = 10) -> list[dict]:
        """
        Get top players by score.
        
        Args:
            limit: Maximum number of players to return
            
        Returns:
            List of dicts with user_id, player_name, total_score, rank
        """
        cursor = self._connection.cursor()
        try:
            rows = cursor.execute(
                """
                SELECT user_id, player_name, total_score, active_title
                FROM user_state
                WHERE total_score > 0
                ORDER BY total_score DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            
            return [
                {
                    "rank": idx + 1,
                    "user_id": row["user_id"],
                    "player_name": row["player_name"],
                    "total_score": row["total_score"],
                    "active_title": row["active_title"],
                }
                for idx, row in enumerate(rows)
            ]
        finally:
            cursor.close()

    def get_user_rank(self, user_id: int) -> int | None:
        """Get a user's rank on the leaderboard, or None if not ranked."""
        cursor = self._connection.cursor()
        try:
            row = cursor.execute(
                """
                SELECT COUNT(*) + 1 as rank
                FROM user_state
                WHERE total_score > (
                    SELECT COALESCE(total_score, 0) FROM user_state WHERE user_id = ?
                )
                """,
                (user_id,),
            ).fetchone()
            return row["rank"] if row else None
        finally:
            cursor.close()


def _json_dumps(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def _json_loads(raw: str) -> Any:
    return json.loads(raw) if raw else {}
