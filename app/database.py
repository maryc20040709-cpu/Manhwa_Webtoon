import sqlite3
import os

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
    conn.commit()
    conn.close()


def save_analysis(title: str, characters: str, panels_found: int, total_scenes: int, recap: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO analyses (title, characters, panels_found, total_scenes, recap) VALUES (?, ?, ?, ?, ?)",
        (title, characters, panels_found, total_scenes, recap)
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 10):
    init_db()  # ensure table exists
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
