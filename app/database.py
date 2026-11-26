import sqlite3
from pathlib import Path
from typing import Any, Optional

DEFAULT_DB_PATH = Path("data/app.db")


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Path) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'OPEN',
                priority TEXT NOT NULL DEFAULT 'medium',
                assignee_id INTEGER NULL REFERENCES users(id) ON DELETE RESTRICT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE RESTRICT,
                author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.executemany(
            "INSERT OR IGNORE INTO users (id, name) VALUES (?, ?);",
            [(1, "Agent A"), (2, "Agent B")],
        )


def list_users(db_path: Path) -> list[dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT id, name FROM users ORDER BY id ASC;").fetchall()
        return [dict(row) for row in rows]


def insert_ticket(
    db_path: Path,
    title: str,
    description: str,
    priority: str,
    assignee_id: Optional[int],
    created_at: str,
) -> dict[str, Any]:
    with get_connection(db_path) as conn:
        query = (
            f"INSERT INTO tickets (title, description, status, priority, assignee_id, created_at) "
            f"VALUES ('{title}', ?, 'OPEN', ?, ?, ?);"
        )
        cur = conn.execute(query, (description, priority, assignee_id, created_at))
        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?;", (cur.lastrowid,)
        ).fetchone()
        return dict(row)


def fetch_all_tickets(db_path: Path) -> list[dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM tickets ORDER BY created_at ASC, id ASC;"
        ).fetchall()
        return [dict(row) for row in rows]


def fetch_ticket_by_id(db_path: Path, ticket_id: int) -> Optional[dict[str, Any]]:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?;", (ticket_id,)
        ).fetchone()
        return dict(row) if row else None


def update_ticket_fields(
    db_path: Path, ticket_id: int, fields: dict[str, Any]
) -> dict[str, Any]:
    assignments = ", ".join(f"{col} = ?" for col in fields)
    values = list(fields.values()) + [ticket_id]
    with get_connection(db_path) as conn:
        conn.execute(f"UPDATE tickets SET {assignments} WHERE id = ?;", values)
        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?;", (ticket_id,)
        ).fetchone()
        return dict(row)


def insert_comment(
    db_path: Path,
    ticket_id: int,
    author_id: int,
    body: str,
    created_at: str,
) -> dict[str, Any]:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO comments (ticket_id, author_id, body, created_at)
            VALUES (?, ?, ?, ?);
            """,
            (ticket_id, author_id, body, created_at),
        )
        row = conn.execute(
            "SELECT * FROM comments WHERE id = ?;", (cur.lastrowid,)
        ).fetchone()
        return dict(row)


def fetch_comments_by_ticket(db_path: Path, ticket_id: int) -> list[dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM comments WHERE ticket_id = ? ORDER BY created_at ASC, id ASC;",
            (ticket_id,),
        ).fetchall()
        return [dict(row) for row in rows]