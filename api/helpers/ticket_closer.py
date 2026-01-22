"""
Helper module for closing tickets with full transcript generation
"""

import sqlite3
import asyncio
import discord
import chat_exporter
import io
from typing import Dict, Any


async def close_ticket_with_transcript(
    ticket_id: int, db_path: str, bot_instance, closed_by_username: str
) -> Dict[str, Any]:
    """
    Close a ticket with full transcript creation, matching Discord behavior

    Args:
        ticket_id: The ticket ID to close
        db_path: Path to the tickets database
        bot_instance: The Discord bot instance
        closed_by_username: Username of who closed the ticket (for logging)

    Returns:
        Dict with success status and message
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get ticket data from plex first
        cursor.execute(
            """SELECT guild_id, member_id, ticket_id, channel_id, closed, locked, 
                      claimed, claimed_by, type, created_by, opened 
               FROM plex_ticket_data WHERE ticket_id = ?""",
            (ticket_id,),
        )
        result = cursor.fetchone()
        table_prefix = "plex"

        if not result:
            # Try TV tickets
            cursor.execute(
                """SELECT guild_id, member_id, ticket_id, channel_id, closed, locked, 
                          claimed, claimed_by, type, created_by, opened 
                   FROM tv_ticket_data WHERE ticket_id = ?""",
                (ticket_id,),
            )
            result = cursor.fetchone()
            table_prefix = "tv"

        if not result:
            conn.close()
            return {"success": False, "message": "Ticket not found"}

        (
            guild_id,
            member_id,
            _ticket_id,
            channel_id,
            closed,
            locked,
            claimed,
            claimed_by,
            ticket_type,
            created_by,
            opened,
        ) = result

        if closed:
            conn.close()
            return {"success": False, "message": "Ticket is already closed"}

        conn.close()

        # Get channel and guild
        channel = bot_instance.get_channel(int(channel_id))
        guild = bot_instance.get_guild(int(guild_id))

        if not channel or not guild:
            return {"success": False, "message": "Channel or guild not found"}

        # Get transcripts channel ID from setup
        setup_conn = sqlite3.connect(db_path)
        setup_cursor = setup_conn.cursor()
        setup_cursor.execute(
            f"SELECT transcripts_id FROM {table_prefix}_ticket_panel WHERE guild_id = ?",
            (guild_id,),
        )
        setup_result = setup_cursor.fetchone()
        setup_conn.close()

        if not setup_result:
            # Just close without transcript if setup not found
            await channel.delete(reason="Ticket closed via web UI")
            return {
                "success": True,
                "message": "Ticket closed (no transcript - setup not found)",
            }

        transcripts_channel_id = setup_result[0]

        # Create transcript using chat_exporter
        print(f"[DEBUG] Creating transcript for ticket {ticket_id}")
        transcript = await chat_exporter.export(
            channel,
            limit=None,
            tz_info="UTC",
            military_time=False,
            bot=bot_instance,
        )

        if transcript is None:
            print(f"[WARNING] Transcript creation failed for ticket {ticket_id}")
            # Close without transcript if creation failed
            await channel.delete(reason="Ticket closed via web UI")
            return {
                "success": True,
                "message": "Ticket closed (transcript creation failed)",
            }

        # Count messages and participants
        messages = [message async for message in channel.history(limit=None)]
        message_count = len(messages)
        participants = set(msg.author.id for msg in messages if not msg.author.bot)

        print(
            f"[DEBUG] Transcript created: {message_count} messages, {len(participants)} participants"
        )

        # Create transcript file
        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{table_prefix}-{ticket_id}.html",
        )

        # Create transcript embed
        transcript_embed = discord.Embed(
            title=f"📑 {table_prefix.upper()} Ticket Transcript: #{ticket_id}",
            description=f"**Ticket Information**\n"
            f"Ticket ID: `{ticket_id}`\n"
            f"Type: `{table_prefix.upper()}-{ticket_type}`\n"
            f"Closed by: Web UI ({closed_by_username})\n"
            f"Messages: `{message_count}`\n"
            f"Participants: `{len(participants)}`\n\n"
            f"The complete transcript is attached as an HTML file which can be downloaded and opened in any browser.",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )

        # Add thumbnail
        if table_prefix == "plex":
            transcript_embed.set_thumbnail(
                url="https://github.com/cyb3rgh05t/brands-logos/blob/master/StreamNet/club/discord/splex.png?raw=true"
            )
        else:
            transcript_embed.set_thumbnail(
                url="https://github.com/cyb3rgh05t/brands-logos/blob/master/StreamNet/club/discord/s_tv.png?raw=true"
            )

        transcript_embed.set_footer(
            text=f"{guild.name} • Support System",
            icon_url=guild.icon.url if guild.icon else None,
        )

        # Send to transcripts channel
        transcripts_channel = guild.get_channel(transcripts_channel_id)
        if transcripts_channel:
            try:
                await transcripts_channel.send(
                    embed=transcript_embed,
                    file=transcript_file,
                )
                print(f"[INFO] Transcript sent to channel {transcripts_channel.name}")
            except Exception as e:
                print(f"[ERROR] Failed to send transcript to channel: {e}")

        # Send to ticket creator via DM
        ticket_creator = guild.get_member(created_by)
        if ticket_creator:
            try:
                dm_transcript_file = discord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{table_prefix}-{ticket_id}.html",
                )

                user_embed = discord.Embed(
                    title=f"📑 Dein {table_prefix.upper()} Ticket wurde geschlossen",
                    description=f"**Ticket Details**\n"
                    f"Ticket ID: `{ticket_id}`\n"
                    f"Typ: `{table_prefix.upper()}-{ticket_type}`\n"
                    f"Geschlossen von: Web UI\n"
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
                print(f"[INFO] Transcript sent to {ticket_creator.name} via DM")
            except discord.Forbidden:
                # User has DMs disabled
                print(
                    f"[WARNING] Could not send transcript to {ticket_creator.name} (DMs disabled)"
                )
                if transcripts_channel:
                    await transcripts_channel.send(
                        f"{ticket_creator.mention} konnte nicht über DMs erreicht werden."
                    )

        # Mark as closed in database
        db_conn = sqlite3.connect(db_path)
        db_cursor = db_conn.cursor()
        db_cursor.execute(
            f"UPDATE {table_prefix}_ticket_data SET closed = 1 WHERE ticket_id = ?",
            (ticket_id,),
        )
        db_conn.commit()
        db_conn.close()

        print(f"[INFO] Ticket {ticket_id} marked as closed in database")

        # Delete the channel after a brief delay
        await asyncio.sleep(3)
        await channel.delete(reason=f"Ticket {ticket_id} closed via web UI")

        print(f"[INFO] Channel {channel.name} deleted")

        return {
            "success": True,
            "message": "Ticket closed successfully with transcript",
        }

    except Exception as e:
        print(f"[ERROR] Error in close_ticket_with_transcript: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "message": f"Error: {str(e)}"}
