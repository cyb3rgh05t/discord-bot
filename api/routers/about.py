"""About page router - version info, system info, bot status"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import platform
import psutil
import os
import requests
from typing import Optional
from datetime import datetime

router = APIRouter(tags=["about"])


class SystemInfo(BaseModel):
    os: str
    os_version: str
    python_version: str
    cpu_count: int
    total_memory: float


class BotStats(BaseModel):
    uptime: str
    latency: str
    guild_count: int
    user_count: int


class BotStatus(BaseModel):
    online: bool


class AboutData(BaseModel):
    version: str
    bot_status: BotStatus
    bot_stats: BotStats
    system_info: SystemInfo


class VersionInfo(BaseModel):
    local: str
    remote: str
    is_update_available: bool
    loading: bool = False
    error: Optional[str] = None


@router.get("/data", response_model=AboutData)
async def get_about_data():
    """Get all about page data"""
    try:
        from api.main import get_bot_instance

        # Get version from file
        version_file = os.path.join(
            os.path.dirname(__file__), "..", "..", "version.txt"
        )
        try:
            with open(version_file, "r") as f:
                version = f.read().strip()
        except:
            version = "unknown"

        # Get system info
        system_info = SystemInfo(
            os=platform.system(),
            os_version=platform.release(),
            python_version=platform.python_version(),
            cpu_count=psutil.cpu_count() or 0,
            total_memory=round(psutil.virtual_memory().total / (1024**3), 2),  # GB
        )

        # Get bot instance
        bot = get_bot_instance()

        # Get bot status
        bot_status = BotStatus(online=bot.is_ready() if bot else False)

        # Get bot stats
        if bot and bot.is_ready():
            # Calculate uptime
            uptime = "0d 0h 0m"
            if hasattr(bot, "start_time") and bot.start_time is not None:
                from datetime import timezone

                delta = datetime.now(timezone.utc) - bot.start_time
                days = delta.days
                hours, remainder = divmod(delta.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime = (
                    f"{days}d {hours}h {minutes}m"
                    if days > 0
                    else f"{hours}h {minutes}m"
                )

            latency_ms = round(bot.latency * 1000, 2) if bot.latency else 0
            guild_count = len(bot.guilds)
            user_count = sum(g.member_count for g in bot.guilds)

            bot_stats = BotStats(
                uptime=uptime,
                latency=f"{latency_ms}",
                guild_count=guild_count,
                user_count=user_count,
            )
        else:
            bot_stats = BotStats(
                uptime="0d 0h 0m",
                latency="0",
                guild_count=0,
                user_count=0,
            )

        return AboutData(
            version=version,
            bot_status=bot_status,
            bot_stats=bot_stats,
            system_info=system_info,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/version", response_model=VersionInfo)
async def get_version():
    """Get version information and check for updates"""
    try:
        # Read current version from version.txt
        version_file = os.path.join(
            os.path.dirname(__file__), "..", "..", "version.txt"
        )
        try:
            with open(version_file, "r") as f:
                local_version = f.read().strip()
        except:
            local_version = "unknown"

        # Fetch latest version from GitHub
        remote_version = local_version
        try:
            response = requests.get(
                "https://api.github.com/repos/cyb3rgh05t/discord-bot/releases/latest",
                timeout=5,
            )
            if response.status_code == 200:
                latest_release = response.json()
                remote_version = latest_release.get("tag_name", "").lstrip("v")
        except Exception:
            pass  # Use local version as fallback

        is_update_available = (
            remote_version != local_version if remote_version else False
        )

        return VersionInfo(
            local=local_version,
            remote=remote_version,
            is_update_available=is_update_available,
            loading=False,
        )
    except Exception as e:
        return VersionInfo(
            local="unknown",
            remote="unknown",
            is_update_available=False,
            loading=False,
            error=str(e),
        )
