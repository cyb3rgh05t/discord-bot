"""Tickets endpoints"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from api.routers.auth import get_current_user, User
import os
import sqlite3
from datetime import datetime

router = APIRouter()


def get_bot_instance():
    """Get the Discord bot instance"""
    from api.main import bot_instance

    return bot_instance


def get_discord_usernames_bulk(user_ids):
    """Get Discord usernames for multiple user IDs"""
    bot = get_bot_instance()

    if not bot or not bot.is_ready():
        return {}

    usernames = {}
    for user_id in user_ids:
        try:
            user_id_int = int(user_id)
            user = bot.get_user(user_id_int)
            if user:
                usernames[str(user_id)] = str(user)
            else:
                usernames[str(user_id)] = f"User#{user_id}"
        except (ValueError, AttributeError):
            usernames[str(user_id)] = f"User#{user_id}"

    return usernames


class TicketItem(BaseModel):
    id: int
    user_id: str
    username: str
    type: str
    status: str
    created_at: str


class TicketStats(BaseModel):
    total: int
    open: int
    closed: int


class TicketsResponse(BaseModel):
    tickets: List[TicketItem]
    stats: TicketStats
    total_pages: int


def get_tickets_db_path():
    """Get the path to the tickets database"""
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "databases",
        "ticket_system.db",
    )
    return db_path if os.path.exists(db_path) else None


@router.get("/", response_model=TicketsResponse)
async def get_tickets(
    status: str = Query("all"),
    type: str = Query("all"),
    page: int = Query(1),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Get all tickets with filtering and pagination"""
    db_path = get_tickets_db_path()

    if not db_path:
        return TicketsResponse(
            tickets=[], stats=TicketStats(total=0, open=0, closed=0), total_pages=0
        )

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        all_tickets = []

        # Query plex tickets if type is 'all' or 'plex'
        if type in ["all", "plex"]:
            if status == "all":
                cursor.execute(
                    """
                    SELECT ticket_id, member_id, channel_id, type,
                           CASE WHEN closed = 1 THEN 'closed' ELSE 'open' END as status,
                           datetime(opened, 'unixepoch') as created_at
                    FROM plex_ticket_data
                    ORDER BY opened DESC
                """
                )
            else:
                closed_value = 1 if status == "closed" else 0
                cursor.execute(
                    """
                    SELECT ticket_id, member_id, channel_id, type,
                           CASE WHEN closed = 1 THEN 'closed' ELSE 'open' END as status,
                           datetime(opened, 'unixepoch') as created_at
                    FROM plex_ticket_data
                    WHERE closed = ?
                    ORDER BY opened DESC
                """,
                    (closed_value,),
                )

            for row in cursor.fetchall():
                all_tickets.append(
                    {
                        "id": row["ticket_id"],
                        "user_id": str(row["member_id"]),
                        "channel_id": str(row["channel_id"]),
                        "type": row["type"] or "unknown",
                        "ticket_type": "plex",
                        "status": row["status"],
                        "created_at": row["created_at"],
                    }
                )

        # Query TV tickets if type is 'all' or 'tv'
        if type in ["all", "tv"]:
            if status == "all":
                cursor.execute(
                    """
                    SELECT ticket_id, member_id, channel_id, type,
                           CASE WHEN closed = 1 THEN 'closed' ELSE 'open' END as status,
                           datetime(opened, 'unixepoch') as created_at
                    FROM tv_ticket_data
                    ORDER BY opened DESC
                """
                )
            else:
                closed_value = 1 if status == "closed" else 0
                cursor.execute(
                    """
                    SELECT ticket_id, member_id, channel_id, type,
                           CASE WHEN closed = 1 THEN 'closed' ELSE 'open' END as status,
                           datetime(opened, 'unixepoch') as created_at
                    FROM tv_ticket_data
                    WHERE closed = ?
                    ORDER BY opened DESC
                """,
                    (closed_value,),
                )

            for row in cursor.fetchall():
                all_tickets.append(
                    {
                        "id": row["ticket_id"],
                        "user_id": str(row["member_id"]),
                        "channel_id": str(row["channel_id"]),
                        "type": row["type"] or "unknown",
                        "ticket_type": "tv",
                        "status": row["status"],
                        "created_at": row["created_at"],
                    }
                )

        # Sort all tickets by created_at DESC
        all_tickets.sort(key=lambda x: x["created_at"], reverse=True)

        # Apply search filter
        if search:
            search_lower = search.lower()
            all_tickets = [
                t
                for t in all_tickets
                if search_lower in str(t["id"]).lower()
                or search_lower in t["user_id"].lower()
                or search_lower in t["type"].lower()
            ]

        # Calculate stats (from all tickets before pagination)
        open_count = sum(1 for t in all_tickets if t["status"] == "open")
        closed_count = sum(1 for t in all_tickets if t["status"] == "closed")
        total = len(all_tickets)

        # Pagination
        per_page = 10
        offset = (page - 1) * per_page
        paginated_tickets = all_tickets[offset : offset + per_page]

        # Get Discord usernames for paginated tickets
        user_ids = [t["user_id"] for t in paginated_tickets]
        usernames = get_discord_usernames_bulk(user_ids)

        # Convert to TicketItem models with real usernames
        tickets = [
            TicketItem(
                id=t["id"],
                user_id=t["user_id"],
                username=usernames.get(t["user_id"], f"User#{t['user_id']}"),
                type=t["type"],
                status=t["status"],
                created_at=t["created_at"],
            )
            for t in paginated_tickets
        ]

        conn.close()

        total_pages = (total + per_page - 1) // per_page if total > 0 else 0

        return TicketsResponse(
            tickets=tickets,
            stats=TicketStats(total=total, open=open_count, closed=closed_count),
            total_pages=total_pages,
        )

    except Exception as e:
        print(f"Error fetching tickets: {e}")
        import traceback

        traceback.print_exc()
        return TicketsResponse(
            tickets=[], stats=TicketStats(total=0, open=0, closed=0), total_pages=0
        )


@router.get("/{ticket_id}")
async def get_ticket_detail(
    ticket_id: int, current_user: User = Depends(get_current_user)
):
    """Get details for a specific ticket"""
    db_path = get_tickets_db_path()

    if not db_path:
        return {"success": False, "message": "Tickets database not found"}

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Try plex tickets first
        cursor.execute(
            """
            SELECT ticket_id, member_id, channel_id, type,
                   CASE WHEN closed = 1 THEN 'closed' ELSE 'open' END as status,
                   datetime(opened, 'unixepoch') as created_at,
                   NULL as closed_at,
                   claimed, claimed_by, locked
            FROM plex_ticket_data
            WHERE ticket_id = ?
        """,
            (ticket_id,),
        )

        row = cursor.fetchone()
        ticket_type = None

        if row:
            ticket_type = "plex"
        else:
            # Try TV tickets
            cursor.execute(
                """
                SELECT ticket_id, member_id, channel_id, type,
                       CASE WHEN closed = 1 THEN 'closed' ELSE 'open' END as status,
                       datetime(opened, 'unixepoch') as created_at,
                       NULL as closed_at,
                       claimed, claimed_by, locked
                FROM tv_ticket_data
                WHERE ticket_id = ?
            """,
                (ticket_id,),
            )
            row = cursor.fetchone()
            if row:
                ticket_type = "tv"

        conn.close()

        if not row:
            return {"success": False, "message": "Ticket not found"}

        # Convert row to dict
        ticket = dict(row)
        ticket["ticket_type"] = ticket_type
        ticket["id"] = ticket.pop("ticket_id")
        ticket["user_id"] = str(ticket.pop("member_id"))
        ticket["channel_id"] = str(ticket["channel_id"])

        # Remove falsy/null values for optional fields
        if not ticket.get("claimed"):
            ticket.pop("claimed", None)
            ticket.pop("claimed_by", None)
        if not ticket.get("locked"):
            ticket.pop("locked", None)
        if not ticket.get("closed_at"):
            ticket.pop("closed_at", None)

        # Get Discord username
        usernames = get_discord_usernames_bulk([ticket["user_id"]])
        ticket["username"] = usernames.get(
            ticket["user_id"], f"User#{ticket['user_id']}"
        )

        return {"success": True, "ticket": ticket}

    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.post("/{ticket_id}/close")
async def close_ticket(ticket_id: int, current_user: User = Depends(get_current_user)):
    """Close a ticket with full transcript creation like Discord"""
    db_path = get_tickets_db_path()

    if not db_path:
        return {"success": False, "message": "Tickets database not found"}

    from api.main import bot_instance
    from api.helpers.ticket_closer import close_ticket_with_transcript
    import asyncio

    if not bot_instance or not bot_instance.is_ready():
        return {"success": False, "message": "Bot is not ready"}

    try:
        future = asyncio.run_coroutine_threadsafe(
            close_ticket_with_transcript(
                ticket_id, db_path, bot_instance, current_user.username
            ),
            bot_instance.loop,
        )
        result = future.result(timeout=30)
        return result

    except Exception as e:
        print(f"Error in close_ticket endpoint: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.get("/{ticket_id}", response_model=TicketItem)
async def get_ticket(ticket_id: int, current_user: User = Depends(get_current_user)):
    """Get specific ticket"""
    db_path = get_tickets_db_path()

    if not db_path:
        return TicketItem(
            id=ticket_id,
            user_id="0",
            username="Unknown",
            type="general",
            status="open",
            created_at=datetime.now().isoformat(),
        )

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return TicketItem(
                id=row["id"],
                user_id=str(row["user_id"]),
                username=row["username"] or "Unknown",
                type=row["type"] or "general",
                status=row["status"],
                created_at=row["created_at"],
            )
        else:
            return TicketItem(
                id=ticket_id,
                user_id="0",
                username="Not Found",
                type="general",
                status="open",
                created_at=datetime.now().isoformat(),
            )

    except Exception as e:
        print(f"Error fetching ticket: {e}")
        return TicketItem(
            id=ticket_id,
            user_id="0",
            username="Error",
            type="general",
            status="open",
            created_at=datetime.now().isoformat(),
        )
