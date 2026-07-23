from dataclasses import dataclass
from datetime import datetime

# 
@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str
    hashed_password: str
    created_at: datetime


CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


CREATE_TODO_ITEMS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS todo_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
    user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
"""


CREATE_ACCESS_TOKENS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS access_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
"""


INSERT_TEMPORARY_USER_SQL = """
INSERT OR IGNORE INTO users (
    id,
    name,
    email,
    hashed_password,
    created_at
)
VALUES (
    1,
    'Temporary User',
    'temporary@example.com',
    'temporary-password-placeholder',
    datetime('now')
)
"""
