import os
import sqlite3
import discord
import logging
from discord.ext import commands
from discord.ui import View, Button
from config.settings import MEMBER_ROLE, WELCOME_CHANNEL_ID


class RulesAcceptButton(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Ensure the `databases` folder exists
        db_folder = "databases"
        os.makedirs(db_folder, exist_ok=True)

        # Path to the database file
        self.db_path = os.path.join(db_folder, "rules_message.db")

        # Initialize SQLite database
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rules_message (
                guild_id INTEGER PRIMARY KEY,
                message_id INTEGER
            )
            """
        )
        self.conn.commit()

    class AcceptButton(Button):
        """Button to accept the rules."""

        def __init__(self, cog):
            super().__init__(
                label="Bestätige die Regeln mit einem Klick",
                style=discord.ButtonStyle.success,
                custom_id="acceptRole",
            )
            self.cog = cog  # Pass the cog for access to bot and other methods

        async def callback(self, interaction: discord.Interaction):
            """Handle button click."""
            member = interaction.user
            guild = interaction.guild
            role_name = MEMBER_ROLE
            role = discord.utils.get(guild.roles, name=role_name)

            if not role:
                await interaction.response.send_message(
                    f"❌ Could not find the '{role_name}' role. Please contact an admin.",
                    ephemeral=True,
                )
                return

            if role in member.roles:
                await interaction.response.send_message(
                    f"✅ {member.mention}, du hast die Regeln schon bestätigt!!",
                    ephemeral=True,
                )
            else:
                await member.add_roles(role, reason="Accepted the rules")
                await interaction.response.send_message(
                    f"✅ {member.mention}, du hast die Regeln bestätigt und die Rolle '{role.name}' wurde dir hinzugefügt!",
                    ephemeral=True,
                )

                welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)
                if welcome_channel:
                    await welcome_channel.send(
                        f"🎉 Willkommen {member.mention} im **{guild.name}**!\n"
                        f"Das <:sclub:1312507027951452160> Team wünscht dir gute Unterhaltung 😀\n\n"
                        f"Befolge die Schritte wenn du Zutritt zum Service willst.\n"
                        f"<#825364230827409479>"
                    )

    def save_message_id(self, guild_id, message_id):
        """Save or update the rules message ID in the database."""
        logging.debug(f"Saving rules message ID {message_id} for guild {guild_id}.")
        self.cursor.execute(
            """
            INSERT INTO rules_message (guild_id, message_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET message_id = excluded.message_id
            """,
            (guild_id, message_id),
        )
        self.conn.commit()

    def get_message_id(self, guild_id):
        """Retrieve the rules message ID for a guild."""
        logging.debug(f"Retrieving rules message ID for guild {guild_id}.")
        self.cursor.execute(
            "SELECT message_id FROM rules_message WHERE guild_id = ?", (guild_id,)
        )
        result = self.cursor.fetchone()
        if result:
            logging.debug(f"Found message ID {result[0]} for guild {guild_id}.")
            return result[0]
        logging.warning(f"No message ID found for guild {guild_id}.")
        return None

    async def resend_rules_message(self, guild):
        """Resend the rules message if the bot restarts."""
        logging.debug(
            f"Attempting to resend rules message for guild '{guild.name}' (ID: {guild.id})."
        )
        message_id = self.get_message_id(guild.id)
        if not message_id:
            logging.warning(
                f"No rules message ID found for guild '{guild.name}' (ID: {guild.id})."
            )
            return

        try:
            channel = discord.utils.get(guild.channels, id=WELCOME_CHANNEL_ID)
            if not channel:
                logging.warning(
                    f"Welcome channel not found for guild '{guild.name}' (ID: {guild.id})."
                )
                return

            logging.debug(
                f"Attempting to fetch message ID {message_id} in channel {channel.name}."
            )
            message = await channel.fetch_message(message_id)
            logging.info(
                f"Rules message successfully loaded for guild '{guild.name}' (ID: {guild.id})."
            )

            view = View()
            view.add_item(self.AcceptButton(self))  # Pass the cog instance
            await message.edit(view=view)
        except discord.NotFound:
            logging.warning(
                f"Rules message with ID {message_id} not found in guild '{guild.name}' (ID: {guild.id})."
            )
        except discord.Forbidden:
            logging.error(
                f"Bot lacks permissions to fetch message ID {message_id} in guild '{guild.name}'."
            )
        except Exception as e:
            logging.error(f"Unexpected error when resending rules message: {e}")

    @commands.command(
        name="rulesbutton", help="Send the rules message with an accept button."
    )
    @commands.has_permissions(administrator=True)
    async def rulesbutton(self, ctx):
        """Send the rules message with an accept button."""
        view = View()
        view.add_item(self.AcceptButton(self))  # Pass the cog instance

        # Send the rules message
        rules_text = (
            "**Bitte akzeptiert die Regeln für die MEMBER Rolle:**\n\n"
            "**```diff\n- Regel #1: Streng verboten```**\n"
            "• Es ist strengstens verboten für StreamNet.Club zu **werben**.\n"
            "• Es ist strengstens verboten StreamNet einem nicht vorhandenen Mitglied zu **demonstrieren**.\n"
            "• Es ist strengstens verboten über StreamNet.Club mit einem nicht vorhandenen Mitglied zu **diskutieren**.\n"
            "• Du darfst dein StreamNet Konto **nicht** mit anderen Personen **teilen**.\n\n"
            "**```diff\n- Regel #2: Sei kein Ars##```**\n"
            "• Sei allen auf dem Server gegenüber respektvoll.\n\n"
            "**```diff\n- Regel #3: Verwende die entsprechenden Kanäle```**\n"
            "• Bitte verwende den richtigen Kanal für deine Frage und bleib innerhalb des Kanals beim Thema.\n\n"
            "**```diff\n- Regel #4: Sei geduldig```**\n"
            "• Nicht jeder ist jederzeit verfügbar. Jemand wird dir antworten, wenn er kann.\n"
            "==============================\n"
        )

        message = await ctx.send(content=rules_text, view=view)
        self.save_message_id(ctx.guild.id, message.id)

    @commands.Cog.listener()
    async def on_ready(self):
        """Resend rules message for all guilds on bot startup."""
        for guild in self.bot.guilds:
            await self.resend_rules_message(guild)


async def setup(bot):
    await bot.add_cog(RulesAcceptButton(bot))
    logging.info("RulesAcceptButton cog loaded.")
