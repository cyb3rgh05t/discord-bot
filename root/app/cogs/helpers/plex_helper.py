import re
import logging
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer

logger = logging.getLogger(__name__)


def verify_email(address_to_verify):
    """Verify if a string is a valid email address."""
    regex = "(^[a-zA-Z0-9'_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    match = re.match(regex, address_to_verify.lower())
    return match is not None


def plex_invite(plex, plex_email, plex_libs):
    """Invite user to Plex server."""
    try:
        if plex_libs[0] == "all":
            plex_libs = plex.library.sections()

        plex.myPlexAccount().inviteFriend(
            user=plex_email,
            server=plex,
            sections=plex_libs,
            allowSync=False,
            allowCameraUpload=False,
            allowChannels=False,
            filterMovies=None,
            filterTelevision=None,
            filterMusic=None,
        )
        logger.info(f"{plex_email} has been added to Plex")
        return True
    except Exception as e:
        logger.error(f"Error inviting user to Plex: {e}")
        return False


def plex_remove(plex, plex_email):
    """Remove user from Plex server."""
    try:
        plex.myPlexAccount().removeFriend(user=plex_email)
        logger.info(f"{plex_email} has been removed from Plex")
        return True
    except Exception as e:
        logger.error(f"Error removing user from Plex: {e}")
        return False


def connect_to_plex(
    plex_user=None,
    plex_pass=None,
    plex_server_name=None,
    plex_token=None,
    plex_base_url=None,
):
    """Connect to Plex server using either username/password or token."""
    try:
        if plex_token and plex_base_url:
            logger.info("Connecting to Plex using auth token")
            return PlexServer(plex_base_url, plex_token)
        elif plex_user and plex_pass and plex_server_name:
            logger.info("Connecting to Plex using credentials")
            account = MyPlexAccount(plex_user, plex_pass)
            return account.resource(plex_server_name).connect()
        else:
            logger.error("Insufficient credentials to connect to Plex")
            return None
    except Exception as e:
        logger.error(f"Error connecting to Plex: {e}")
        return None
