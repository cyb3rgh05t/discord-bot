"""Invites endpoints"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from api.routers.auth import get_current_user, User
import os
import sqlite3
from datetime import datetime, timedelta

router = APIRouter()


class InviteItem(BaseModel):
    id: int
    email: str
    discord_user: str
    status: str
    created_at: str
    expires_at: Optional[str] = None


class InviteStats(BaseModel):
    total: int
    active: int
    expired: int
    revoked: int
    removed: int


class PlexStats(BaseModel):
    connected: bool
    server_name: str
    version: str
    movies: int
    shows: int
    users: int


class InvitesResponse(BaseModel):
    invites: List[InviteItem]
    stats: InviteStats
    plex_stats: PlexStats
    total_pages: int


class AddInviteRequest(BaseModel):
    email: EmailStr
    discord_user: str


def get_invites_db_path():
    """Get the path to the invites database"""
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "databases",
        "invites.db",
    )
    return db_path if os.path.exists(db_path) else None


def get_plex_connection():
    """Get Plex connection"""
    try:
        from plexapi.server import PlexServer
        from config.settings import PLEX_BASE_URL, PLEX_TOKEN

        if not PLEX_BASE_URL or not PLEX_TOKEN:
            return None
        return PlexServer(PLEX_BASE_URL, PLEX_TOKEN)
    except Exception as e:
        print(f"Error connecting to Plex: {e}")
        return None


@router.get("/", response_model=InvitesResponse)
async def get_invites(
    page: int = Query(1),
    per_page: int = Query(10),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Get all invites with filtering and pagination"""
    db_path = get_invites_db_path()

    if not db_path:
        return InvitesResponse(
            invites=[],
            stats=InviteStats(total=0, active=0, expired=0, revoked=0, removed=0),
            plex_stats=PlexStats(
                connected=False,
                server_name="N/A",
                version="N/A",
                movies=0,
                shows=0,
                users=0,
            ),
            total_pages=0,
        )

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all invites
        cursor.execute(
            """
            SELECT id, email, discord_user, status, created_at, expires_at
            FROM invites
            ORDER BY created_at DESC
        """
        )

        all_invites = []
        for row in cursor.fetchall():
            all_invites.append(dict(row))

        # Apply search filter
        if search:
            search_lower = search.lower()
            all_invites = [
                inv
                for inv in all_invites
                if search_lower in inv.get("email", "").lower()
                or search_lower in inv.get("discord_user", "").lower()
            ]

        # Get stats
        cursor.execute("SELECT COUNT(*) FROM invites")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM invites WHERE status = 'active'")
        active = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM invites WHERE status = 'expired'")
        expired = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM invites WHERE status = 'revoked'")
        revoked = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM invites WHERE status = 'removed'")
        removed = cursor.fetchone()[0]

        conn.close()

        # Pagination
        total_count = len(all_invites)
        offset = (page - 1) * per_page
        paginated_invites = all_invites[offset : offset + per_page]

        # Get Plex stats
        plex = get_plex_connection()
        if plex:
            try:
                movies = 0
                shows = 0
                for section in plex.library.sections():
                    if section.type == "movie":
                        movies += section.totalSize
                    elif section.type == "show":
                        shows += section.totalSize

                plex_stats = PlexStats(
                    connected=True,
                    server_name=plex.friendlyName,
                    version=plex.version,
                    movies=movies,
                    shows=shows,
                    users=active,
                )
            except Exception as e:
                print(f"Error getting Plex stats: {e}")
                plex_stats = PlexStats(
                    connected=False,
                    server_name="N/A",
                    version="N/A",
                    movies=0,
                    shows=0,
                    users=0,
                )
        else:
            plex_stats = PlexStats(
                connected=False,
                server_name="N/A",
                version="N/A",
                movies=0,
                shows=0,
                users=0,
            )

        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

        return InvitesResponse(
            invites=[
                InviteItem(
                    id=inv["id"],
                    email=inv["email"],
                    discord_user=inv["discord_user"],
                    status=inv["status"],
                    created_at=inv["created_at"],
                    expires_at=inv.get("expires_at"),
                )
                for inv in paginated_invites
            ],
            stats=InviteStats(
                total=total,
                active=active,
                expired=expired,
                revoked=revoked,
                removed=removed,
            ),
            plex_stats=plex_stats,
            total_pages=total_pages,
        )

    except Exception as e:
        print(f"Error fetching invites: {e}")
        import traceback

        traceback.print_exc()
        return InvitesResponse(
            invites=[],
            stats=InviteStats(total=0, active=0, expired=0, revoked=0, removed=0),
            plex_stats=PlexStats(
                connected=False,
                server_name="N/A",
                version="N/A",
                movies=0,
                shows=0,
                users=0,
            ),
            total_pages=0,
        )


@router.post("/add")
async def add_invite(
    invite: AddInviteRequest, current_user: User = Depends(get_current_user)
):
    """Add a new invite"""
    db_path = get_invites_db_path()

    if not db_path:
        return {"success": False, "message": "Invites database not found"}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        expires = (datetime.now() + timedelta(days=30)).isoformat()

        cursor.execute(
            """
            INSERT INTO invites (email, discord_user, status, created_at, expires_at)
            VALUES (?, ?, 'active', ?, ?)
        """,
            (invite.email, invite.discord_user, now, expires),
        )

        conn.commit()
        invite_id = cursor.lastrowid
        conn.close()

        return {
            "success": True,
            "message": "Invite added successfully",
            "id": invite_id,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.post("/{invite_id}/remove")
async def remove_invite(invite_id: int, current_user: User = Depends(get_current_user)):
    """Remove an invite"""
    db_path = get_invites_db_path()

    if not db_path:
        return {"success": False, "message": "Invites database not found"}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get invite data before deletion
        cursor.execute(
            "SELECT id, email, discord_user, status FROM invites WHERE id = ?",
            (invite_id,),
        )
        invite_data = cursor.fetchone()

        if not invite_data:
            conn.close()
            return {"success": False, "message": "Invite not found"}

        # Delete the invite
        cursor.execute("DELETE FROM invites WHERE id = ?", (invite_id,))
        conn.commit()
        conn.close()

        return {"success": True, "message": "Invite removed successfully"}

    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"success": False, "message": str(e)}
