"""
Service monitoring utilities
Monitor bot health, system resources, and services
"""

import psutil
import os
from datetime import datetime


def get_service_status():
    """Get status of various services"""
    services = []

    # Discord Bot
    services.append(
        {
            "name": "Discord Bot",
            "status": "running",  # Will be dynamic based on bot status
            "icon": "fa-robot",
            "uptime": get_bot_uptime(),
        }
    )

    # Database
    services.append(
        {
            "name": "Database",
            "status": "running" if check_database() else "stopped",
            "icon": "fa-database",
            "uptime": "N/A",
        }
    )

    # Plex Integration
    services.append(
        {
            "name": "Plex Integration",
            "status": "running" if check_plex() else "disabled",
            "icon": "fa-film",
            "uptime": "N/A",
        }
    )

    # Ko-fi Webhook
    services.append(
        {
            "name": "Ko-fi Webhook",
            "status": "running" if check_kofi() else "disabled",
            "icon": "fa-coffee",
            "uptime": "N/A",
        }
    )

    return services


def get_system_resources():
    """Get system resource usage"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu": {"percent": cpu_percent, "cores": psutil.cpu_count()},
        "memory": {
            "percent": memory.percent,
            "used": memory.used / (1024**3),  # GB
            "total": memory.total / (1024**3),  # GB
        },
        "disk": {
            "percent": disk.percent,
            "used": disk.used / (1024**3),  # GB
            "total": disk.total / (1024**3),  # GB
        },
    }


def get_bot_uptime():
    """Get bot uptime"""
    # Placeholder - will need to track start time
    return "N/A"


def check_database():
    """Check if database is accessible"""
    try:
        from config.settings import DATABASE_PATH

        return os.path.exists(DATABASE_PATH)
    except:
        return False


def check_plex():
    """Check if Plex integration is enabled"""
    try:
        from config.settings import PLEX_ENABLED

        return PLEX_ENABLED
    except:
        return False


def check_kofi():
    """Check if Ko-fi webhook is configured"""
    try:
        from config.settings import KOFI_VERIFICATION_TOKEN

        return bool(KOFI_VERIFICATION_TOKEN)
    except:
        return False


def restart_bot():
    """Restart the bot (placeholder)"""
    # This would need to be implemented based on your deployment
    # Could use systemd, docker restart, or process management
    raise NotImplementedError("Bot restart not implemented yet")
