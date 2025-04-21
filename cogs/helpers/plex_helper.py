from plexapi.myplex import MyPlexAccount
import re
import logging
import sqlite3
import os
import discord
from cogs.helpers.logger import logger


def plexinviter(plex, plexname, plex_libs):
    """
    Invite a user to the Plex server
    """
    try:
        if plex_libs[0] == "all":
            plex_libs = plex.library.sections()
        plex.myPlexAccount().inviteFriend(
            user=plexname,
            server=plex,
            sections=plex_libs,
            allowSync=False,
            allowCameraUpload=False,
            allowChannels=False,
            filterMovies=None,
            filterTelevision=None,
            filterMusic=None,
        )
        logger.info(f"{plexname} has been added to Plex")
        return True
    except Exception as e:
        logger.error(f"Error adding {plexname} to Plex: {e}")
        return False


def plexremove(plex, plexname):
    """
    Remove a user from the Plex server
    """
    try:
        plex.myPlexAccount().removeFriend(user=plexname)
        logger.info(f"{plexname} has been removed from Plex")
        return True
    except Exception as e:
        logger.error(f"Error removing {plexname} from Plex: {e}")
        return False


def verifyemail(addressToVerify):
    """
    Verify if an email address is valid
    """
    regex = "(^[a-zA-Z0-9'_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    match = re.match(regex, addressToVerify.lower())
    return match is not None


# Database operations
def create_connection(db_file):
    """Create a database connection to a SQLite database"""
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        logger.info("Connected to Plex database")
    except sqlite3.Error as e:
        logger.error(f"Error connecting to Plex database: {e}")
    return conn


def check_table_exists(dbcon, tablename):
    """Check if a table exists in the database"""
    dbcur = dbcon.cursor()
    dbcur.execute(
        """SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{0}';""".format(
            tablename.replace("'", "''")
        )
    )
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True
    dbcur.close()
    return False


def init_db(db_path):
    """Initialize the database"""
    conn = create_connection(db_path)
    if conn:
        if not check_table_exists(conn, "clients"):
            conn.execute(
                """CREATE TABLE "clients" (
                "id"	INTEGER NOT NULL UNIQUE,
                "discord_username"	TEXT NOT NULL UNIQUE,
                "email"	TEXT,
                PRIMARY KEY("id" AUTOINCREMENT)
                );"""
            )
            conn.commit()
            logger.info("Created Plex clients table")
    return conn


def save_user_email(conn, user_id, email, username=None):
    """Save a user's email to the database"""
    if user_id and email:
        try:
            conn.execute(
                f"""
                INSERT OR REPLACE INTO clients(discord_username, email)
                VALUES('{user_id}', '{email}')
                """
            )
            conn.commit()

            # Use username in logs if provided
            display_name = username or user_id
            logger.info(f"User {display_name} added to database with email {email}")
            return True
        except Exception as e:
            logger.error(f"Error saving user to database: {e}")
            return False
    else:
        logger.warning("Username and email cannot be empty")
        return False


def get_user_email(conn, username):
    """Get a user's email from the database"""
    if username:
        try:
            cursor = conn.execute(
                'SELECT discord_username, email from clients where discord_username="{}";'.format(
                    username
                )
            )
            email = None  # Initialize email variable
            for row in cursor:
                email = row[1]
            if email:
                return email
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting user email: {e}")
            return None
    else:
        logger.warning("Username cannot be empty")
        return None


def remove_email(conn, username):
    """Set a user's email to null in the database"""
    if username:
        try:
            conn.execute(
                f"UPDATE clients SET email = null WHERE discord_username = '{username}'"
            )
            conn.commit()
            logger.info(f"Email removed from user {username} in database")
            return True
        except Exception as e:
            logger.error(f"Error removing email: {e}")
            return False
    else:
        logger.warning("Username cannot be empty")
        return False


def delete_user(conn, username):
    """Delete a user from the database"""
    if username:
        try:
            conn.execute(
                'DELETE from clients where discord_username="{}";'.format(username)
            )
            conn.commit()
            logger.info(f"User {username} deleted from database")
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    else:
        logger.warning("Username cannot be empty")
        return False


def read_all_users(conn):
    """Read all users from the database"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients")
        rows = cur.fetchall()
        all_users = []
        for row in rows:
            all_users.append(row)
        return all_users
    except Exception as e:
        logger.error(f"Error reading users from database: {e}")
        return []


# Add this setup function to make it compatible with Discord's extension loader
# This will allow the bot to load this file as a cog even though it's just a helper module
async def setup(bot):
    # This is just a helper module, so we don't need to do anything here
    pass
