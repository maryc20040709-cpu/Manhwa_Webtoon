import os
import uuid
import sqlite3

# ── Optional Postgres backend (Neon, Supabase, etc.) ────────────────────────
# Render's free tier wipes the local filesystem on every deploy AND every
# spin-down/wake cycle, so SQLite history never actually persists there.
# Setting a DATABASE_URL env var switches to a real external Postgres
# database. Without it, everything falls back to the original local SQLite
# file — this keeps local dev and CI working with zero setup.
DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "history.db")


def _get_conn():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = _get_conn()
    try:
        if USE_POSTGRES:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    characters TEXT,
                    panels_found INTEGER,
                    total_scenes INTEGER,
                    recap TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    result_id TEXT,
                    genre TEXT
                )
            """)
            conn.commit()
            cur.close()
        else:
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
    finally:
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
    conn = _get_conn()
    try:
        if USE_POSTGRES:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO analyses
                   (title, characters, panels_found, total_scenes, recap, result_id, genre)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (title, characters, panels_found, total_scenes, recap, result_id, genre),
            )
            conn.commit()
            cur.close()
        else:
            conn.execute(
                """INSERT INTO analyses
                   (title, characters, panels_found, total_scenes, recap, result_id, genre)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (title, characters, panels_found, total_scenes, recap, result_id, genre),
            )
            conn.commit()
    finally:
        conn.close()
    return result_id


def get_analysis_by_id(result_id: str):
    """Retrieve a single analysis by its short result_id."""
    init_db()
    conn = _get_conn()
    try:
        if USE_POSTGRES:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM analyses WHERE result_id = %s", (result_id,))
            row = cur.fetchone()
            cur.close()
            return dict(row) if row else None
        else:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM analyses WHERE result_id = ?", (result_id,)
            ).fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_history(limit: int = 10):
    init_db()
    conn = _get_conn()
    try:
        if USE_POSTGRES:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                "SELECT * FROM analyses ORDER BY created_at DESC LIMIT %s", (limit,)
            )
            rows = cur.fetchall()
            cur.close()
            return [dict(row) for row in rows]
        else:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(row) for row in rows]
    finally:
        conn.close()


def get_total_count() -> int:
    init_db()
    conn = _get_conn()
    try:
        if USE_POSTGRES:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM analyses")
            count = cur.fetchone()[0]
            cur.close()
            return count
        else:
            count = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
            return count
    finally:
        conn.close()
