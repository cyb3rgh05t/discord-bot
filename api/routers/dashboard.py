"""
Dashboard endpoints
Main dashboard stats and overview
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import sys
import os
import psutil
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.main import get_bot_instance

router = APIRouter()


class BotStatus(BaseModel):
    online: bool
    name: str
    latency: str
    uptime: str
    guilds: int
    users: int


class BotStats(BaseModel):
    channels: int
    roles: int
    commands: int


class TicketStats(BaseModel):
    open: int
    closed: int
    total: int


class InviteStats(BaseModel):
    active: int
    expired: int
    total: int


class DatabaseStats(BaseModel):
    databases: int
    tables: int
    records: int


class ResourceItem(BaseModel):
    percent: float
    label: str


class SystemResources(BaseModel):
    cpu: ResourceItem
    memory: ResourceItem
    disk: ResourceItem


class ServiceItem(BaseModel):
    name: str
    status: str
    icon: str


class DashboardData(BaseModel):
    bot_status: BotStatus
    bot_stats: BotStats
    ticket_stats: TicketStats
    invite_stats: InviteStats
    db_stats: DatabaseStats
    resources: SystemResources
    services: List[ServiceItem]
    services_running: int


def get_db_connection(db_name: str):
    """Get database connection"""
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "databases",
        f"{db_name}.db",
    )
    return sqlite3.connect(db_path)


def get_bot_status() -> BotStatus:
    """Get bot status information"""
    bot = get_bot_instance()

    if not bot:
        return BotStatus(
            online=False, name="Bot", latency="0ms", uptime="0s", guilds=0, users=0
        )

    # Calculate uptime
    uptime = "N/A"
    if hasattr(bot, "start_time") and bot.start_time is not None:
        from datetime import datetime, timezone

        delta = datetime.now(timezone.utc) - bot.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime = f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"

    latency_ms = round(bot.latency * 1000, 2) if bot and bot.latency else 0

    return BotStatus(
        online=bot.is_ready() if bot else False,
        name=bot.user.name if bot and bot.user else "Bot",
        latency=f"{latency_ms}",
        uptime=uptime,
        guilds=len(bot.guilds) if bot else 0,
        users=sum(g.member_count for g in bot.guilds) if bot else 0,
    )


def get_bot_stats() -> BotStats:
    """Get bot statistics"""
    bot = get_bot_instance()

    if not bot or not bot.is_ready():
        return BotStats(channels=0, roles=0, commands=0)

    channels = sum(len(g.channels) for g in bot.guilds)
    roles = sum(len(g.roles) for g in bot.guilds)
    commands = len(bot.commands) + sum(
        len(cog.get_commands()) for cog in bot.cogs.values()
    )

    return BotStats(channels=channels, roles=roles, commands=commands)


def get_database_stats() -> DatabaseStats:
    """Get database statistics"""
    databases = set()
    tables = 0
    total_records = 0

    db_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "databases"
    )

    if not os.path.exists(db_dir):
        return DatabaseStats(databases=0, tables=0, records=0)

    for db_file in os.listdir(db_dir):
        if db_file.endswith(".db"):
            db_name = db_file[:-3]
            databases.add(db_name)

            try:
                conn = get_db_connection(db_name)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_names = cursor.fetchall()
                tables += len(table_names)

                for (table_name,) in table_names:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        total_records += count
                    except Exception:
                        pass

                conn.close()
            except Exception:
                pass

    return DatabaseStats(databases=len(databases), tables=tables, records=total_records)


def get_ticket_stats() -> TicketStats:
    """Get ticket statistics"""
    stats = {"total": 0, "open": 0, "closed": 0}

    try:
        conn = get_db_connection("ticket_system")
        cursor = conn.cursor()

        # Count plex tickets
        cursor.execute("SELECT COUNT(*) FROM plex_ticket_data")
        plex_total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM plex_ticket_data WHERE closed = 0")
        plex_open = cursor.fetchone()[0]

        # Count TV tickets
        cursor.execute("SELECT COUNT(*) FROM tv_ticket_data")
        tv_total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tv_ticket_data WHERE closed = 0")
        tv_open = cursor.fetchone()[0]

        # Combine totals
        stats["total"] = plex_total + tv_total
        stats["open"] = plex_open + tv_open
        stats["closed"] = stats["total"] - stats["open"]

        conn.close()
    except Exception:
        pass

    return TicketStats(**stats)


def get_invite_stats() -> InviteStats:
    """Get invite statistics"""
    stats = {"total": 0, "active": 0, "expired": 0}

    try:
        conn = get_db_connection("invites")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM invites")
        stats["total"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM invites WHERE status = 'active'")
        stats["active"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM invites WHERE status = 'expired'")
        stats["expired"] = cursor.fetchone()[0]
        conn.close()
    except Exception:
        pass

    return InviteStats(**stats)


def get_system_resources() -> SystemResources:
    """Get system resource usage"""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return SystemResources(
        cpu=ResourceItem(percent=cpu_percent, label="CPU"),
        memory=ResourceItem(percent=memory.percent, label="Memory"),
        disk=ResourceItem(percent=disk.percent, label="Disk"),
    )


def get_service_status() -> List[ServiceItem]:
    """Get service status"""
    from config.settings import PLEX_ENABLED, KOFI_ENABLED, WEB_ENABLED

    services = [
        ServiceItem(
            name="Discord Bot",
            status=(
                "running"
                if get_bot_instance() and get_bot_instance().is_ready()
                else "stopped"
            ),
            icon="fa-robot",
        ),
        ServiceItem(
            name="Web Interface",
            status="running" if WEB_ENABLED else "stopped",
            icon="fa-globe",
        ),
        ServiceItem(
            name="Plex Integration",
            status="running" if PLEX_ENABLED else "stopped",
            icon="fa-film",
        ),
        ServiceItem(
            name="Ko-fi Webhook",
            status="running" if KOFI_ENABLED else "stopped",
            icon="fa-coffee",
        ),
    ]

    return services


@router.get("/", response_model=DashboardData)
async def get_dashboard():
    """Get dashboard overview data"""
    try:
        bot_status = get_bot_status()
        bot_stats = get_bot_stats()
        ticket_stats = get_ticket_stats()
        invite_stats = get_invite_stats()
        db_stats = get_database_stats()
        resources = get_system_resources()
        services = get_service_status()
        services_running = sum(1 for s in services if s.status == "running")

        return DashboardData(
            bot_status=bot_status,
            bot_stats=bot_stats,
            ticket_stats=ticket_stats,
            invite_stats=invite_stats,
            db_stats=db_stats,
            resources=resources,
            services=services,
            services_running=services_running,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bot-status", response_model=BotStatus)
async def get_bot_status_endpoint():
    """Get bot status only"""
    return get_bot_status()
