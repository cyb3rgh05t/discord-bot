import discord
from discord.ext import commands
from discord import ui
import sqlite3
import random
import logging
from config.settings import DATABASE_PATH, TICKET_CATEGORY_ID, STAFF_ROLE, LIVE_TICKET
from cogs.helpers.logger import logger


class TicketHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = f"{DATABASE_PATH}/ticket_system.db"
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for ticket system."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table for tickets
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ticket_data (
                guild_id INTEGER,
                member_id INTEGER,
                ticket_id INTEGER,
                channel_id INTEGER,
                closed BOOLEAN,
                locked BOOLEAN,
                claimed BOOLEAN,
                claimed_by INTEGER,
                type TEXT,
                created_by INTEGER,
                opened TIMESTAMP,
                PRIMARY KEY (guild_id, channel_id)
            )
        """
        )
        conn.commit()
        conn.close()

    async def save_ticket(
        self, guild_id, member_id, ticket_id, channel_id, ticket_type
    ):
        """Save ticket information to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ticket_data (guild_id, member_id, ticket_id, channel_id, closed, locked, claimed, claimed_by, type, created_by, opened)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                guild_id,
                member_id,
                ticket_id,
                channel_id,
                False,
                False,
                False,
                None,
                ticket_type,
                member_id,
                int(discord.utils.utcnow().timestamp()),
            ),
        )
        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle button interactions for ticket creation."""
        if interaction.type != discord.InteractionType.component:
            return

        custom_id = interaction.data.get("custom_id")
        if custom_id != "create_ticket":
            return

        guild = interaction.guild
        member = interaction.user
        ticket_name = LIVE_TICKET
        ticket_id = random.randint(10000, 99999)  # Generate random ticket ID

        # Fetch preconfigured category from settings
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)
        if not category:
            await interaction.response.send_message(
                "Ticket category not found. Please contact an administrator.",
                ephemeral=True,
            )
            logger.error("Ticket category not found in the guild.")
            return

        # Create the ticket channel
        # Define permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            ),
            guild.owner: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            ),
        }
        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE)
        # Add staff role to the permissions if it exists
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            )

        # Create the ticket channel
        ticket_channel = await guild.create_text_channel(
            f"{ticket_name}-{ticket_id}",
            category=category,
            overwrites=overwrites,
        )

        # Save ticket data in the database
        await self.save_ticket(guild.id, member.id, ticket_id, ticket_channel.id, "TV")

        # Send a response to the interaction
        await interaction.response.send_message(
            f"{member.mention}, dein Ticket wurde erstellt: {ticket_channel.mention}",
            ephemeral=True,
        )

        # Send a message in the new ticket channel
        embed = discord.Embed(
            title=f"Ticket ID: {ticket_id}",
            description=f"Ticket erstellt von {member.mention}.\n\nBitte warte geduldig auf eine Antwort des Staff Teams. Beschreibe in der Zwischenzeit bitte deine Anfrage oder dein Problem so detailliert wie möglich.",
            color=discord.Color.random(),
        )
        embed.set_footer(text="Buttons sind nur für Staff Team!")

        # Add ticket management buttons
        class TicketButtons(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(
                    discord.ui.Button(
                        label="Save & Close Ticket",
                        custom_id="close",
                        style=discord.ButtonStyle.primary,
                        emoji="💾",
                    )
                )
                self.add_item(
                    discord.ui.Button(
                        label="Lock",
                        custom_id="lock",
                        style=discord.ButtonStyle.secondary,
                        emoji="🔐",
                    )
                )
                self.add_item(
                    ui.Button(
                        label="Unlock",
                        custom_id="unlock",
                        style=discord.ButtonStyle.success,
                        emoji="🔓",
                    )
                )
                self.add_item(
                    ui.Button(
                        label="Claim",
                        custom_id="claim",
                        style=discord.ButtonStyle.primary,
                        emoji="📰",
                    )
                )

        view = TicketButtons()
        await ticket_channel.send(embed=embed, view=view)
        await ticket_channel.send(content=f"{member.mention}, hier ist dein Ticket.")


async def setup(bot):
    await bot.add_cog(TicketHandler(bot))
    logger.debug("TicketHandler cog loaded.")
