import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import logging
from config.settings import GUILD_ID


class TicketSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "databases/ticket_system.db"
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database for ticket panels."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ticket_panel (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                message_id INTEGER,
                category_id INTEGER,
                transcripts_id INTEGER,
                helpers_role_id INTEGER,
                everyone_role_id INTEGER,
                description TEXT,
                buttons TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def save_ticket_panel(
        self,
        guild_id,
        channel_id,
        message_id,
        category_id,
        transcripts_id,
        helpers_role_id,
        everyone_role_id,
        description,
        buttons,
    ):
        """Save or update ticket panel details in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ticket_panel (guild_id, channel_id, message_id, category_id, transcripts_id, helpers_role_id, everyone_role_id, description, buttons)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
            channel_id = excluded.channel_id,
            message_id = excluded.message_id,
            category_id = excluded.category_id,
            transcripts_id = excluded.transcripts_id,
            helpers_role_id = excluded.helpers_role_id,
            everyone_role_id = excluded.everyone_role_id,
            description = excluded.description,
            buttons = excluded.buttons
        """,
            (
                guild_id,
                channel_id,
                message_id,
                category_id,
                transcripts_id,
                helpers_role_id,
                everyone_role_id,
                description,
                ",".join(buttons),
            ),
        )
        conn.commit()
        conn.close()

    def get_ticket_panel(self, guild_id):
        """Retrieve ticket panel details for a guild."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ticket_panel WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    async def reinitialize_ticket_panel(self, guild):
        """Reinitialize the ticket panel on bot startup."""
        data = self.get_ticket_panel(guild.id)
        if not data:
            logging.warning(
                f"No ticket panel found for guild '{guild.name}' (ID: {guild.id})."
            )
            return

        _, channel_id, message_id, _, _, _, _, description, buttons = data
        channel = guild.get_channel(channel_id)

        if not channel:
            logging.warning(
                f"Channel with ID {channel_id} not found in guild '{guild.name}'."
            )
            return

        try:
            message = await channel.fetch_message(message_id)
            logging.info(
                f"Reinitialized ticket panel for guild '{guild.name}' (ID: {guild.id})."
            )

            # Create buttons dynamically
            class TicketButtons(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                    for i, button_name in enumerate(buttons.split(",")):
                        self.add_item(
                            discord.ui.Button(
                                label=button_name,
                                custom_id=button_name,
                                style=[
                                    discord.ButtonStyle.danger,
                                    discord.ButtonStyle.secondary,
                                    discord.ButtonStyle.success,
                                ][i],
                                emoji=[
                                    "<:help:1312507464188690462>",
                                    "<:invite:1312507843437396060>",
                                    "<:movie:1312507878849904752>",
                                ][i],
                            )
                        )

            # Edit the message to attach the view again
            view = TicketButtons()
            await message.edit(view=view)

        except discord.NotFound:
            logging.warning(
                f"Message with ID {message_id} not found in channel {channel.name} (ID: {channel.id})."
            )
        except Exception as e:
            logging.error(f"Error while reinitializing ticket panel: {e}")

    @app_commands.command(name="ticketsetup", description="Setup your ticket panel")
    @app_commands.describe(
        channel="Select a ticket creation channel",
        category="Select the ticket channels parent category",
        transcripts="Select a ticket transcripts channel",
        helpers="Select the ticket helpers role",
        everyone="Provide the @everyone role",
        description="Set a description of the ticket system",
        firstbutton="Select a name for your first button",
        secondbutton="Select a name for your second button",
        thirdbutton="Select a name for your third button",
    )
    async def ticketsetup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        category: discord.CategoryChannel,
        transcripts: discord.TextChannel,
        helpers: discord.Role,
        everyone: discord.Role,
        description: str,
        firstbutton: str,
        secondbutton: str,
        thirdbutton: str,
    ):
        """Set up the ticket system."""
        guild = interaction.guild

        try:
            # Define button names and emojis
            buttons = [firstbutton, secondbutton, thirdbutton]
            emojis = [
                "<:help:1312507464188690462>",
                "<:invite:1312507843437396060>",
                "<:movie:1312507878849904752>",
            ]  # Replace with your preferred emojis

            # Create buttons
            class TicketButtons(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                    for i, button_name in enumerate(buttons):
                        self.add_item(
                            discord.ui.Button(
                                label=button_name,
                                custom_id=button_name,
                                style=[
                                    discord.ButtonStyle.danger,
                                    discord.ButtonStyle.secondary,
                                    discord.ButtonStyle.success,
                                ][i],
                                emoji=emojis[i],
                            )
                        )

            # Create embed
            embed = discord.Embed(
                title=f"{guild.name} | Ticket System",
                description=description,
                color=discord.Color.random(),
            )
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

            # Send the message to the specified channel
            ticket_message = await channel.send(embed=embed, view=TicketButtons())

            # Save the panel to the database
            self.save_ticket_panel(
                guild.id,
                channel.id,
                ticket_message.id,
                category.id,
                transcripts.id,
                helpers.id,
                everyone.id,
                description,
                buttons,
            )

            await interaction.response.send_message(
                "Ticket system setup successfully!", ephemeral=True
            )

        except Exception as e:
            logging.error(f"Error during ticket setup: {e}")
            await interaction.response.send_message(
                "An error occurred while setting up the ticket system.", ephemeral=True
            )

    @commands.Cog.listener()
    async def on_ready(self):
        """Reinitialize ticket panels for all guilds on bot startup."""
        for guild in self.bot.guilds:
            await self.reinitialize_ticket_panel(guild)

    async def cog_load(self):
        """Associate commands with a specific guild."""
        guild = discord.Object(GUILD_ID)  # Replace with your GUILD_ID
        self.bot.tree.add_command(self.ticketsetup, guild=guild)


async def setup(bot):
    await bot.add_cog(TicketSetup(bot))
    logging.info("TicketSetup cog loaded.")
