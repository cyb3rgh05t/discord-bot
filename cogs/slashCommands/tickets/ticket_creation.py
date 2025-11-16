import discord
from discord.ext import commands
from discord import ui
import sqlite3
import random
import logging
from config.settings import STAFF_ROLE, TICKET_CATEGORY_ID
from cogs.helpers.logger import logger


class TicketCreation(commands.Cog):
    """Handler for ticket creation from button clicks"""

    def __init__(self, bot):
        self.bot = bot
        self.db_path = "databases/ticket_system.db"

    async def fetch_ticket_setup(self, guild_id, table_prefix):
        """Fetch ticket setup data for the guild."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM {table_prefix}_ticket_panel WHERE guild_id = ?", (guild_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result

    async def save_ticket(
        self, guild_id, member_id, ticket_id, channel_id, ticket_type, table_prefix
    ):
        """Save ticket information to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO {table_prefix}_ticket_data (guild_id, member_id, ticket_id, channel_id, closed, locked, claimed, claimed_by, type, created_by, opened)
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
        logger.debug(f"Saved {table_prefix} ticket data for ID {ticket_id}")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle button interactions for ticket creation."""
        if interaction.type != discord.InteractionType.component:
            return

        custom_id = interaction.data.get("custom_id")
        logger.debug(f"Interaction with custom_id: {custom_id}")

        # Handle special case for management buttons
        # These should NOT create new tickets
        if (
            custom_id.startswith("plex_")
            and custom_id[5:] in ["close", "lock", "unlock", "claim"]
        ) or (
            custom_id.startswith("tv_")
            and custom_id[3:] in ["close", "lock", "unlock", "claim"]
        ):
            # This is a management button, not a ticket creation button
            # Skip it - the TicketManagement cog will handle these
            logger.debug(f"Skipping management button: {custom_id}")
            return

        # Handle special case for the Test Line button from lines.py
        if custom_id == "create_ticket":
            # This is the TV test line button
            logger.debug("Processing create_ticket button (test line)")
            table_prefix = "tv"
            ticket_type = "TEST-LINE"

            # Continue with ticket creation using the TV system
            await self.create_ticket(interaction, table_prefix, ticket_type)
            return

        # Skip if not a ticket button
        if not (custom_id.startswith("plex_") or custom_id.startswith("tv_")):
            return

        # Determine which ticket system to use
        if custom_id.startswith("plex_"):
            table_prefix = "plex"
            ticket_type = custom_id[5:]  # Remove "plex_" prefix
            logger.debug(f"Processing Plex ticket creation: {ticket_type}")
        elif custom_id.startswith("tv_"):
            table_prefix = "tv"
            ticket_type = custom_id[3:]  # Remove "tv_" prefix
            logger.debug(f"Processing TV ticket creation: {ticket_type}")
        else:
            return

        # Create the ticket
        await self.create_ticket(interaction, table_prefix, ticket_type)

    async def create_ticket(self, interaction, table_prefix, ticket_type):
        """Create a ticket based on the specified system and type."""
        guild = interaction.guild
        member = interaction.user
        ticket_id = random.randint(10000, 99999)  # Generate random ticket ID

        logger.debug(
            f"Creating {table_prefix} ticket: {ticket_type} with ID {ticket_id}"
        )

        # Fetch ticket panel setup for getting helper roles and transcripts channel
        setup_data = await self.fetch_ticket_setup(guild.id, table_prefix)
        if not setup_data:
            await interaction.response.send_message(
                f"No {table_prefix.capitalize()} ticket setup found. Please run the /{table_prefix}ticketsetup command first.",
                ephemeral=True,
            )
            logger.warning(
                f"No {table_prefix} ticket setup found for guild '{guild.name}'"
            )
            return

        # Extract configuration from database (we only need helpers_role_id and transcripts_id)
        (
            _,
            _,
            _,
            _,
            transcripts_id,
            helpers_role_id,
            everyone_role_id,
            description,
            _,
        ) = setup_data

        # Get the global TICKET_CATEGORY_ID from settings.py - this is where all tickets are created
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not category:
            await interaction.response.send_message(
                f"Ticket category not found (ID: {TICKET_CATEGORY_ID}). Please check your settings.py configuration.",
                ephemeral=True,
            )
            logger.error(
                f"TICKET_CATEGORY_ID {TICKET_CATEGORY_ID} not found in guild '{guild.name}'"
            )
            return

        # Get roles from the database configuration
        helpers_role = guild.get_role(helpers_role_id)
        everyone_role = guild.get_role(everyone_role_id)

        if not (helpers_role and everyone_role):
            await interaction.response.send_message(
                "Required roles not found. Please run the setup command again.",
                ephemeral=True,
            )
            logger.error(f"Missing roles for {table_prefix} ticket creation")
            return

        # Create ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            ),
            helpers_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True,
                manage_messages=True,
            ),
        }

        # Format channel name
        if table_prefix == "plex":
            channel_name = f"plex-{ticket_type}-{ticket_id}"
        else:
            channel_name = f"tv-{ticket_type}-{ticket_id}"

        try:
            # Create the ticket channel
            ticket_channel = await guild.create_text_channel(
                channel_name,
                category=category,
                overwrites=overwrites,
            )

            logger.info(f"Created {table_prefix} ticket channel: {channel_name}")

            # Save ticket data to database
            await self.save_ticket(
                guild.id,
                member.id,
                ticket_id,
                ticket_channel.id,
                ticket_type,
                table_prefix,
            )

            # Create the embed for the ticket channel
            if table_prefix == "plex":
                embed_thumbnail = "https://github.com/cyb3rgh05t/brands-logos/blob/master/StreamNet/club/discord/splex.png?raw=true"
                title = f"{guild.name} | PLEX Ticket ID: {ticket_id}"
            else:
                embed_thumbnail = "https://github.com/cyb3rgh05t/brands-logos/blob/master/StreamNet/club/discord/s_tv.png?raw=true"
                title = f"{guild.name} | TV Ticket ID: {ticket_id}"

            embed = discord.Embed(
                title=title,
                description=f"Ticket erstellt von {member.mention}\n\nBitte warte geduldig auf eine Antwort des Staff Teams. Beschreibe in der Zwischenzeit bitte deine Anfrage oder dein Problem so detailliert wie möglich.",
                color=discord.Color.random(),
            )
            embed.set_thumbnail(url=embed_thumbnail)
            embed.set_footer(text="Buttons sind nur für Staff Team!")

            # Create ticket management buttons
            class TicketButtons(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                    # Use the table_prefix in the custom IDs to differentiate the systems
                    self.add_item(
                        discord.ui.Button(
                            label="Save & Close Ticket",
                            custom_id=f"{table_prefix}_close",
                            style=discord.ButtonStyle.primary,
                            emoji="💾",
                        )
                    )
                    self.add_item(
                        discord.ui.Button(
                            label="Lock",
                            custom_id=f"{table_prefix}_lock",
                            style=discord.ButtonStyle.secondary,
                            emoji="🔐",
                        )
                    )
                    self.add_item(
                        discord.ui.Button(
                            label="Unlock",
                            custom_id=f"{table_prefix}_unlock",
                            style=discord.ButtonStyle.success,
                            emoji="🔓",
                        )
                    )
                    self.add_item(
                        discord.ui.Button(
                            label="Claim",
                            custom_id=f"{table_prefix}_claim",
                            style=discord.ButtonStyle.primary,
                            emoji="📰",
                        )
                    )

            # Send messages in the new channel
            view = TicketButtons()
            await ticket_channel.send(embed=embed, view=view)
            await ticket_channel.send(
                content=f"{member.mention}, hier ist dein Ticket."
            )

            # Respond to the interaction
            await interaction.response.send_message(
                content=f"{member.mention}, dein {table_prefix.upper()} Ticket wurde erstellt: {ticket_channel.mention}",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(f"Error creating ticket channel: {e}")
            await interaction.response.send_message(
                f"Error creating ticket: {e}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(TicketCreation(bot))
    logger.debug("TicketCreation cog loaded.")
