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
    """Remove an invite and revoke Plex access"""
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

        invite_id_db, email, discord_user, status = invite_data

        # Try to remove from Plex if the invite was active/accepted
        plex_removed = False
        plex_message = ""
        notification_sent = False

        if status in ["active", "accepted"]:
            try:
                from cogs.helpers.plex_helper import plexremove
                from api.main import bot_instance
                from config.settings import PLEX_SERVER_NAME
                import discord
                import asyncio

                # Get Plex connection for removal
                plex = get_plex_connection()
                if plex:
                    # Try to remove using email (primary method)
                    result = plexremove(plex, email)

                    if result:
                        plex_removed = True
                        plex_message = (
                            f"User {email} removed from Plex server successfully"
                        )

                        # Try to send DM notification to the user
                        if bot_instance and bot_instance.is_ready():
                            try:

                                async def send_removal_notification():
                                    # Try to find the Discord user by username
                                    guild = None
                                    user_obj = None

                                    # Search all guilds for the user
                                    for g in bot_instance.guilds:
                                        for member in g.members:
                                            if (
                                                member.name.lower()
                                                == discord_user.lower()
                                            ):
                                                user_obj = member
                                                guild = g
                                                break
                                        if user_obj:
                                            break

                                    if user_obj:
                                        try:
                                            embed = discord.Embed(
                                                title="👋 StreamNet Plex Zugriff entfernt",
                                                description=(
                                                    f"**Hallo {user_obj.mention}!**\n\n"
                                                    f"Dein Zugriff auf **{PLEX_SERVER_NAME or 'Plex Server'}** wurde entfernt.\n\n"
                                                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                                    f"📧 Email: `{email}`\n"
                                                    f"🎬 Server: **{PLEX_SERVER_NAME or 'Plex Server'}**\n\n"
                                                    f"ℹ️ **Grund:**\n"
                                                    f"• Zugriff wurde über Web UI entfernt\n"
                                                    f"• Einladung wurde widerrufen\n\n"
                                                    f"💡 *Bei Fragen wende dich an einen Administrator*"
                                                ),
                                                color=0xE5A00D,
                                            )
                                            embed.set_thumbnail(
                                                url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
                                            )
                                            embed.set_footer(
                                                text=f"{PLEX_SERVER_NAME or 'Plex Server'} • Zugriff entfernt",
                                                icon_url="https://cdn.discordapp.com/emojis/1310635856318562334.png",
                                            )

                                            await user_obj.send(embed=embed)
                                            return True
                                        except discord.Forbidden:
                                            print(
                                                f"[INFO] Could not send DM to {discord_user} (DMs disabled)"
                                            )
                                            return False
                                    return False

                                future = asyncio.run_coroutine_threadsafe(
                                    send_removal_notification(), bot_instance.loop
                                )
                                notification_sent = future.result(timeout=5)

                            except Exception as e:
                                print(
                                    f"[WARNING] Could not send removal notification: {e}"
                                )
                    else:
                        plex_message = "Could not remove from Plex"
                else:
                    plex_message = "Plex connection unavailable"

            except Exception as e:
                print(f"Error removing from Plex: {e}")
                import traceback

                traceback.print_exc()
                plex_message = f"Failed to remove from Plex: {str(e)}"

        # Update invite status to 'revoked' (same as Discord role removal)
        cursor.execute(
            "UPDATE invites SET status = 'revoked' WHERE id = ?", (invite_id,)
        )
        conn.commit()
        conn.close()

        # Prepare response message
        if plex_removed:
            message = f"Invite revoked successfully. {plex_message}"
            if notification_sent:
                message += " User was notified via DM."
            else:
                message += " (Could not notify user - not found or DMs disabled)"
        elif status in ["active", "accepted"]:
            message = (
                f"Invite revoked in database, but Plex removal failed: {plex_message}"
            )
        else:
            message = (
                f"Invite revoked successfully (status: {status}, no Plex action needed)"
            )

        return {"success": True, "message": message, "plex_removed": plex_removed}

    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"success": False, "message": str(e)}
