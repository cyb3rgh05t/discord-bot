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
        logger.info(f"[PLEX INVITE] Starting invite process for: {plexname}")

        # Resolve library sections
        if plex_libs[0] == "all":
            plex_libs = plex.library.sections()
            lib_names = [lib.title for lib in plex_libs]
            logger.info(
                f"[PLEX INVITE] Sharing ALL libraries with {plexname}: {', '.join(lib_names)}"
            )
        else:
            lib_names = [
                lib if isinstance(lib, str) else lib.title for lib in plex_libs
            ]
            logger.info(
                f"[PLEX INVITE] Sharing selected libraries with {plexname}: {', '.join(lib_names)}"
            )

        # Send the invitation
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

        logger.info(
            f"[PLEX INVITE] SUCCESS: Successfully invited {plexname} to Plex server"
        )
        return True
    except Exception as e:
        logger.error(f"[PLEX INVITE] FAILED: Could not invite {plexname} to Plex: {e}")
        return False


def plexremove(plex, plexname):
    """
    Remove a user from the Plex server
    Args:
        plex: Plex server instance
        plexname: Email or username to remove
    """
    try:
        logger.info(f"[PLEX REMOVE] Starting removal process for: {plexname}")
        account = plex.myPlexAccount()

        # Get all friends to find the correct one
        friends = account.users()
        logger.debug(f"[PLEX REMOVE] Found {len(friends)} users on Plex server")

        # Try to find the user by email or username
        user_to_remove = None
        for friend in friends:
            # Check if the friend's email or username matches
            if (
                hasattr(friend, "email")
                and friend.email
                and friend.email.lower() == plexname.lower()
            ) or (
                hasattr(friend, "username")
                and friend.username
                and friend.username.lower() == plexname.lower()
            ):
                user_to_remove = (
                    friend.username if hasattr(friend, "username") else friend.email
                )
                logger.debug(f"[PLEX REMOVE] Found matching user: {user_to_remove}")
                break

        if user_to_remove:
            account.removeFriend(user=user_to_remove)
            logger.info(
                f"[PLEX REMOVE] SUCCESS: Removed {user_to_remove} (searched as {plexname}) from Plex"
            )
            return True
        else:
            # If not found, try the direct removal (backwards compatibility)
            logger.debug(
                f"[PLEX REMOVE] User not found in friends list, attempting direct removal"
            )
            account.removeFriend(user=plexname)
            logger.info(f"[PLEX REMOVE] SUCCESS: Removed {plexname} from Plex")
            return True

    except Exception as e:
        logger.error(
            f"[PLEX REMOVE] FAILED: Could not remove {plexname} from Plex: {e}"
        )
        return False


def verifyemail(addressToVerify):
    """
    Verify if an email address is valid
    """
    regex = r"(^[a-zA-Z0-9'_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
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
            logger.debug(f"[PLEX DB] Saving user to database: {user_id} -> {email}")
            conn.execute(
                f"""
                INSERT OR REPLACE INTO clients(discord_username, email)
                VALUES('{user_id}', '{email}')
                """
            )
            conn.commit()

            # Use username in logs if provided
            display_name = username or user_id
            logger.info(
                f"[PLEX DB] SUCCESS: User {display_name} added to database with email {email}"
            )
            return True
        except Exception as e:
            logger.error(f"[PLEX DB] FAILED: Could not save user to database: {e}")
            return False
    else:
        logger.warning("[PLEX DB] Username and email cannot be empty")
        return False


def get_user_email(conn, username):
    """Get a user's email from the database"""
    if username:
        try:
            logger.debug(f"[PLEX DB] Looking up email for user: {username}")
            cursor = conn.execute(
                'SELECT discord_username, email from clients where discord_username="{}";'.format(
                    username
                )
            )
            email = None  # Initialize email variable
            for row in cursor:
                email = row[1]
            if email:
                logger.debug(f"[PLEX DB] Found email for {username}: {email}")
                return email
            else:
                logger.debug(f"[PLEX DB] No email found for user: {username}")
                return None
        except Exception as e:
            logger.error(f"[PLEX DB] FAILED: Could not get user email: {e}")
            return None
    else:
        logger.warning("[PLEX DB] Username cannot be empty")
        return None


def remove_email(conn, username):
    """Set a user's email to null in the database"""
    if username:
        try:
            logger.debug(f"[PLEX DB] Removing email from user: {username}")
            conn.execute(
                f"UPDATE clients SET email = null WHERE discord_username = '{username}'"
            )
            conn.commit()
            logger.info(
                f"[PLEX DB] SUCCESS: Email removed from user {username} in database"
            )
            return True
        except Exception as e:
            logger.error(f"[PLEX DB] FAILED: Could not remove email: {e}")
            return False
    else:
        logger.warning("[PLEX DB] Username cannot be empty")
        return False


def delete_user(conn, username):
    """Delete a user from the database"""
    if username:
        try:
            logger.debug(f"[PLEX DB] Deleting user from database: {username}")
            conn.execute(
                'DELETE from clients where discord_username="{}";'.format(username)
            )
            conn.commit()
            logger.info(f"[PLEX DB] SUCCESS: User {username} deleted from database")
            return True
        except Exception as e:
            logger.error(f"[PLEX DB] FAILED: Could not delete user: {e}")
            return False
    else:
        logger.warning("[PLEX DB] Username cannot be empty")
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
