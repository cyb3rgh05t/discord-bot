"""
Interface to interact with the Discord bot instance
Provides read-only access to bot status and information
"""

import psutil
import os
import discord
from datetime import datetime


def get_bot_instance():
    """Get the bot instance from the app context"""
    from web.app import bot_instance

    return bot_instance


def get_bot_status():
    """Get current bot status"""
    bot = get_bot_instance()

    if not bot:
        return {
            "online": False,
            "name": "Bot",
            "latency": 0,
            "uptime": "0s",
            "guilds": 0,
            "users": 0,
        }

    return {
        "online": bot.is_ready() if bot else False,
        "name": bot.user.name if bot and bot.user else "Bot",
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
            "slash_commands": 0,
            "prefix_commands": 0,
            "channels": 0,
            "roles": 0,
        }

    total_channels = sum(len(g.channels) for g in bot.guilds) if bot else 0
    total_roles = sum(len(g.roles) for g in bot.guilds) if bot else 0
    total_users = sum(g.member_count for g in bot.guilds) if bot else 0

    # Count slash commands (app commands)
    slash_commands = 0
    if hasattr(bot, "tree") and bot.tree:
        slash_commands = len(bot.tree.get_commands())

    # Count prefix commands
    prefix_commands = len(bot.commands) if bot else 0

    return {
        "uptime": calculate_uptime(bot),
        "latency": f"{round(bot.latency * 1000, 2)}ms" if bot else "N/A",
        "guild_count": len(bot.guilds) if bot else 0,
        "user_count": total_users,
        "commands": prefix_commands + slash_commands,
        "slash_commands": slash_commands,
        "prefix_commands": prefix_commands,
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


def close_discord_ticket_channel(channel_id):
    """Close a ticket channel in Discord with transcript generation"""
    import asyncio
    import io

    bot = get_bot_instance()

    print(f"[Discord Close] Bot instance: {bot}")
    print(f"[Discord Close] Bot ready: {bot.is_ready() if bot else False}")

    if not bot or not bot.is_ready():
        return {"success": False, "error": "Bot is not ready"}

    try:

        async def close_ticket_with_transcript():
            try:
                import chat_exporter
                import sqlite3
                from discord.utils import get

                channel_id_int = int(channel_id)
                print(f"[Discord Close] Looking for channel {channel_id_int}")
                channel = bot.get_channel(channel_id_int)

                if not channel:
                    return {
                        "success": False,
                        "error": f"Channel {channel_id} not found",
                    }

                print(f"[Discord Close] Found channel: {channel.name}")
                guild = channel.guild

                # Determine ticket type and table prefix
                db_path = "databases/ticket_system.db"
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Try to find ticket in plex tickets
                cursor.execute(
                    "SELECT ticket_id, member_id, type, created_by FROM plex_ticket_data WHERE channel_id = ?",
                    (channel_id_int,),
                )
                ticket_data = cursor.fetchone()
                table_prefix = "plex"

                if not ticket_data:
                    # Try TV tickets
                    cursor.execute(
                        "SELECT ticket_id, member_id, type, created_by FROM tv_ticket_data WHERE channel_id = ?",
                        (channel_id_int,),
                    )
                    ticket_data = cursor.fetchone()
                    table_prefix = "tv"

                if not ticket_data:
                    conn.close()
                    return {
                        "success": False,
                        "error": "Ticket data not found in database",
                    }

                ticket_id, member_id, ticket_type, created_by = ticket_data
                print(
                    f"[Discord Close] Ticket {ticket_id} ({table_prefix}) - Creating transcript..."
                )

                # Get transcript channel
                cursor.execute(
                    f"SELECT transcripts_id FROM {table_prefix}_ticket_panel WHERE guild_id = ?",
                    (guild.id,),
                )
                setup_data = cursor.fetchone()
                conn.close()

                if not setup_data:
                    return {"success": False, "error": "Ticket setup not found"}

                transcripts_channel_id = setup_data[0]

                # Create transcript using chat_exporter
                print(f"[Discord Close] Exporting transcript...")
                transcript = await chat_exporter.export(
                    channel=channel,
                    limit=None,
                    tz_info="Europe/Berlin",
                    guild=guild,
                    bot=bot,
                )

                if not transcript:
                    return {"success": False, "error": "Failed to create transcript"}

                print(f"[Discord Close] Transcript created, counting messages...")

                # Count messages and participants
                message_count = 0
                participants = set()
                async for msg in channel.history(limit=None):
                    message_count += 1
                    if not msg.author.bot:
                        participants.add(msg.author.id)

                print(
                    f"[Discord Close] {message_count} messages, {len(participants)} participants"
                )

                # Create transcript file
                transcript_file = discord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{table_prefix}-{ticket_id}.html",
                )

                # Create transcript embed
                transcript_embed = discord.Embed(
                    title=f"📑 {table_prefix.upper()} Ticket Transcript: #{ticket_id}",
                    description=f"**Ticket Summary**\n"
                    f"Type: `{table_prefix.upper()}-{ticket_type}`\n"
                    f"Created by: <@{created_by}>\n"
                    f"Closed via: `Web Interface`\n"
                    f"Messages: `{message_count}`\n"
                    f"Participants: `{len(participants)}`\n\n"
                    f"The complete transcript is attached as an HTML file.",
                    color=discord.Color.blue(),
                    timestamp=discord.utils.utcnow(),
                )

                # Send to transcript channel
                transcripts_channel = guild.get_channel(transcripts_channel_id)
                if transcripts_channel:
                    print(
                        f"[Discord Close] Sending transcript to channel {transcripts_channel.name}"
                    )
                    await transcripts_channel.send(
                        embed=transcript_embed,
                        file=transcript_file,
                    )
                else:
                    print(
                        f"[Discord Close] Warning: Transcript channel {transcripts_channel_id} not found"
                    )

                # Send to ticket creator
                ticket_creator = guild.get_member(created_by)
                if ticket_creator:
                    try:
                        print(f"[Discord Close] Sending DM to {ticket_creator.name}")
                        dm_transcript_file = discord.File(
                            io.BytesIO(transcript.encode()),
                            filename=f"transcript-{table_prefix}-{ticket_id}.html",
                        )

                        user_embed = discord.Embed(
                            title=f"📑 Dein {table_prefix.upper()} Ticket wurde geschlossen",
                            description=f"**Ticket Details**\n"
                            f"Ticket ID: `{ticket_id}`\n"
                            f"Typ: `{table_prefix.upper()}-{ticket_type}`\n"
                            f"Geschlossen via: `Web Interface`\n"
                            f"Nachrichten: `{message_count}`\n\n"
                            f"Eine vollständige Kopie des Gesprächsverlaufs ist als HTML-Datei angehängt.",
                            color=discord.Color.blue(),
                            timestamp=discord.utils.utcnow(),
                        )

                        if table_prefix == "plex":
                            user_embed.set_thumbnail(
                                url="https://github.com/cyb3rgh05t/brands-logos/blob/master/StreamNet/club/discord/splex.png?raw=true"
                            )
                        else:
                            user_embed.set_thumbnail(
                                url="https://github.com/cyb3rgh05t/brands-logos/blob/master/StreamNet/club/discord/s_tv.png?raw=true"
                            )

                        user_embed.set_footer(
                            text=f"{guild.name} • Support System",
                            icon_url=guild.icon.url if guild.icon else None,
                        )

                        await ticket_creator.send(
                            embed=user_embed,
                            file=dm_transcript_file,
                        )
                        print(f"[Discord Close] DM sent successfully")
                    except discord.Forbidden:
                        print(f"[Discord Close] DMs disabled for {ticket_creator.name}")
                        if transcripts_channel:
                            await transcripts_channel.send(
                                f"{ticket_creator.mention} konnte nicht über DMs erreicht werden."
                            )
                else:
                    print(f"[Discord Close] Ticket creator {created_by} not found")

                # Wait a moment then delete the channel
                print(f"[Discord Close] Waiting 5 seconds before deletion...")
                await asyncio.sleep(5)
                await channel.delete(reason="Ticket closed via web interface")
                print(f"[Discord Close] Channel deleted successfully")

                return {
                    "success": True,
                    "message": f"Ticket {ticket_id} closed with transcript",
                }
            except Exception as e:
                print(f"[Discord Close] Inner exception: {str(e)}")
                import traceback

                traceback.print_exc()
                return {"success": False, "error": str(e)}

        # Run in bot's event loop
        print(f"[Discord Close] Submitting to bot event loop...")
        future = asyncio.run_coroutine_threadsafe(
            close_ticket_with_transcript(), bot.loop
        )
        result = future.result(
            timeout=30
        )  # 30 second timeout for transcript generation
        print(f"[Discord Close] Final result: {result}")

        return result
    except Exception as e:
        print(f"[Discord Close] Outer exception: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}
