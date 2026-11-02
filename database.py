
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

    connection = sqlite3.connect(
        DB_PATH,
        timeout=10
    )

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

        conn.executescript("""

            CREATE TABLE IF NOT EXISTS chats (

                id TEXT PRIMARY KEY,

                title TEXT NOT NULL,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP

            );


            CREATE TABLE IF NOT EXISTS messages (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                chat_id TEXT NOT NULL,

                role TEXT NOT NULL
                    CHECK(role IN ('user', 'assistant')),

                content TEXT NOT NULL,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(chat_id)
                    REFERENCES chats(id)
                    ON DELETE CASCADE

            );

        """)


# ---------------------------------
# CREATE A NEW CHAT
# ---------------------------------

def create_chat(title="New Chat"):

    chat_id = str(uuid.uuid4())

    with get_connection() as conn:

        conn.execute("""

            INSERT INTO chats (id, title)

            VALUES (?, ?)

        """, (chat_id, title))

    return chat_id


# ---------------------------------
# GET ALL CHATS
# ---------------------------------

def get_chats():

    with get_connection() as conn:

        rows = conn.execute("""

            SELECT id, title, created_at, updated_at

            FROM chats

            ORDER BY updated_at DESC

        """).fetchall()

    return [dict(row) for row in rows]


# ---------------------------------
# GET MESSAGES OF A CHAT
# ---------------------------------

def get_messages(chat_id):

    with get_connection() as conn:

        rows = conn.execute("""

            SELECT role, content

            FROM messages

            WHERE chat_id = ?

            ORDER BY id ASC

        """, (chat_id,)).fetchall()

    return [dict(row) for row in rows]


# ---------------------------------
# ADD A MESSAGE
# ---------------------------------

def add_message(chat_id, role, content):

    with get_connection() as conn:

        conn.execute("""

            INSERT INTO messages (chat_id, role, content)

            VALUES (?, ?, ?)

        """, (chat_id, role, content))

        conn.execute("""

            UPDATE chats

            SET updated_at = CURRENT_TIMESTAMP

            WHERE id = ?

        """, (chat_id,))


# ---------------------------------
# RENAME A CHAT
# ---------------------------------

def rename_chat(chat_id, new_title):

    with get_connection() as conn:

        conn.execute("""

            UPDATE chats

            SET title = ?,
                updated_at = CURRENT_TIMESTAMP

            WHERE id = ?

        """, (new_title, chat_id))


# ---------------------------------
# DELETE A CHAT
# ---------------------------------

def delete_chat(chat_id):

    with get_connection() as conn:

        conn.execute("""

            DELETE FROM chats

            WHERE id = ?

        """, (chat_id,))
