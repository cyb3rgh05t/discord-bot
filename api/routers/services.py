"""Services endpoints"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
import psutil
import os
from api.routers.auth import get_current_user, User
from api.main import get_bot_instance

router = APIRouter()


class ServiceStatus(BaseModel):
    name: str
    status: str
    icon: str
    uptime: str


class SystemResources(BaseModel):
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]


class ServicesData(BaseModel):
    services: List[ServiceStatus]
    resources: SystemResources


def get_service_status() -> List[ServiceStatus]:
    """Get status of various services"""
    services = []
    bot = get_bot_instance()

    # Discord Bot
    bot_uptime = "N/A"
    if bot and hasattr(bot, "start_time"):
        from datetime import datetime

        delta = datetime.utcnow() - bot.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        bot_uptime = (
            f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"
        )

    services.append(
        ServiceStatus(
            name="Discord Bot",
            status="running" if bot and bot.is_ready() else "stopped",
            icon="fa-robot",
            uptime=bot_uptime,
        )
    )

    # Database
    services.append(
        ServiceStatus(
            name="Database",
            status="running" if os.path.exists("databases") else "stopped",
            icon="fa-database",
            uptime="N/A",
        )
    )

    # Plex Integration
    try:
        from config.settings import PLEX_ENABLED

        plex_status = "running" if PLEX_ENABLED else "disabled"
    except:
        plex_status = "disabled"

    services.append(
        ServiceStatus(
            name="Plex Integration", status=plex_status, icon="fa-film", uptime="N/A"
        )
    )

    # Ko-fi Webhook
    try:
        from config.settings import KOFI_ENABLED

        kofi_status = "running" if KOFI_ENABLED else "disabled"
    except:
        kofi_status = "disabled"

    services.append(
        ServiceStatus(
            name="Ko-fi Webhook", status=kofi_status, icon="fa-coffee", uptime="N/A"
        )
    )

    return services


def get_system_resources() -> SystemResources:
    """Get system resource usage"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return SystemResources(
        cpu={"percent": cpu_percent, "cores": psutil.cpu_count()},
        memory={
            "percent": memory.percent,
            "used": memory.used / (1024**3),  # GB
            "total": memory.total / (1024**3),  # GB
        },
        disk={
            "percent": disk.percent,
            "used": disk.used / (1024**3),  # GB
            "total": disk.total / (1024**3),  # GB
        },
    )


@router.get("/", response_model=ServicesData)
async def get_services():
    """Get service statuses and system resources"""
    return ServicesData(services=get_service_status(), resources=get_system_resources())
