"""
Dashboard view - Main overview page
Shows bot status, statistics, and quick info
"""

from flask import Blueprint, render_template
from flask_login import login_required
from web.utils.decorators import auth_required
from web.utils.bot_interface import get_bot_status, get_bot_stats
from web.utils.database_helper import get_database_tables, get_db_connection
from web.utils.service_monitor import get_service_status, get_system_resources
import os

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@auth_required
def index():
    """Main dashboard page with comprehensive overview"""
    bot_status = get_bot_status()
    bot_stats = get_bot_stats()

    # Get database statistics
    tables = get_database_tables()
    databases = set()
    total_records = 0

    for table in tables:
        databases.add(table["database"])
        try:
            conn = get_db_connection(table["database"])
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table['name']}")
            count = cursor.fetchone()[0]
            total_records += count
            conn.close()
        except Exception:
            pass

    db_stats = {
        "databases": len(databases),
        "tables": len(tables),
        "records": total_records,
    }

    # Get invite statistics
    invite_stats = {"total": 0, "active": 0, "expired": 0}
    try:
        conn = get_db_connection("invites")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM invites")
        invite_stats["total"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM invites WHERE status = 'active'")
        invite_stats["active"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM invites WHERE status = 'expired'")
        invite_stats["expired"] = cursor.fetchone()[0]
        conn.close()
    except Exception:
        pass

    # Get ticket statistics
    ticket_stats = {"total": 0, "open": 0, "closed": 0}
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

        # Combine totals
        ticket_stats["total"] = plex_total + tv_total
        ticket_stats["open"] = plex_open + tv_open
        ticket_stats["closed"] = plex_closed + tv_closed

        conn.close()
    except Exception:
        pass

    # Get service status
    services = get_service_status()
    services_running = sum(1 for s in services if s["status"] == "running")

    # Get system resources
    resources = get_system_resources()

    return render_template(
        "dashboard/index.html",
        bot_status=bot_status,
        bot_stats=bot_stats,
        db_stats=db_stats,
        invite_stats=invite_stats,
        ticket_stats=ticket_stats,
        services=services,
        services_running=services_running,
        resources=resources,
    )
