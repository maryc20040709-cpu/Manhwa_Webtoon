import sqlite3
import os
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "history.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            characters TEXT,
            panels_found INTEGER,
            total_scenes INTEGER,
            recap TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migrate: add new columns if they don't exist yet
    for col, definition in [
        ("result_id", "TEXT"),
        ("genre",     "TEXT"),
    ]:
        try:
            conn.execute(f"ALTER TABLE analyses ADD COLUMN {col} {definition}")
        except Exception:
            pass  # column already exists — safe to ignore
    conn.commit()
    conn.close()


def save_analysis(
    title: str,
    characters: str,
    panels_found: int,
    total_scenes: int,
    recap: str,
    genre: str = None,
) -> str:
    """Save an analysis and return its short result_id."""
    init_db()
    result_id = uuid.uuid4().hex[:8]  # e.g. "a3f8c12e"
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO analyses
           (title, characters, panels_found, total_scenes, recap, result_id, genre)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (title, characters, panels_found, total_scenes, recap, result_id, genre),
    )
    conn.commit()
    conn.close()
    return result_id


def get_analysis_by_id(result_id: str):
    """Retrieve a single analysis by its short result_id."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM analyses WHERE result_id = ?", (result_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_history(limit: int = 10):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_total_count() -> int:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
    conn.close()
    return count
