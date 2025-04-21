import sqlite3
import logging
import os

logger = logging.getLogger(__name__)

# Database path
DB_PATH = "databases/plex_users.db"


def create_connection():
    """Create a database connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    try:
        conn = sqlite3.connect(DB_PATH)
        logger.info("Connected to Plex users database")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None


def init_db():
    """Initialize the database with necessary tables."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS plex_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id TEXT NOT NULL UNIQUE,
                    email TEXT
                )
            """
            )
            conn.commit()
            logger.info("Plex users table initialized")
            conn.close()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error creating table: {e}")
            return False
    else:
        return False


def save_user_email(discord_id, email):
    """Save a user's Discord ID and Plex email."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO plex_users (discord_id, email) VALUES (?, ?)",
                (discord_id, email),
            )
            conn.commit()
            conn.close()
            logger.info(f"User {discord_id} added to database with email {email}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving user: {e}")
            conn.close()
            return False
    else:
        return False


def get_user_email(discord_id):
    """Get a user's Plex email by Discord ID."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT email FROM plex_users WHERE discord_id = ?", (discord_id,)
            )
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]
            else:
                return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching user email: {e}")
            conn.close()
            return None
    else:
        return None


def remove_user(discord_id):
    """Remove a user from the database."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM plex_users WHERE discord_id = ?", (discord_id,))
            conn.commit()
            conn.close()
            logger.info(f"User {discord_id} removed from database")
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error removing user: {e}")
            conn.close()
            return False
    else:
        return False


def get_all_users():
    """Get all users from the database."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plex_users")
            users = cursor.fetchall()
            conn.close()
            return users
        except sqlite3.Error as e:
            logger.error(f"Error fetching all users: {e}")
            conn.close()
            return []
    else:
        return []


# Initialize the database when the module is imported
init_db()
