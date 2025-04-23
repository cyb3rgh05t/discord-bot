import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import logging
from cogs.helpers.logger import logger


class BaseTicketSetup(commands.Cog):
    """Base class for ticket setup systems"""

    def __init__(self, bot, db_path, table_prefix):
        self.bot = bot
        self.db_path = db_path
        self.table_prefix = table_prefix  # "plex" or "tv"
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database for ticket panels."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_prefix}_ticket_panel (
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

        # Create table for individual tickets
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_prefix}_ticket_data (
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
            f"""
            INSERT INTO {self.table_prefix}_ticket_panel (guild_id, channel_id, message_id, category_id, transcripts_id, helpers_role_id, everyone_role_id, description, buttons)
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
        cursor.execute(
            f"SELECT * FROM {self.table_prefix}_ticket_panel WHERE guild_id = ?",
            (guild_id,),
        )
        result = cursor.fetchone()
        conn.close()
        return result

    async def reinitialize_ticket_panel(self, guild):
        """Reinitialize the ticket panel on bot startup."""
        data = self.get_ticket_panel(guild.id)
        if not data:
            logger.warning(
                f"No {self.table_prefix} ticket panel found for guild '{guild.name}' (ID: {guild.id})."
            )
            return

        _, channel_id, message_id, _, _, _, _, description, buttons = data
        channel = guild.get_channel(channel_id)

        if not channel:
            logger.warning(
                f"Channel with ID {channel_id} not found in guild '{guild.name}'."
            )
            return

        try:
            message = await channel.fetch_message(message_id)
            logger.info(
                f"Reinitialized {self.table_prefix} ticket panel for guild '{guild.name}' (ID: {guild.id})."
            )

            # Create buttons dynamically
            class TicketButtons(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                    for i, button_name in enumerate(buttons.split(",")):
                        self.add_item(
                            discord.ui.Button(
                                label=button_name,
                                custom_id=f"{self.table_prefix}_{button_name}",
                                style=[
                                    discord.ButtonStyle.danger,
                                    discord.ButtonStyle.secondary,
                                    discord.ButtonStyle.success,
                                ][
                                    i % 3
                                ],  # Cycle through styles if more than 3 buttons
                                emoji=[
                                    "<:help:1312507464188690462>",
                                    "<:invite:1312507843437396060>",
                                    "<:movie:1312507878849904752>",
                                ][
                                    i % 3
                                ],  # Cycle through emojis if more than 3 buttons
                            )
                        )

            # Edit the message to attach the view again
            view = TicketButtons()
            await message.edit(view=view)

        except discord.NotFound:
            logger.warning(
                f"Message with ID {message_id} not found in channel {channel.name} (ID: {channel.id})."
            )
        except Exception as e:
            logger.error(
                f"Error while reinitializing {self.table_prefix} ticket panel: {e}"
            )


# Required setup function that does nothing
# This prevents discord.py from trying to load this as a cog directly
async def setup(bot):
    # This file isn't meant to be loaded as a cog directly
    pass
