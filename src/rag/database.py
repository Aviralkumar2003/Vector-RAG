import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "data/chat_history.db"):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sources TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            conn.commit()

    def save_session(self, session_id: str, filename: str, filepath: str, status: str):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO sessions (id, filename, filepath, status) VALUES (?, ?, ?, ?)",
                (session_id, filename, filepath, status)
            )
            conn.commit()

    def update_session_status(self, session_id: str, status: str):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE sessions SET status = ? WHERE id = ?",
                (status, session_id)
            )
            conn.commit()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
            return dict(row) if row else None

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    def delete_session(self, session_id: str):
        with self._get_connection() as conn:
            # Delete messages first due to foreign key constraint (though SQLite doesn't always enforce it by default, it's good practice)
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()

    def save_message(self, session_id: str, role: str, content: str, sources: Optional[str] = None):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, sources) VALUES (?, ?, ?, ?)",
                (session_id, role, content, sources)
            )
            conn.commit()

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT role, content, sources, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,)
            ).fetchall()
            return [dict(row) for row in rows]

# Global instance
db_manager = DatabaseManager()
