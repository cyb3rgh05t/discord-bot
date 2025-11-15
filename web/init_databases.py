"""
Initialize database tables if they don't exist
Run this once to set up the database structure
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.settings import DATABASE_PATH


def init_invites_db():
    """Initialize invites database"""
    db_path = os.path.join(DATABASE_PATH, "invites.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS invites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            discord_user TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TEXT NOT NULL,
            expires_at TEXT
        )
    """
    )

    conn.commit()
    conn.close()
    print("✓ Invites database initialized")


def init_ticket_system_db():
    """Initialize ticket system database"""
    db_path = os.path.join(DATABASE_PATH, "ticket_system.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Plex ticket panel
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS plex_ticket_panel (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            message_id INTEGER,
            category_id INTEGER,
            transcripts_id INTEGER,
            helpers_role_id INTEGER,
            everyone_role_id INTEGER,
            description TEXT,
            buttons TEXT
        )
    """
    )

    # Plex ticket data
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS plex_ticket_data (
            guild_id INTEGER,
            member_id INTEGER,
            ticket_id INTEGER,
            channel_id INTEGER,
            closed BOOLEAN,
            locked BOOLEAN,
            claimed BOOLEAN,
            claimed_by INTEGER,
            type TEXT,
            created_by INTEGER,
            opened TIMESTAMP,
            PRIMARY KEY (guild_id, channel_id)
        )
    """
    )

    # TV ticket panel
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tv_ticket_panel (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            message_id INTEGER,
            category_id INTEGER,
            transcripts_id INTEGER,
            helpers_role_id INTEGER,
            everyone_role_id INTEGER,
            description TEXT,
            buttons TEXT
        )
    """
    )

    # TV ticket data
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tv_ticket_data (
            guild_id INTEGER,
            member_id INTEGER,
            ticket_id INTEGER,
            channel_id INTEGER,
            closed BOOLEAN,
            locked BOOLEAN,
            claimed BOOLEAN,
            claimed_by INTEGER,
            type TEXT,
            created_by INTEGER,
            opened TIMESTAMP,
            PRIMARY KEY (guild_id, channel_id)
        )
    """
    )

    conn.commit()
    conn.close()
    print("✓ Ticket system database initialized")


def init_plex_clients_db():
    """Initialize plex clients database"""
    db_path = os.path.join(DATABASE_PATH, "plex_clients.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT NOT NULL,
            plex_email TEXT NOT NULL,
            plex_username TEXT,
            status TEXT DEFAULT 'active',
            invited_at TEXT NOT NULL,
            last_seen TEXT
        )
    """
    )

    conn.commit()
    conn.close()
    print("✓ Plex clients database initialized")


if __name__ == "__main__":
    print("Initializing databases...")
    print(f"Database path: {DATABASE_PATH}")

    # Create databases directory if it doesn't exist
    os.makedirs(DATABASE_PATH, exist_ok=True)

    init_invites_db()
    init_ticket_system_db()
    init_plex_clients_db()

    print("\n✓ All databases initialized successfully!")
    print("\nYou can now start the bot with: python bot.py")
