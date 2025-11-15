"""
Interface to interact with the Discord bot instance
Provides read-only access to bot status and information
"""

import psutil
import os
from datetime import datetime


def get_bot_instance():
    """Get the bot instance from the app context"""
    from web.app import bot_instance

    return bot_instance


def get_bot_status():
    """Get current bot status"""
    bot = get_bot_instance()

    if not bot:
        return {"online": False, "latency": 0, "uptime": "0s", "guilds": 0, "users": 0}

    return {
        "online": bot.is_ready() if bot else False,
        "latency": round(bot.latency * 1000, 2) if bot else 0,
        "uptime": calculate_uptime(bot),
        "guilds": len(bot.guilds) if bot else 0,
        "users": sum(g.member_count for g in bot.guilds) if bot else 0,
    }


def get_bot_stats():
    """Get bot statistics"""
    bot = get_bot_instance()

    if not bot:
        return {
            "uptime": "N/A",
            "latency": "N/A",
            "guild_count": 0,
            "user_count": 0,
            "commands": 0,
            "channels": 0,
            "roles": 0,
        }

    total_channels = sum(len(g.channels) for g in bot.guilds) if bot else 0
    total_roles = sum(len(g.roles) for g in bot.guilds) if bot else 0
    total_users = sum(g.member_count for g in bot.guilds) if bot else 0

    return {
        "uptime": calculate_uptime(bot),
        "latency": f"{round(bot.latency * 1000, 2)}ms" if bot else "N/A",
        "guild_count": len(bot.guilds) if bot else 0,
        "user_count": total_users,
        "commands": len(bot.commands) if bot else 0,
        "channels": total_channels,
        "roles": total_roles,
    }


def calculate_uptime(bot):
    """Calculate bot uptime"""
    if not bot or not hasattr(bot, "start_time") or bot.start_time is None:
        return "N/A"

    uptime_delta = datetime.now() - bot.start_time

    days = uptime_delta.days
    hours, remainder = divmod(uptime_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def get_discord_username(user_id):
    """Get Discord username from user ID"""
    bot = get_bot_instance()

    if not bot or not bot.is_ready():
        return None

    try:
        user_id = int(user_id)
        # Try to get user from cache first
        user = bot.get_user(user_id)
        if user:
            return str(
                user
            )  # Returns "username#discriminator" or "username" for new format

        # If not in cache, try fetching (this is async, so we can't do it here)
        return None
    except (ValueError, AttributeError):
        return None


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
