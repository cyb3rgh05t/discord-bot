"""
Guild Stats API Router
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class GuildStat(BaseModel):
    """Guild statistics model"""

    id: str
    name: str
    icon: Optional[str]
    owner: str
    owner_id: str
    member_count: int
    humans: int
    bots: int
    online: int
    idle: int
    dnd: int
    offline: int
    text_channels: int
    voice_channels: int
    categories: int
    total_channels: int
    role_count: int
    emoji_count: int
    created_at: str
    boost_level: int
    boost_count: int
    verification_level: str


class GuildStatsResponse(BaseModel):
    """Guild stats response with totals"""

    guilds: List[GuildStat]
    totals: dict


@router.get("/", response_model=GuildStatsResponse)
async def get_guild_stats():
    """Get detailed statistics for all guilds"""
    from api.main import bot_instance

    if not bot_instance:
        raise HTTPException(status_code=503, detail="Bot is not running")

    guild_stats = []

    for guild in bot_instance.guilds:
        # Count channels by type
        text_channels = len([c for c in guild.text_channels])
        voice_channels = len([c for c in guild.voice_channels])
        categories = len([c for c in guild.categories])

        # Count members by status
        online = len([m for m in guild.members if str(m.status) == "online"])
        idle = len([m for m in guild.members if str(m.status) == "idle"])
        dnd = len([m for m in guild.members if str(m.status) == "dnd"])
        offline = len([m for m in guild.members if str(m.status) == "offline"])

        # Count bots vs humans
        bots = len([m for m in guild.members if m.bot])
        humans = guild.member_count - bots

        guild_stats.append(
            GuildStat(
                id=str(guild.id),
                name=guild.name,
                icon=str(guild.icon.url) if guild.icon else None,
                owner=str(guild.owner) if guild.owner else "Unknown",
                owner_id=str(guild.owner_id),
                member_count=guild.member_count,
                humans=humans,
                bots=bots,
                online=online,
                idle=idle,
                dnd=dnd,
                offline=offline,
                text_channels=text_channels,
                voice_channels=voice_channels,
                categories=categories,
                total_channels=len(guild.channels),
                role_count=len(guild.roles),
                emoji_count=len(guild.emojis),
                created_at=(
                    guild.created_at.strftime("%Y-%m-%d")
                    if guild.created_at
                    else "Unknown"
                ),
                boost_level=guild.premium_tier,
                boost_count=guild.premium_subscription_count or 0,
                verification_level=str(guild.verification_level)
                .replace("_", " ")
                .title(),
            )
        )

    # Sort by member count
    guild_stats.sort(key=lambda x: x.member_count, reverse=True)

    # Calculate totals
    totals = {
        "guilds": len(guild_stats),
        "members": sum(g.member_count for g in guild_stats),
        "channels": sum(g.total_channels for g in guild_stats),
        "roles": sum(g.role_count for g in guild_stats),
    }

    return GuildStatsResponse(guilds=guild_stats, totals=totals)
