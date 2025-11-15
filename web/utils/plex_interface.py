"""
Plex server interface for web UI
Direct connection to Plex server for viewing users and stats
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from plexapi.server import PlexServer

    PLEX_AVAILABLE = True
except ImportError:
    PLEX_AVAILABLE = False


def get_plex_connection():
    """Get Plex server connection"""
    if not PLEX_AVAILABLE:
        return None

    try:
        from config.settings import PLEX_BASE_URL, PLEX_TOKEN

        if PLEX_BASE_URL and PLEX_TOKEN:
            plex = PlexServer(PLEX_BASE_URL, PLEX_TOKEN)
            return plex
    except ImportError as e:
        print(f"Plex settings not found: {e}")
    except Exception as e:
        print(f"Failed to connect to Plex: {e}")

    return None


def get_plex_users():
    """Get list of Plex users"""
    plex = get_plex_connection()
    if not plex:
        return []

    try:
        account = plex.myPlexAccount()
        users = account.users()

        user_list = []
        for user in users:
            user_list.append(
                {
                    "id": getattr(user, "id", 0),
                    "username": (
                        getattr(user, "username", None)
                        if hasattr(user, "username")
                        else getattr(user, "title", "Unknown")
                    ),
                    "email": getattr(user, "email", ""),
                    "friend": getattr(user, "friend", False),
                    "home": hasattr(user, "home") and getattr(user, "home", False),
                    "servers": (
                        len(getattr(user, "servers", []))
                        if hasattr(user, "servers")
                        else 0
                    ),
                }
            )

        return user_list
    except Exception as e:
        print(f"Error getting Plex users: {e}")
        return []


def get_plex_stats():
    """Get Plex server statistics"""
    plex = get_plex_connection()
    if not plex:
        return {
            "connected": False,
            "server_name": "N/A",
            "version": "N/A",
            "movies": 0,
            "shows": 0,
            "users": 0,
        }

    try:
        # Get library counts
        movies = 0
        shows = 0

        for section in plex.library.sections():
            if section.type == "movie":
                movies += section.totalSize
            elif section.type == "show":
                shows += section.totalSize

        # Get user count from invites database with status 'active'
        import sqlite3
        from config.settings import DATABASE_PATH

        users = 0
        try:
            conn = sqlite3.connect(os.path.join(DATABASE_PATH, "invites.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM invites WHERE status = 'active'")
            result = cursor.fetchone()
            users = result[0] if result else 0
            conn.close()
        except Exception as db_error:
            print(f"Error getting user count from database: {db_error}")
            users = 0

        return {
            "connected": True,
            "server_name": plex.friendlyName,
            "version": plex.version,
            "movies": movies,
            "shows": shows,
            "users": users,
            "platform": plex.platform,
            "platform_version": plex.platformVersion,
        }
    except Exception as e:
        print(f"Error getting Plex stats: {e}")
        return {
            "connected": False,
            "server_name": "Error",
            "version": "N/A",
            "movies": 0,
            "shows": 0,
            "users": 0,
        }


def verify_plex_invite(email):
    """Check if an email is already invited to Plex"""
    plex = get_plex_connection()
    if not plex:
        return False

    try:
        account = plex.myPlexAccount()
        users = account.users()

        for user in users:
            user_email = getattr(user, "email", None)
            if user_email and user_email.lower() == email.lower():
                return True

        return False
    except Exception as e:
        print(f"Error verifying Plex invite: {e}")
        return False
