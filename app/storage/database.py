"""Database management for Bionic AI"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from app.config import DATABASE_PATH


class Database:
    """SQLite database manager"""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    conversation_id INTEGER,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY,
                    action TEXT,
                    tool_name TEXT,
                    command TEXT,
                    approved BOOLEAN,
                    result TEXT,
                    timestamp TIMESTAMP
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS permissions (
                    id INTEGER PRIMARY KEY,
                    tool_name TEXT,
                    permission_level TEXT,
                    granted BOOLEAN,
                    timestamp TIMESTAMP
                )
            """
            )
            conn.commit()

    def create_conversation(self, title: str) -> int:
        """Create a new conversation"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO conversations (title, created_at, updated_at) VALUES (?, ?, ?)",
                (title, now, now),
            )
            conn.commit()
            return cursor.lastrowid

    def add_message(
        self, conversation_id: int, role: str, content: str
    ) -> int:
        """Add message to conversation"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, now),
            )
            conn.commit()
            return cursor.lastrowid

    def get_conversation_history(self, conversation_id: int) -> list[dict]:
        """Get all messages in a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp",
                (conversation_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def log_action(
        self,
        action: str,
        tool_name: str,
        command: str,
        approved: bool,
        result: str = "",
    ):
        """Log an action in audit log"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO audit_log (action, tool_name, command, approved, result, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (action, tool_name, command, approved, result, now),
            )
            conn.commit()

    def get_audit_log(self, limit: int = 100) -> list[dict]:
        """Get recent audit logs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]
