import os
import sqlite3
import discord
import logging
from discord.ext import commands
from discord.ui import View, Button
from config.settings import (
    MEMBER_ROLE,
    RULES_CHANNEL_ID,
    WELCOME_CHANNEL_ID,
)
from cogs.helpers.logger import logger


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
                    f"✅ {member.mention}, Du hast die Regeln schon bestätigt!!",
                    ephemeral=True,
                )
            else:
                await member.add_roles(role, reason="Accepted the rules")
                await interaction.response.send_message(
                    f"✅ {member.mention}, du hast Regeln bestätigt und Rolle '{role.name}' wurde hinzugefügt!",
                    ephemeral=True,
                )

                # Send welcome message to channel with enhanced content in plain text
                welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)
                if welcome_channel:
                    welcome_message = (
                        f"<:boss:1030145002568958024> **Willkommen bei {guild.name}!**\n\n"
                        f"Wir freuen uns, dich in unserer Community begrüßen zu dürfen, {member.mention}!\n\n"
                        f"<:tc_error:1364320671261262016> **Nächste Schritte**\n"
                        f"Befolge die Schritte wenn du Zutritt zum Service willst.\n"
                        f"<#825364230827409479>\n\n"
                        f"<:sclub:1312507027951452160> **StreamNet Club**\n"
                        f"Unser Team steht dir bei Fragen gerne zur Verfügung!\n\n"
                        f"Wir wünschen dir gute Unterhaltung 😀"
                    )

                    await welcome_channel.send(welcome_message)

                # Send a direct message to the user
                try:
                    dm_embed = discord.Embed(
                        title=f"Willkommen bei {guild.name}!",
                        description=(
                            f"Hallo {member.name},\n\n"
                            f"Vielen Dank für deine Regelbestätigung! Du hast nun Zugriff auf alle Member-Bereiche in unserem Server.\n\n"
                            f"**Wichtige Informationen:**\n"
                            f"• In <#825364230827409479> findest du Anweisungen, wie du Zugang zu unseren Services bekommst\n"
                            f"• Bei Fragen kannst du jederzeit ein Support-Ticket eröffnen\n"
                            f"• Wir freuen uns auf deine aktive Teilnahme in unserer Community!"
                        ),
                        color=discord.Color.blue(),
                    )

                    # Add server logo/icon
                    if guild.icon:
                        dm_embed.set_thumbnail(url=guild.icon.url)

                    # Add footer
                    dm_embed.set_footer(
                        text=f"{guild.name} • StreamNet Club",
                        icon_url=guild.icon.url if guild.icon else None,
                    )

                    await member.send(embed=dm_embed)
                    logger.info(f"Sent welcome DM to {member.name}")
                except discord.Forbidden:
                    logger.warning(
                        f"Could not send DM to {member.name} - DMs may be disabled"
                    )

    def save_message_id(self, guild_id, message_id):
        """Save or update the rules message ID in the database."""
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
        self.cursor.execute(
            "SELECT message_id FROM rules_message WHERE guild_id = ?", (guild_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    async def resend_rules_message(self, guild):
        """Resend the rules message if the bot restarts."""
        message_id = self.get_message_id(guild.id)
        if not message_id:
            logger.warning(
                f"No rules message ID found for guild '{guild.name}' (ID: {guild.id})."
            )
            return

        try:
            channel = discord.utils.get(guild.channels, id=RULES_CHANNEL_ID)
            if not channel:
                logger.warning(
                    f"Rules channel not found for guild '{guild.name}' (ID: {guild.id})."
                )
                return

            message = await channel.fetch_message(message_id)
            logger.info(
                f"Rules message successfully loaded for guild '{guild.name}' (ID: {guild.id})."
            )

            # Register the view globally
            view = View(timeout=None)
            view.add_item(self.AcceptButton(self))
            self.bot.add_view(view)  # Register globally for persistence
            logger.info("Rules Button registered")
            await message.edit(view=view)
        except discord.NotFound:
            logger.warning(
                f"Rules message with ID {message_id} not found in guild '{guild.name}' (ID: {guild.id})."
            )
        except discord.Forbidden:
            logger.error(
                f"Bot lacks permissions to fetch message ID {message_id} in guild '{guild.name}'."
            )
        except Exception as e:
            logger.error(f"Unexpected error when resending rules message: {e}")

    @commands.command(
        name="rulesbutton", help="Send the rules message with an accept button."
    )
    @commands.has_permissions(administrator=True)
    async def rulesbutton(self, ctx):
        """Send the rules message with an accept button."""
        channel = ctx.guild.get_channel(RULES_CHANNEL_ID)
        if not channel:
            await ctx.send(
                f"❌ The predefined rules channel (ID: {RULES_CHANNEL_ID}) does not exist.",
                ephemeral=True,
            )
            return

        view = View(timeout=None)
        view.add_item(self.AcceptButton(self))  # Pass the cog instance
        self.bot.add_view(view)  # Register globally for persistence

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
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )

        message = await channel.send(content=rules_text, view=view)
        self.save_message_id(ctx.guild.id, message.id)

    @commands.Cog.listener()
    async def on_ready(self):
        """Resend rules message for all guilds on bot startup."""
        for guild in self.bot.guilds:
            await self.resend_rules_message(guild)


async def setup(bot):
    await bot.add_cog(RulesAcceptButton(bot))
    logger.debug("RulesAcceptButton cog loaded.")
