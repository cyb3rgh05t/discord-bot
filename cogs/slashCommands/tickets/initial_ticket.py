import discord
from discord.ext import commands
from discord import ui
import sqlite3
import random
import logging
from config.settings import DATABASE_PATH, TICKET_CATEGORY_ID, STAFF_ROLE
from cogs.helpers.logger import logger


class TicketInteraction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = f"{DATABASE_PATH}/ticket_system.db"
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for ticket system."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table for individual tickets
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

    async def fetch_ticket_setup(self, guild_id):
        """Fetch ticket setup data for the guild."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ticket_panel WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        conn.close()
        return result

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
                member_id,
                ticket_type,
                member_id,
                int(discord.utils.utcnow().timestamp()),
            ),
        )
        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle button interactions."""
        if not interaction.data.get("custom_id"):
            return

        guild = interaction.guild
        member = interaction.user
        custom_id = interaction.data["custom_id"]

        # Fetch ticket panel setup
        setup_data = await self.fetch_ticket_setup(guild.id)
        if not setup_data:
            logger.warning(
                f"Ticket setup data not found for guild '{guild.name}' (ID: {guild.id})."
            )
            return

        (
            _,
            channel_id,
            _,
            category_id,
            transcripts_id,
            helpers_role_id,
            everyone_role_id,
            description,
            buttons,
        ) = setup_data
        buttons_list = buttons.split(",")

        if custom_id not in buttons_list:
            return  # Ignore unrelated buttons

        ticket_id = random.randint(10000, 99999)  # Generate a random ticket ID
        category = guild.get_channel(category_id)
        handlers_role = guild.get_role(helpers_role_id)
        everyone_role = guild.get_role(everyone_role_id)

        if not category or not handlers_role or not everyone_role:
            logger.error(
                f"One or more required entities (category/roles) are missing for ticket creation in guild '{guild.name}'."
            )
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

        ticket_channel = await guild.create_text_channel(
            f"{custom_id}-{ticket_id}",
            category=category,
            overwrites=overwrites,
        )

        # Save ticket data
        await self.save_ticket(
            guild.id, member.id, ticket_id, ticket_channel.id, custom_id
        )

        # Create the embed
        embed = discord.Embed(
            title=f"{guild.name} | Ticket ID: {ticket_id}",
            description=f"Ticket erstellt von {member.mention}\n\nBitte warte geduldig auf eine Antwort des Staff Teams. Beschreibe in der Zwischenzeit bitte deine Anfrage oder dein Problem so detailliert wie möglich.",
            color=discord.Color.random(),
        )
        embed.set_footer(text="Buttons sind nur für Staff Team!")

        # Create buttons for ticket management
        class TicketButtons(ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(
                    ui.Button(
                        label="Save & Close Ticket",
                        custom_id="close",
                        style=discord.ButtonStyle.primary,
                        emoji="💾",
                    )
                )
                self.add_item(
                    ui.Button(
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

        # Send messages in the new channel
        view = TicketButtons()
        await ticket_channel.send(embed=embed, view=view)
        await ticket_channel.send(content=f"{member.mention}, hier ist dein Ticket.")

        # Respond to the interaction
        await interaction.response.send_message(
            content=f"{member.mention}, dein Ticket wurde erstellt: {ticket_channel.mention}",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(TicketInteraction(bot))
    logger.debug("TicketInteraction cog loaded.")
