# i can pretty much reuse this exact shape for future APIs I build

from datetime import UTC, datetime

from app.auth import generate_token, hash_password, verify_password
from app.database import get_connection
from app.models import User
from app.schemas import TodoItemCreate, TodoItemRead, TodoItemUpdate, UserCreate, UserLogin


def _row_to_todo_item(row) -> TodoItemRead:
    return TodoItemRead(**dict(row))


def _row_to_user(row) -> User:
    user_data = dict(row)
    user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
    return User(**user_data)


def get_user(user_id: int) -> User | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, name, email, hashed_password, created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_user(row)


def get_user_by_email(email: str) -> User | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, name, email, hashed_password, created_at
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_user(row)


def create_user(user_data: UserCreate) -> User | None:
    if get_user_by_email(user_data.email) is not None:
        return None

    created_at = datetime.now(UTC).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (
                name,
                email,
                hashed_password,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_data.name,
                user_data.email,
                hash_password(user_data.password),
                created_at,
            ),
        )
        connection.commit()

    return get_user(cursor.lastrowid)


def create_access_token(user_id: int) -> str:
    token = generate_token()
    created_at = datetime.now(UTC).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO access_tokens (
                user_id,
                token,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (user_id, token, created_at),
        )
        connection.commit()

    return token


# Looks up a stored access token and returns the user it belongs to.
def get_user_by_token(token: str) -> User | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT users.id, users.name, users.email, users.hashed_password, users.created_at
            FROM users
            INNER JOIN access_tokens
            ON access_tokens.user_id = users.id
            WHERE access_tokens.token = ?
            """,
            (token,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_user(row)


# Authenticates login details and returns a new token when the credentials are valid.
def login_user(login_data: UserLogin) -> str | None:
    user = get_user_by_email(login_data.email)

    if user is None:
        return None

    if not verify_password(login_data.password, user.hashed_password):
        return None

    return create_access_token(user.id)

# CREATE
def create_todo_item(todo_item_data: TodoItemCreate, user_id: int) -> TodoItemRead:
    now = datetime.now(UTC).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO todo_items (
                title,
                description,
                completed,
                user_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                todo_item_data.title,
                todo_item_data.description,
                0,
                user_id,
                now,
                now,
            ),
        )
        connection.commit()

    return get_todo_item(cursor.lastrowid)

# READ
def get_todo_items(
    user_id: int,
    page: int,
    limit: int,
    completed: bool | None,
) -> tuple[list[TodoItemRead], int]:
    offset = (page - 1) * limit
    where_clauses = ["user_id = ?"]
    query_values: list[int] = [user_id]

    if completed is not None:
        where_clauses.append("completed = ?")
        query_values.append(int(completed))

    where_sql = " AND ".join(where_clauses)

    with get_connection() as connection:
        total = connection.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM todo_items
            WHERE {where_sql}
            """,
            query_values,
        ).fetchone()["total"]

        rows = connection.execute(
            f"""
            SELECT id, title, description, completed, user_id, created_at, updated_at
            FROM todo_items
            WHERE {where_sql}
            ORDER BY id
            LIMIT ?
            OFFSET ?
            """,
            (*query_values, limit, offset),
        ).fetchall()

    return [_row_to_todo_item(row) for row in rows], total


def get_todo_item(todo_item_id: int) -> TodoItemRead | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, description, completed, user_id, created_at, updated_at
            FROM todo_items
            WHERE id = ?
            """,
            (todo_item_id,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_todo_item(row)

# UPDATE
def update_todo_item(
    todo_item_id: int,
    todo_item_data: TodoItemUpdate,
) -> TodoItemRead | None:
    if get_todo_item(todo_item_id) is None:
        return None

    update_data = todo_item_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(UTC).isoformat()

    columns = []
    values = []

    for field, value in update_data.items():
        columns.append(f"{field} = ?")
        values.append(int(value) if field == "completed" else value)

    values.append(todo_item_id)

    with get_connection() as connection:
        connection.execute(
            f"""
            UPDATE todo_items
            SET {", ".join(columns)}
            WHERE id = ?
            """,
            values,
        )
        connection.commit()

    return get_todo_item(todo_item_id)

# DELETE
def delete_todo_item(todo_item_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM todo_items
            WHERE id = ?
            """,
            (todo_item_id,),
        )
        connection.commit()

    return cursor.rowcount > 0
