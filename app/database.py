import sqlite3
from pathlib import Path

from app.models import (
    CREATE_ACCESS_TOKENS_TABLE_SQL,
    CREATE_TODO_ITEMS_TABLE_SQL,
    CREATE_USERS_TABLE_SQL,
    INSERT_TEMPORARY_USER_SQL,
)

DATABASE_PATH = Path(__file__).resolve().parent.parent / "todo_api.db"

def get_connection(): # establishes connection so our code and db (SQLite) can talk to each other
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _create_todo_items_table(connection):
    connection.execute(CREATE_TODO_ITEMS_TABLE_SQL)


def _todo_items_table_exists(connection):
    row = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = 'todo_items'
        """
    ).fetchone()

    return row is not None


def _todo_items_table_has_user_fk(connection):
    foreign_keys = connection.execute("PRAGMA foreign_key_list(todo_items)").fetchall()
    return any(row["table"] == "users" for row in foreign_keys)


def _migrate_todo_items_table(connection):
    connection.execute("ALTER TABLE todo_items RENAME TO old_todo_items")
    _create_todo_items_table(connection)
    connection.execute(
        """
        INSERT INTO todo_items (
            id,
            title,
            description,
            completed,
            user_id,
            created_at,
            updated_at
        )
        SELECT
            id,
            title,
            description,
            completed,
            user_id,
            created_at,
            updated_at
        FROM old_todo_items
        """
    )
    connection.execute("DROP TABLE old_todo_items")


def init_db(): # creates the database tables if they do not already exist
    with get_connection() as connection:
        connection.execute(CREATE_USERS_TABLE_SQL)
        connection.execute(INSERT_TEMPORARY_USER_SQL)
        connection.execute(CREATE_ACCESS_TOKENS_TABLE_SQL)

        if _todo_items_table_exists(connection):
            if not _todo_items_table_has_user_fk(connection):
                _migrate_todo_items_table(connection)
        else:
            _create_todo_items_table(connection)

        connection.commit()
