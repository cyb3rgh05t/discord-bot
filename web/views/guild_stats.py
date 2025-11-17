"""
Guild Stats view - Display detailed guild statistics
"""

from flask import Blueprint, render_template
from web.utils.decorators import auth_required
from web.utils.bot_interface import get_bot_instance

guild_stats_bp = Blueprint("guild_stats", __name__, url_prefix="/guild-stats")


@guild_stats_bp.route("/")
@auth_required
def index():
    """Guild statistics page"""
    bot = get_bot_instance()

    guild_stats = []

    if bot and bot.guilds:
        for guild in bot.guilds:
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
                {
                    "id": guild.id,
                    "name": guild.name,
                    "icon": str(guild.icon.url) if guild.icon else None,
                    "owner": str(guild.owner) if guild.owner else "Unknown",
                    "owner_id": guild.owner_id,
                    "member_count": guild.member_count,
                    "humans": humans,
                    "bots": bots,
                    "online": online,
                    "idle": idle,
                    "dnd": dnd,
                    "offline": offline,
                    "text_channels": text_channels,
                    "voice_channels": voice_channels,
                    "categories": categories,
                    "total_channels": len(guild.channels),
                    "role_count": len(guild.roles),
                    "emoji_count": len(guild.emojis),
                    "created_at": (
                        guild.created_at.strftime("%Y-%m-%d")
                        if guild.created_at
                        else "Unknown"
                    ),
                    "boost_level": guild.premium_tier,
                    "boost_count": guild.premium_subscription_count or 0,
                    "verification_level": str(guild.verification_level)
                    .replace("_", " ")
                    .title(),
                }
            )

    # Sort by member count
    guild_stats.sort(key=lambda x: x["member_count"], reverse=True)

    # Calculate totals
    totals = {
        "guilds": len(guild_stats),
        "members": sum(g["member_count"] for g in guild_stats),
        "channels": sum(g["total_channels"] for g in guild_stats),
        "roles": sum(g["role_count"] for g in guild_stats),
    }

    return render_template(
        "guild_stats/index.html",
        guilds=guild_stats,
        totals=totals,
    )
