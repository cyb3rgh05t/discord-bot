import discord
from discord.ext import commands
import sqlite3
import logging
import asyncio
from discord.utils import get
import chat_exporter
from cogs.helpers.logger import logger


# Database path
DATABASE_PATH = "databases/ticket_system.db"


class TicketOptions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = DATABASE_PATH
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for ticket options."""
        conn = sqlite3.connect(self.db_path)
        conn.commit()
        conn.close()

    async def fetch_ticket_setup(self, guild_id):
        """Fetch ticket setup data for a guild."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT transcripts_id, helpers_role_id FROM ticket_panel WHERE guild_id = ?",
            (guild_id,),
        )
        setup_data = cursor.fetchone()
        conn.close()
        return setup_data

    async def fetch_ticket_data(self, channel_id):
        """Fetch ticket data for a specific channel."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ticket_data WHERE channel_id = ?", (channel_id,))
        ticket_data = cursor.fetchone()
        conn.close()
        return ticket_data

    async def update_ticket_data(self, channel_id, **updates):
        """Update ticket data in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for key, value in updates.items():
            cursor.execute(
                f"UPDATE ticket_data SET {key} = ? WHERE channel_id = ?",
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
        if custom_id not in ["close", "lock", "unlock", "claim"]:
            return

        guild = interaction.guild
        member = interaction.user
        channel = interaction.channel

        # Fetch ticket setup data
        setup_data = await self.fetch_ticket_setup(guild.id)
        if not setup_data:
            await interaction.response.send_message(
                "Ticket setup not found for this guild.",
                ephemeral=True,
            )
            logger.warning(f"Ticket setup not found for guild {guild.name}.")
            return

        transcripts_channel_id, helpers_role_id = setup_data
        handlers_role = get(guild.roles, id=helpers_role_id)

        # Ensure the member has the required role
        if not handlers_role or handlers_role not in member.roles:
            await interaction.response.send_message(
                "Nur für Staff Mitglieder!", ephemeral=True
            )
            logger.warning(f"{member.name} attempted to interact without proper role.")
            return

        # Fetch ticket data
        ticket_data = await self.fetch_ticket_data(channel.id)
        if not ticket_data:
            await interaction.response.send_message(
                "No data found for this ticket. Please delete it manually.",
                ephemeral=True,
            )
            logger.warning(f"No ticket data found for channel {channel.name}.")
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
        if custom_id == "lock":
            if locked:
                await interaction.response.send_message(
                    "Das Ticket ist bereits gesperrt", ephemeral=True
                )
            else:
                await self.update_ticket_data(channel.id, locked=True)
                embed.description = (
                    "🔐 | Dieses Ticket ist jetzt zur Überprüfung gesperrt."
                )
                await channel.set_permissions(member, send_messages=False)
                await interaction.response.send_message(embed=embed)

        elif custom_id == "unlock":
            if not locked:
                await interaction.response.send_message(
                    "Das Ticket ist bereits freigeschaltet", ephemeral=True
                )
            else:
                await self.update_ticket_data(channel.id, locked=False)
                embed.description = "🔓 | Dieses Ticket ist jetzt freigeschaltet."
                await channel.set_permissions(member, send_messages=True)
                await interaction.response.send_message(embed=embed)

        elif custom_id == "close":
            if closed:
                await interaction.response.send_message(
                    "Das Ticket ist bereits geschlossen, bitte warte, bis es gelöscht wird.",
                    ephemeral=True,
                )
            else:
                # Acknowledge the interaction immediately
                await interaction.response.defer(ephemeral=True)
                # Generate transcript using `py-discord-html-transcripts`
                transcript_message = await chat_exporter.quick_export(channel)
                if not transcript_message.attachments:
                    await interaction.followup.send(
                        "Fehler beim Erstellen des Transkripts. Bitte versuche es erneut.",
                        ephemeral=True,
                    )
                    logger.error(
                        f"Transcript creation failed for channel {channel.name}."
                    )
                    return

                # Extract the transcript file
                transcript_file = transcript_message.attachments[0]

                # Fetch the transcripts channel
                transcripts_channel = get(
                    guild.text_channels, id=transcripts_channel_id
                )
                if transcripts_channel:
                    await transcripts_channel.send(
                        embed=discord.Embed(
                            title=f"Ticket ID: {ticket_id}",
                            description=f"Closed By: {member.mention}\nMember: <@{created_by}>",
                            timestamp=discord.utils.utcnow(),
                        ),
                        file=await transcript_file.to_file(),  # Correctly attach the transcript file
                    )

                # Send the transcript as a DM to the ticket creator
                ticket_creator = guild.get_member(created_by)
                if ticket_creator:
                    try:
                        await ticket_creator.send(
                            embed=discord.Embed(
                                title="Ticket Transcript",
                                description=f"Hier ist das Transkript für dein Ticket ID: {ticket_id}.",
                                timestamp=discord.utils.utcnow(),
                            ),
                            file=await transcript_file.to_file(),
                        )
                        logger.info(
                            f"Transcript sent to {ticket_creator.name} for ticket {ticket_id}."
                        )
                    except discord.Forbidden:
                        logger.warning(
                            f"Could not send transcript to {ticket_creator.name} (DMs disabled)."
                        )
                        await transcripts_channel.send(
                            f"{ticket_creator.mention} konnte nicht über DMs erreicht werden. Das Transkript ist hier im Kanal verfügbar."
                        )

            await self.update_ticket_data(channel.id, closed=True)
            embed.description = "Das Ticket wurde erfolgreich geschlossen, wird gelöscht und archiviert."
            await interaction.followup.send(embed=embed)
            await asyncio.sleep(10)
            await channel.delete()
            logger.info(f"Ticket {ticket_id} was deleted.")

        elif custom_id == "claim":
            if claimed:
                await interaction.response.send_message(
                    f"Dieses Ticket wurde bereits von <@{claimed_by}> beansprucht.",
                    ephemeral=True,
                )
            else:
                await self.update_ticket_data(
                    channel.id, claimed=True, claimed_by=member.id
                )
                embed.description = (
                    f"📰 | Dieses Ticket wird jetzt von {member.mention} beansprucht."
                )
                await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(TicketOptions(bot))
    logger.debug("TicketOptions cog loaded.")
