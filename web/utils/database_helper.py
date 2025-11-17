"""
Database helper functions
Query and manage SQLite databases
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def get_db_connection(db_name="invites"):
    """Get database connection"""
    db_path = os.path.join("databases", f"{db_name}.db")
    return sqlite3.connect(db_path)


def find_table_database(table_name):
    """Find which database contains the specified table"""
    database_path = "databases"

    if not os.path.exists(database_path):
        return None

    for db_file in os.listdir(database_path):
        if db_file.endswith(".db"):
            db_name = db_file[:-3]
            try:
                conn = get_db_connection(db_name)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,),
                )
                result = cursor.fetchone()
                conn.close()

                if result:
                    return db_name
            except Exception:
                continue

    return None


def get_database_tables():
    """Get list of all tables in databases"""
    tables = []

    # Check each database file
    if os.path.exists("databases"):
        for db_file in os.listdir("databases"):
            if db_file.endswith(".db"):
                db_name = db_file[:-3]
                try:
                    conn = get_db_connection(db_name)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

                    for row in cursor.fetchall():
                        tables.append({"database": db_name, "name": row[0]})

                    conn.close()
                except Exception:
                    continue

    return tables


def get_table_data(table_name, page=1, per_page=50):
    """Get data from a specific table"""
    # Validate table name (prevent SQL injection)
    if not table_name.replace("_", "").isalnum():
        raise ValueError(f"Invalid table name: {table_name}")

    # Find which database contains this table
    db_name = find_table_database(table_name)

    if not db_name:
        raise ValueError(f"Table '{table_name}' not found in any database")

    try:
        conn = get_db_connection(db_name)
        cursor = conn.cursor()

        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]

        # Get paginated data
        offset = (page - 1) * per_page
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {per_page} OFFSET {offset}")

        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        conn.close()

        return {
            "columns": columns,
            "rows": rows,
            "page": page,
            "per_page": per_page,
            "total": total_count,
            "database": db_name,
        }
    except sqlite3.OperationalError as e:
        if conn:
            conn.close()
        raise ValueError(f"Database error accessing table '{table_name}': {str(e)}")
    except Exception as e:
        if conn:
            conn.close()
        raise


def get_table_schema(table_name, db_name=None):
    """Get schema for a table"""
    # Validate table name (prevent SQL injection)
    if not table_name.replace("_", "").isalnum():
        raise ValueError(f"Invalid table name: {table_name}")

    if not db_name:
        db_name = find_table_database(table_name)

    if not db_name:
        raise ValueError(f"Table '{table_name}' not found in any database")

    try:
        conn = get_db_connection(db_name)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")

        schema_raw = cursor.fetchall()
        conn.close()

        # Convert to dict format
        schema = []
        for col in schema_raw:
            schema.append(
                {
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "default": col[4],
                    "pk": bool(col[5]),
                }
            )

        return schema
    except Exception as e:
        if conn:
            conn.close()
        raise ValueError(f"Error getting schema for table '{table_name}': {str(e)}")


def execute_query(sql):
    """Execute a read-only SQL query"""
    # Security: Only allow SELECT queries
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed")

    db_name = "invites"
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute(sql)

    results = cursor.fetchall()
    conn.close()

    return results


# Specific helper functions for common operations


def get_tickets(status="all"):
    """Get tickets from database"""
    try:
        conn = get_db_connection("ticket_system")
        cursor = conn.cursor()

        tickets = []

        # Query plex tickets
        if status == "all":
            cursor.execute(
                """
                SELECT ticket_id, member_id, channel_id, type, 
                       CASE WHEN closed = 1 THEN 'closed' ELSE 'open' END as status,
                       datetime(opened, 'unixepoch') as created_at,
                       NULL as closed_at
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
                       datetime(opened, 'unixepoch') as created_at,
                       NULL as closed_at
                FROM plex_ticket_data
                WHERE closed = ?
                ORDER BY opened DESC
            """,
                (closed_value,),
            )

        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            ticket = dict(zip(columns, row))
            ticket["ticket_type"] = "plex"
            ticket["id"] = ticket.pop("ticket_id")
            ticket["user_id"] = str(ticket.pop("member_id"))
            ticket["channel_id"] = str(ticket["channel_id"])
            ticket["type"] = ticket.pop("type", "unknown")
            tickets.append(ticket)

        # Query TV tickets
        if status == "all":
            cursor.execute(
                """
                SELECT ticket_id, member_id, channel_id, type,
                       CASE WHEN closed = 1 THEN 'closed' ELSE 'open' END as status,
                       datetime(opened, 'unixepoch') as created_at,
                       NULL as closed_at
                FROM tv_ticket_data
                ORDER BY opened DESC
            """
            )
        else:
            cursor.execute(
                """
                SELECT ticket_id, member_id, channel_id, type,
                       CASE WHEN closed = 1 THEN 'closed' ELSE 'open' END as status,
                       datetime(opened, 'unixepoch') as created_at,
                       NULL as closed_at
                FROM tv_ticket_data
                WHERE closed = ?
                ORDER BY opened DESC
            """,
                (closed_value,),
            )

        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            ticket = dict(zip(columns, row))
            ticket["ticket_type"] = "tv"
            ticket["id"] = ticket.pop("ticket_id")
            ticket["user_id"] = str(ticket.pop("member_id"))
            ticket["channel_id"] = str(ticket["channel_id"])
            ticket["type"] = ticket.pop("type", "unknown")
            tickets.append(ticket)

        conn.close()

        # Sort all tickets by created_at
        tickets.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return tickets
    except sqlite3.OperationalError as e:
        print(f"Error getting tickets: {e}")
        return []


def get_ticket_details(ticket_id):
    """Get details for a specific ticket"""
    try:
        conn = get_db_connection("ticket_system")
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
        if row:
            columns = [desc[0] for desc in cursor.description]
            ticket = dict(zip(columns, row))
            ticket["ticket_type"] = "plex"
            ticket["id"] = ticket.pop("ticket_id")
            ticket["user_id"] = str(ticket.pop("member_id"))
            ticket["channel_id"] = str(ticket["channel_id"])
            ticket["type"] = ticket.pop("type", "unknown")
            conn.close()
            return ticket

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
            columns = [desc[0] for desc in cursor.description]
            ticket = dict(zip(columns, row))
            ticket["ticket_type"] = "tv"
            ticket["id"] = ticket.pop("ticket_id")
            ticket["user_id"] = str(ticket.pop("member_id"))
            ticket["channel_id"] = str(ticket["channel_id"])
            ticket["type"] = ticket.pop("type", "unknown")
            conn.close()
            return ticket

        conn.close()
        return None
    except sqlite3.OperationalError as e:
        print(f"Error getting ticket details: {e}")
        return None


def close_ticket(ticket_id):
    """Close a ticket"""
    try:
        conn = get_db_connection("ticket_system")
        cursor = conn.cursor()

        # Try to close in plex tickets
        cursor.execute(
            """
            UPDATE plex_ticket_data
            SET closed = 1
            WHERE ticket_id = ?
        """,
            (ticket_id,),
        )

        if cursor.rowcount == 0:
            # Try TV tickets
            cursor.execute(
                """
                UPDATE tv_ticket_data
                SET closed = 1
                WHERE ticket_id = ?
            """,
                (ticket_id,),
            )

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except sqlite3.OperationalError as e:
        print(f"Error closing ticket: {e}")
        return False


def get_invites():
    """Get all invites"""
    try:
        conn = get_db_connection("invites")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, email, discord_user, status, created_at, expires_at
            FROM invites
            ORDER BY created_at DESC
        """
        )

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        # Convert to list of dicts
        invites = []
        for row in rows:
            invite = dict(zip(columns, row))
            invites.append(invite)

        return invites
    except sqlite3.OperationalError:
        # Table doesn't exist, return empty list
        return []


def add_invite(email, discord_user):
    """Add a new invite"""
    try:
        conn = get_db_connection("invites")
        cursor = conn.cursor()

        from datetime import datetime, timedelta

        now = datetime.now().isoformat()
        expires = (datetime.now() + timedelta(days=30)).isoformat()

        cursor.execute(
            """
            INSERT INTO invites (email, discord_user, status, created_at, expires_at)
            VALUES (?, ?, 'active', ?, ?)
        """,
            (email, discord_user, now, expires),
        )

        conn.commit()
        invite_id = cursor.lastrowid
        conn.close()
        return invite_id
    except Exception as e:
        return None


def remove_invite(invite_id):
    """Remove an invite and return the invite data"""
    try:
        conn = get_db_connection("invites")
        cursor = conn.cursor()

        # Get invite data before deletion
        cursor.execute(
            "SELECT id, email, discord_user, status FROM invites WHERE id = ?",
            (invite_id,),
        )
        invite_data = cursor.fetchone()

        if not invite_data:
            conn.close()
            return None

        # Convert to dict
        invite = {
            "id": invite_data[0],
            "email": invite_data[1],
            "discord_user": invite_data[2],
            "status": invite_data[3],
        }

        # Delete the invite
        cursor.execute("DELETE FROM invites WHERE id = ?", (invite_id,))

        conn.commit()
        conn.close()
        return invite
    except Exception as e:
        return None


def get_invite_stats():
    """Get invite statistics"""
    try:
        conn = get_db_connection("invites")
        cursor = conn.cursor()

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

        return {
            "total": total,
            "active": active,
            "expired": expired,
            "revoked": revoked,
            "removed": removed,
        }
    except sqlite3.OperationalError:
        return {"total": 0, "active": 0, "expired": 0, "revoked": 0, "removed": 0}


def get_ticket_stats():
    """Get ticket statistics"""
    try:
        conn = get_db_connection("ticket_system")
        cursor = conn.cursor()

        # Count plex tickets
        cursor.execute("SELECT COUNT(*) FROM plex_ticket_data")
        plex_total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM plex_ticket_data WHERE closed = 0")
        plex_open = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM plex_ticket_data WHERE closed = 1")
        plex_closed = cursor.fetchone()[0]

        # Count TV tickets
        cursor.execute("SELECT COUNT(*) FROM tv_ticket_data")
        tv_total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tv_ticket_data WHERE closed = 0")
        tv_open = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tv_ticket_data WHERE closed = 1")
        tv_closed = cursor.fetchone()[0]

        conn.close()

        return {
            "total": plex_total + tv_total,
            "open": plex_open + tv_open,
            "closed": plex_closed + tv_closed,
        }
    except sqlite3.OperationalError as e:
        print(f"Error getting ticket stats: {e}")
        return {"total": 0, "open": 0, "closed": 0}
