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


def get_guild_members():
    """Get list of all guild members with their roles"""
    bot = get_bot_instance()

    if not bot or not bot.is_ready():
        return []

    try:
        from config.settings import GUILD_ID
        from flask import current_app

        guild = bot.get_guild(int(GUILD_ID))
        if not guild:
            return []

        members = []
        for member in guild.members:
            # Skip bots
            if member.bot:
                continue

            # Get member status
            status = str(member.status)

            # Get member roles (excluding @everyone)
            roles = []
            for role in member.roles:
                if role.name != "@everyone":
                    roles.append(
                        {
                            "id": role.id,
                            "name": role.name,
                            "color": (
                                f"#{role.color.value:06x}"
                                if role.color.value
                                else "#99aab5"
                            ),
                        }
                    )

            members.append(
                {
                    "id": member.id,
                    "name": str(member),
                    "display_name": member.display_name,
                    "avatar": (
                        str(member.display_avatar.url)
                        if member.display_avatar
                        else None
                    ),
                    "status": status,
                    "roles": roles,
                }
            )

        return members
    except Exception as e:
        print(f"Error getting guild members: {e}")
        return []


def get_guild_roles():
    """Get list of all guild roles"""
    bot = get_bot_instance()

    if not bot or not bot.is_ready():
        return []

    try:
        from config.settings import GUILD_ID

        guild = bot.get_guild(int(GUILD_ID))
        if not guild:
            return []

        roles = []
        for role in guild.roles:
            # Skip @everyone role
            if role.name == "@everyone":
                continue

            # Count members with this role
            member_count = sum(1 for member in guild.members if role in member.roles)

            roles.append(
                {
                    "id": role.id,
                    "name": role.name,
                    "color": (
                        f"#{role.color.value:06x}" if role.color.value else "#99aab5"
                    ),
                    "position": role.position,
                    "mentionable": role.mentionable,
                    "hoist": role.hoist,
                    "member_count": member_count,
                }
            )

        # Sort by position (highest first)
        roles.sort(key=lambda x: x["position"], reverse=True)

        return roles
    except Exception as e:
        print(f"Error getting guild roles: {e}")
        return []


def add_role_to_member(user_id, role_id):
    """Add a role to a guild member"""
    bot = get_bot_instance()

    if not bot or not bot.is_ready():
        return {"success": False, "error": "Bot is not ready"}

    try:
        from config.settings import GUILD_ID
        import asyncio

        guild = bot.get_guild(int(GUILD_ID))
        if not guild:
            return {"success": False, "error": "Guild not found"}

        role = guild.get_role(role_id)
        if not role:
            return {"success": False, "error": "Role not found"}

        # Fetch member asynchronously (not from cache)
        async def add_role_async():
            from web.utils.logging_helper import log_debug

            try:
                log_debug(f"Fetching member {user_id} from guild {guild.name}")
                member = await guild.fetch_member(user_id)
                log_debug(f"Found member: {member}")

                if not member:
                    return {"success": False, "error": "Member not found"}

                # Check if member already has the role
                if role in member.roles:
                    return {"success": False, "error": "Member already has this role"}

                # Add the role
                await member.add_roles(role)
                return {
                    "success": True,
                    "message": f"Added {role.name} to {member.name}",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Run in bot's event loop
        future = asyncio.run_coroutine_threadsafe(add_role_async(), bot.loop)
        result = future.result(timeout=10)  # 10 second timeout

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def remove_role_from_member(user_id, role_id):
    """Remove a role from a guild member"""
    bot = get_bot_instance()

    if not bot or not bot.is_ready():
        return {"success": False, "error": "Bot is not ready"}

    try:
        from config.settings import GUILD_ID
        import asyncio
        from flask import current_app

        guild = bot.get_guild(int(GUILD_ID))
        if not guild:
            return {"success": False, "error": "Guild not found"}

        role = guild.get_role(role_id)
        if not role:
            return {"success": False, "error": "Role not found"}

        # Fetch member asynchronously (not from cache)
        async def remove_role_async():
            from config.settings import WEB_VERBOSE_LOGGING

            try:
                if WEB_VERBOSE_LOGGING:
                    current_app.logger.debug(
                        f"Fetching member {user_id} from guild {guild.id}"
                    )
                member = await guild.fetch_member(user_id)
                if WEB_VERBOSE_LOGGING:
                    current_app.logger.debug(f"Successfully fetched member: {member}")
                if not member:
                    return {"success": False, "error": "Member not found"}

                # Check if member does not have the role
                if role not in member.roles:
                    return {"success": False, "error": "Member does not have this role"}

                # Remove the role
                await member.remove_roles(role)
                return {
                    "success": True,
                    "message": f"Removed {role.name} from {member.name}",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Run in bot's event loop
        future = asyncio.run_coroutine_threadsafe(remove_role_async(), bot.loop)
        result = future.result(timeout=10)  # 10 second timeout

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
