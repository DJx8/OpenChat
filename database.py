import sqlite3
import uuid

from pathlib import Path
from contextlib import contextmanager

# ---------------------------------
# DATABASE CONFIGURATION
# ---------------------------------

DB_PATH = Path(__file__).resolve().parent / "openchat.db"


# ---------------------------------
# DATABASE CONNECTION
# ---------------------------------


@contextmanager
def get_connection():

    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ---------------------------------
# INITIALIZE DATABASE
# ---------------------------------


def init_db():

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                owner_id TEXT NOT NULL DEFAULT ''
            )
        """)

        # Add owner_id to an older database if it does not exist.
        columns = [
            row["name"] for row in conn.execute("PRAGMA table_info(chats)").fetchall()
        ]

        if "owner_id" not in columns:
            conn.execute("""
                ALTER TABLE chats
                ADD COLUMN owner_id TEXT NOT NULL DEFAULT ''
            """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
            )
        """)


# ---------------------------------
# CREATE A NEW CHAT
# ---------------------------------


def create_chat(owner_id, title="New Chat"):

    chat_id = str(uuid.uuid4())

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chats (id, title, owner_id)
            VALUES (?, ?, ?)
        """,
            (chat_id, title, owner_id),
        )

    return chat_id


# ---------------------------------
# GET CHATS FOR ONE SESSION
# ---------------------------------


def get_chats(owner_id):

    with get_connection() as conn:

        # Preserve older local chats by assigning unowned chats
        # to the first session that accesses the database.
        conn.execute(
            """
            UPDATE chats
            SET owner_id = ?
            WHERE owner_id = ''
        """,
            (owner_id,),
        )

        rows = conn.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM chats
            WHERE owner_id = ?
            ORDER BY updated_at DESC
        """,
            (owner_id,),
        ).fetchall()

    return [dict(row) for row in rows]


# ---------------------------------
# GET MESSAGES OF A CHAT
# ---------------------------------


def get_messages(chat_id, owner_id):

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT messages.role, messages.content
            FROM messages
            INNER JOIN chats ON messages.chat_id = chats.id
            WHERE messages.chat_id = ?
              AND chats.owner_id = ?
            ORDER BY messages.id ASC
        """,
            (chat_id, owner_id),
        ).fetchall()

    return [dict(row) for row in rows]


# ---------------------------------
# ADD A MESSAGE
# ---------------------------------


def add_message(chat_id, owner_id, role, content):

    with get_connection() as conn:

        conn.execute(
            """
            INSERT INTO messages (chat_id, role, content)
            SELECT ?, ?, ?
            WHERE EXISTS (
                SELECT 1 FROM chats
                WHERE id = ? AND owner_id = ?
            )
        """,
            (chat_id, role, content, chat_id, owner_id),
        )

        conn.execute(
            """
            UPDATE chats
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND owner_id = ?
        """,
            (chat_id, owner_id),
        )


# ---------------------------------
# RENAME A CHAT
# ---------------------------------


def rename_chat(chat_id, owner_id, new_title):

    with get_connection() as conn:

        conn.execute(
            """
            UPDATE chats
            SET title = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND owner_id = ?
        """,
            (new_title, chat_id, owner_id),
        )


# ---------------------------------
# DELETE A CHAT
# ---------------------------------


def delete_chat(chat_id, owner_id):

    with get_connection() as conn:

        conn.execute(
            """
            DELETE FROM chats
            WHERE id = ? AND owner_id = ?
        """,
            (chat_id, owner_id),
        )
