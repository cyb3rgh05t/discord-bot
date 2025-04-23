import discord
from discord.ext import commands
import sqlite3
import logging
import asyncio
import io
from discord.utils import get
import chat_exporter
from config.settings import DATABASE_PATH
from cogs.helpers.logger import logger


class TicketManagement(commands.Cog):
    """Handler for ticket management buttons"""

    def __init__(self, bot):
        self.bot = bot
        self.db_path = f"{DATABASE_PATH}/ticket_system.db"

    async def fetch_ticket_setup(self, guild_id, table_prefix):
        """Fetch ticket setup data for a guild."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT transcripts_id, helpers_role_id FROM {table_prefix}_ticket_panel WHERE guild_id = ?",
            (guild_id,),
        )
        setup_data = cursor.fetchone()
        conn.close()
        return setup_data

    async def fetch_ticket_data(self, channel_id, table_prefix):
        """Fetch ticket data for a specific channel."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM {table_prefix}_ticket_data WHERE channel_id = ?",
            (channel_id,),
        )
        ticket_data = cursor.fetchone()
        conn.close()
        return ticket_data

    async def update_ticket_data(self, channel_id, table_prefix, **updates):
        """Update ticket data in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for key, value in updates.items():
            cursor.execute(
                f"UPDATE {table_prefix}_ticket_data SET {key} = ? WHERE channel_id = ?",
                (value, channel_id),
            )
        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle ticket-related button interactions."""
        if (
            not interaction.data.get("component_type") == 2
        ):  # Component type 2 is for buttons
            return

        custom_id = interaction.data.get("custom_id")
        logger.debug(f"Ticket management button clicked: {custom_id}")

        # Check if this is a management button
        if not (custom_id.startswith("plex_") or custom_id.startswith("tv_")):
            return

        # Parse the table prefix and action
        if custom_id.startswith("plex_"):
            table_prefix = "plex"
            action = custom_id[5:]  # Remove "plex_" prefix
        elif custom_id.startswith("tv_"):
            table_prefix = "tv"
            action = custom_id[3:]  # Remove "tv_" prefix
        else:
            return

        # Check if this is a management action (not a ticket creation button)
        if action not in ["close", "lock", "unlock", "claim"]:
            # Not a management action, ignore
            logger.debug(f"Not a management action: {action} - skipping")
            return

        guild = interaction.guild
        member = interaction.user
        channel = interaction.channel

        # Fetch ticket setup data
        setup_data = await self.fetch_ticket_setup(guild.id, table_prefix)
        if not setup_data:
            await interaction.response.send_message(
                f"{table_prefix.capitalize()} ticket setup not found for this guild.",
                ephemeral=True,
            )
            logger.warning(
                f"{table_prefix.capitalize()} ticket setup not found for guild {guild.name}."
            )
            return

        transcripts_channel_id, helpers_role_id = setup_data
        handlers_role = get(guild.roles, id=helpers_role_id)

        # Ensure the member has the required role
        if not handlers_role or handlers_role not in member.roles:
            await interaction.response.send_message(
                "Nur für Staff Mitglieder!", ephemeral=True
            )
            logger.warning(
                f"{member.name} attempted to interact with {table_prefix} ticket without proper role."
            )
            return

        # Fetch ticket data
        ticket_data = await self.fetch_ticket_data(channel.id, table_prefix)
        if not ticket_data:
            await interaction.response.send_message(
                f"No data found for this {table_prefix} ticket. Please delete it manually.",
                ephemeral=True,
            )
            logger.warning(
                f"No {table_prefix} ticket data found for channel {channel.name}."
            )
            return

        (
            guild_id,
            member_id,
            ticket_id,
            channel_id,
            closed,
            locked,
            claimed,
            claimed_by,
            ticket_type,
            created_by,
            opened,
        ) = ticket_data

        embed = discord.Embed(color=discord.Color.blue())

        if action == "lock":
            if locked:
                await interaction.response.send_message(
                    "Das Ticket ist bereits gesperrt", ephemeral=True
                )
            else:
                await self.update_ticket_data(channel.id, table_prefix, locked=True)
                embed.description = (
                    "🔐 | Dieses Ticket ist jetzt zur Überprüfung gesperrt."
                )

                # Get the ticket creator
                creator = guild.get_member(created_by)
                if creator:
                    await channel.set_permissions(creator, send_messages=False)

                await interaction.response.send_message(embed=embed)
                logger.info(f"Ticket {ticket_id} locked by {member.name}")

        elif action == "unlock":
            if not locked:
                await interaction.response.send_message(
                    "Das Ticket ist bereits freigeschaltet", ephemeral=True
                )
            else:
                await self.update_ticket_data(channel.id, table_prefix, locked=False)
                embed.description = "🔓 | Dieses Ticket ist jetzt freigeschaltet."

                # Get the ticket creator
                creator = guild.get_member(created_by)
                if creator:
                    await channel.set_permissions(creator, send_messages=True)

                await interaction.response.send_message(embed=embed)
                logger.info(f"Ticket {ticket_id} unlocked by {member.name}")

        elif action == "close":
            if closed:
                await interaction.response.send_message(
                    "Das Ticket ist bereits geschlossen, bitte warte, bis es gelöscht wird.",
                    ephemeral=True,
                )
            else:
                # Acknowledge the interaction immediately
                await interaction.response.defer(ephemeral=True)
                logger.debug(f"Starting close process for ticket {ticket_id}")

                # Import missing io module

                # Generate transcript using `py-discord-html-transcripts`
                try:
                    transcript = await chat_exporter.export(
                        channel=channel,
                        limit=None,
                        tz_info="Europe/Berlin",
                        guild=guild,
                        bot=self.bot,
                    )

                    if transcript is None:
                        await interaction.followup.send(
                            "Fehler beim Erstellen des Transkripts. Bitte versuche es erneut.",
                            ephemeral=True,
                        )
                        logger.error(
                            f"Transcript creation failed for {table_prefix} channel {channel.name}."
                        )
                        return

                    # Save transcript to file
                    transcript_file = discord.File(
                        io.BytesIO(transcript.encode()),
                        filename=f"transcript-{table_prefix}-{ticket_id}.html",
                    )

                    # Fetch the transcripts channel
                    transcripts_channel = guild.get_channel(transcripts_channel_id)
                    if transcripts_channel:
                        try:
                            await transcripts_channel.send(
                                embed=discord.Embed(
                                    title=f"{table_prefix.upper()} Ticket ID: {ticket_id}",
                                    description=f"Closed By: {member.mention}\nMember: <@{created_by}>",
                                    timestamp=discord.utils.utcnow(),
                                ),
                                file=transcript_file,
                            )
                            logger.info(
                                f"Transcript saved to channel {transcripts_channel.name}"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send transcript to channel: {e}")
                            await interaction.followup.send(
                                f"Failed to save transcript to channel: {e}",
                                ephemeral=True,
                            )
                    else:
                        logger.error(
                            f"Transcript channel {transcripts_channel_id} not found!"
                        )

                    # Send the transcript as a DM to the ticket creator
                    ticket_creator = guild.get_member(created_by)
                    if ticket_creator:
                        try:
                            # Create a new file object for DM since the first one is consumed
                            dm_transcript_file = discord.File(
                                io.BytesIO(transcript.encode()),
                                filename=f"transcript-{table_prefix}-{ticket_id}.html",
                            )

                            await ticket_creator.send(
                                embed=discord.Embed(
                                    title=f"{table_prefix.upper()} Ticket Transcript",
                                    description=f"Hier ist das Transkript für dein {table_prefix.upper()} Ticket ID: {ticket_id}.",
                                    timestamp=discord.utils.utcnow(),
                                ),
                                file=dm_transcript_file,
                            )
                            logger.info(
                                f"Transcript sent to {ticket_creator.name} for {table_prefix} ticket {ticket_id}."
                            )
                        except discord.Forbidden:
                            logger.warning(
                                f"Could not send transcript to {ticket_creator.name} (DMs disabled)."
                            )
                            if transcripts_channel:
                                await transcripts_channel.send(
                                    f"{ticket_creator.mention} konnte nicht über DMs erreicht werden. Das Transkript ist hier im Kanal verfügbar."
                                )
                except Exception as e:
                    logger.error(f"Error creating or sending transcript: {e}")
                    await interaction.followup.send(
                        f"Error creating transcript: {e}", ephemeral=True
                    )
                    return

                # Mark ticket as closed in database
                await self.update_ticket_data(channel.id, table_prefix, closed=True)

                # Send response and close the ticket
                embed.description = "Das Ticket wurde erfolgreich geschlossen, wird gelöscht und archiviert."
                await interaction.followup.send(embed=embed)

                # Wait a bit before deleting to let users see the message
                await asyncio.sleep(10)

                try:
                    await channel.delete(
                        reason=f"Ticket {ticket_id} closed by {member.name}"
                    )
                    logger.info(
                        f"{table_prefix.upper()} Ticket {ticket_id} was deleted."
                    )
                except Exception as e:
                    logger.error(f"Failed to delete ticket channel: {e}")
                    await interaction.followup.send(
                        f"Failed to delete ticket channel: {e}", ephemeral=True
                    )

        elif action == "claim":
            if claimed:
                await interaction.response.send_message(
                    f"Dieses Ticket wurde bereits von <@{claimed_by}> beansprucht.",
                    ephemeral=True,
                )
            else:
                await self.update_ticket_data(
                    channel.id, table_prefix, claimed=True, claimed_by=member.id
                )
                embed.description = (
                    f"📰 | Dieses Ticket wird jetzt von {member.mention} beansprucht."
                )
                await interaction.response.send_message(embed=embed)
                logger.info(f"Ticket {ticket_id} claimed by {member.name}")


async def setup(bot):
    await bot.add_cog(TicketManagement(bot))
    logger.debug("TicketManagement cog loaded.")
