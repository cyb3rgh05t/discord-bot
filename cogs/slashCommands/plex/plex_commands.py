import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import os
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import texttable
from config.settings import GUILD_ID
from cogs.helpers.logger import logger  # Updated import
from cogs.helpers.plex_helper import (
    plexinviter,
    plexremove,
    verifyemail,
    init_db,
    save_user_email,
    get_user_email,
    remove_email,
    delete_user,
    read_all_users,
)

# Database path
PLEX_DB_PATH = "databases/plex_clients.db"

# Ensure database directory exists
os.makedirs(os.path.dirname(PLEX_DB_PATH), exist_ok=True)


class PlexCommands(commands.Cog):
    """Commands for managing Plex invitations"""

    def __init__(self, bot):
        self.bot = bot
        self.db_conn = init_db(PLEX_DB_PATH)

        # Try to load Plex configuration
        self.plex_configured = False
        self.plex_server = None
        self.plex_server_name = ""
        self.plex_roles = []
        self.plex_libs = ["all"]
        self.use_plex = False
        self.plex_connection_failed = False  # Track connection status
        self.admin_user_id = None  # Will be loaded from config

        # Try to initialize Plex
        self.load_plex_config()

        # Start the Plex health check task
        self.plex_health_check.start()

    def load_plex_config(self):
        """Load Plex configuration from settings or environment variables"""
        try:
            # This is a placeholder - you should adapt this to your configuration system
            # Try to load from settings.py if available
            from config.settings import (
                PLEX_USER,
                PLEX_PASS,
                PLEX_SERVER_NAME,
                PLEX_TOKEN,
                PLEX_BASE_URL,
                PLEX_ROLES,
                PLEX_LIBS,
                PLEX_ENABLED,
            )

            # Try to load admin user ID
            try:
                from config.settings import ADMIN_USER_ID

                self.admin_user_id = int(ADMIN_USER_ID)
            except (ImportError, AttributeError):
                logger.warning(
                    "ADMIN_USER_ID not found in settings - Plex health check notifications will be disabled"
                )
                self.admin_user_id = None

            self.plex_server_name = PLEX_SERVER_NAME
            self.plex_roles = (
                PLEX_ROLES if isinstance(PLEX_ROLES, list) else PLEX_ROLES.split(",")
            )
            self.plex_libs = (
                PLEX_LIBS if isinstance(PLEX_LIBS, list) else PLEX_LIBS.split(",")
            )
            self.use_plex = PLEX_ENABLED

            # Try to connect to Plex
            if self.use_plex:
                if PLEX_TOKEN and PLEX_BASE_URL:
                    # Connect using token
                    self.plex_server = PlexServer(PLEX_BASE_URL, PLEX_TOKEN)
                    self.plex_configured = True
                    logger.info("Connected to Plex using token")
                elif PLEX_USER and PLEX_PASS and PLEX_SERVER_NAME:
                    # Connect using username and password
                    account = MyPlexAccount(PLEX_USER, PLEX_PASS)
                    self.plex_server = account.resource(PLEX_SERVER_NAME).connect()
                    self.plex_configured = True
                    logger.info("Connected to Plex using username and password")
                else:
                    logger.warning("Insufficient Plex credentials provided")
        except ImportError:
            logger.warning("Could not import Plex settings from config.settings")
        except Exception as e:
            logger.error(f"Error connecting to Plex: {e}")

    # Embed message functions
    async def embederror(self, interaction, message):
        """Send an error embed message"""
        embed = discord.Embed(title="", description=message, color=0xF50000)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def embedinfo(self, interaction, message):
        """Send an info embed message"""
        embed = discord.Embed(title="", description=message, color=0x00FF00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def embedemail(self, user, message):
        """Send an email request embed message"""
        embed = discord.Embed(
            title="<:splex:1033460420587049021> StreamNet Plex Einladung",
            description=(
                f"**Hallo {user.mention}!**\n\n"
                f"Du wurdest für **{self.plex_server_name}** freigeschalten!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📧 **Bitte antworte mit deiner Plex Email-Adresse**\n\n"
                f"⚠️ **Wichtig:**\n"
                f"• Verwende die Email, die bei Plex registriert ist\n"
                f"• Nur die Email-Adresse senden (keine zusätzlichen Texte)\n"
                f"• Du hast 24 Stunden Zeit zu antworten\n\n"
                f"💡 *Beispiel: deine-email@beispiel.de*"
            ),
            color=0xE5A00D,
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
        )
        embed.set_footer(
            text=f"{self.plex_server_name} • Warte auf deine Antwort...",
            icon_url="https://cdn.discordapp.com/emojis/1310635856318562334.png",
        )
        await user.send(embed=embed)

    async def embederroremail(self, user, message):
        """Send an error email embed message"""
        embed = discord.Embed(title="", description=message, color=0xF50000)
        embed.add_field(
            name="Mögliche Fehler:",
            value="``•`` Fehlerhaftes **EMail**-Format.\n``•`` Du bist schon bei **StreamNet** angemeldet.\n``•`` Die angegebene Email ist nicht bei **Plex** registriert.\n``•`` Username anstadt **EMail** angegeben",
            inline=False,
        )
        await user.send(embed=embed)

    async def getemail(self, user):
        """Get email from user via DM"""
        email = None
        await self.embedemail(
            user,
            "Antworte einfach mit deiner **PLEX Mail**, damit ich dich bei **"
            + self.plex_server_name
            + "** hinzufügen kann!",
        )

        while email is None:

            def check(m):
                return m.author == user and not m.guild

            try:
                msg = await self.bot.wait_for("message", timeout=86400, check=check)
                if verifyemail(str(msg.content)):
                    return str(msg.content)
                else:
                    email = None
                    message = "<:rejected:995614671128244224> Ungültige **Plex Mail**. Bitte gib nur deine **Plex Mail** ein und nichts anderes."
                    await self.embederroremail(user, message)
                    continue
            except asyncio.TimeoutError:
                message = (
                    "⏳ Zeitüberschreitung\n\nWende dich an den **"
                    + self.plex_server_name
                    + "** Admin <@408885990971670531> damit der dich manuell hinzufügen kann."
                )
                await user.send(
                    embed=discord.Embed(title="", description=message, color=0xF50000)
                )
                return None

    async def add_to_plex(self, email, interaction):
        """Add a user to Plex"""
        if not self.plex_configured or not self.use_plex:
            await self.embederror(
                interaction,
                "<:rejected:995614671128244224> Plex integration is not configured or disabled.",
            )
            return False

        if verifyemail(email):
            if plexinviter(self.plex_server, email, self.plex_libs):
                # Save to invites tracking database
                try:
                    import sqlite3
                    from datetime import datetime, timedelta

                    conn = sqlite3.connect("databases/invites.db")
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO invites (email, discord_user, status, created_at, expires_at)
                        VALUES (?, ?, 'active', ?, ?)
                    """,
                        (
                            email,
                            str(interaction.user),
                            datetime.now().isoformat(),
                            (datetime.now() + timedelta(days=30)).isoformat(),
                        ),
                    )
                    conn.commit()
                    conn.close()
                    logger.info(f"Saved invite for {email} to tracking database")
                except Exception as e:
                    logger.error(f"Failed to save invite to database: {e}")

                await self.embedinfo(
                    interaction,
                    "<:approved:995615632961847406> Deine **Plex Mail** wurde zu **"
                    + self.plex_server_name
                    + "** hinzugefügt",
                )
                return True
            else:
                await self.embederror(
                    interaction,
                    "<:rejected:995614671128244224> Es gab einen Fehler beim Hinzufügen dieser Email-Adresse. Bitte überprüfe die Logs für mehr Informationen.",
                )
                return False
        else:
            await self.embederror(
                interaction, "<:rejected:995614671128244224> Ungültige Email-Adresse."
            )
            return False

    async def remove_from_plex(self, email, interaction):
        """Remove a user from Plex"""
        if not self.plex_configured or not self.use_plex:
            await self.embederror(
                interaction,
                "<:rejected:995614671128244224> Plex integration is not configured or disabled.",
            )
            return False

        if verifyemail(email):
            if plexremove(self.plex_server, email):
                await self.embedinfo(
                    interaction,
                    "<:approved:995615632961847406> Diese Email-Adresse wurde von **"
                    + self.plex_server_name
                    + "** entfernt.",
                )
                return True
            else:
                await self.embederror(
                    interaction,
                    "<:rejected:995614671128244224> Es gab einen Fehler beim Entfernen dieser Email-Adresse. Bitte überprüfe die Logs für mehr Informationen.",
                )
                return False
        else:
            await self.embederror(
                interaction, "<:rejected:995614671128244224> Ungültige Email-Adresse."
            )
            return False

    # Event Handlers
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Monitor role changes to trigger Plex invitation or removal"""
        if not self.plex_configured or not self.use_plex or not self.plex_roles:
            return

        roles_in_guild = after.guild.roles
        role = None
        plex_processed = False

        # Check Plex roles
        for role_for_app in self.plex_roles:
            for role_in_guild in roles_in_guild:
                if role_in_guild.name == role_for_app:
                    role = role_in_guild

                # Plex role was added
                if role is not None and (
                    role in after.roles and role not in before.roles
                ):
                    email = await self.getemail(after)
                    if email is not None:
                        # Processing embed
                        embed = discord.Embed(
                            title="📧 Email wird verarbeitet",
                            description="Deine Email-Adresse wird gerade bearbeitet...\nBitte warte einen Moment......",
                            color=0xE5A00D,
                        )
                        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
                        )
                        await after.send(embed=embed)

                        if plexinviter(self.plex_server, email, self.plex_libs):
                            save_user_email(
                                self.db_conn, str(after.id), email, after.name
                            )

                            # Save to invites tracking database
                            try:
                                import sqlite3
                                from datetime import datetime, timedelta

                                conn = sqlite3.connect("databases/invites.db")
                                cursor = conn.cursor()
                                cursor.execute(
                                    """
                                    INSERT INTO invites (email, discord_user, status, created_at, expires_at)
                                    VALUES (?, ?, 'active', ?, ?)
                                """,
                                    (
                                        email,
                                        str(after),
                                        datetime.now().isoformat(),
                                        (
                                            datetime.now() + timedelta(days=30)
                                        ).isoformat(),
                                    ),
                                )
                                conn.commit()
                                conn.close()
                                logger.info(
                                    f"Saved auto-role invite for {email} to tracking database"
                                )
                            except Exception as e:
                                logger.error(f"Failed to save invite to database: {e}")

                            await asyncio.sleep(5)

                            # Success embed
                            embed = discord.Embed(
                                title="<:approved:995615632961847406> **Erfolgreich zu StreamNet Plex hinzugefügt!**",
                                description=(
                                    f"📧 Email: `{email}`\n"
                                    f"🎬 Server: **{self.plex_server_name}**\n\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                    f"**➡️ Nächste Schritte:**\n"
                                    f"1️⃣ Überprüfe deine Email für die Plex-Einladung\n"
                                    f"2️⃣ Klicke auf den Button unten oder den Link in der Email\n"
                                    f"3️⃣ Akzeptiere die Einladung in deinen Plex-Einstellungen\n\n"
                                    f"<:splex:1033460420587049021> Viel Spaß beim Streamen!"
                                ),
                                color=0xE5A00D,
                            )
                            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
                            )
                            embed.set_footer(
                                text=f"{self.plex_server_name} • StreamNet Club",
                                icon_url="https://cdn.discordapp.com/emojis/1310635856318562334.png",
                            )

                            # Create button for accepting invite
                            view = discord.ui.View()
                            button = discord.ui.Button(
                                label="Einladung akzeptieren",
                                style=discord.ButtonStyle.link,
                                url="https://app.plex.tv/desktop/#!/settings/manage-library-access",
                                emoji="✅",
                            )
                            view.add_item(button)

                            await after.send(embed=embed, view=view)

                            # Start Plex walkthrough after successful invitation
                            await asyncio.sleep(3)  # Brief pause before walkthrough
                            walkthrough_cog = self.bot.get_cog("PlexWalkthrough")
                            if walkthrough_cog:
                                await walkthrough_cog.send_walkthrough(after)
                        else:
                            # Error embed
                            embed = discord.Embed(
                                title="❌ Fehler beim Hinzufügen",
                                description=(
                                    f"<:rejected:995614671128244224> **Es gab einen Fehler!**\n\n"
                                    f"Deine Email-Adresse konnte nicht zu Plex hinzugefügt werden.\n\n"
                                    f"**Mögliche Gründe:**\n"
                                    f"• Email-Adresse ist bereits eingeladen\n"
                                    f"• Ungültige Email-Adresse\n"
                                    f"• Plex-Server ist nicht erreichbar\n\n"
                                    f"Bitte kontaktiere <@408885990971670531> für Hilfe."
                                ),
                                color=0xF50000,
                            )
                            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
                            )
                            embed.set_footer(text="Plex Fehler")
                            await after.send(embed=embed)

                    plex_processed = True
                    break

                # Plex role was removed
                elif role is not None and (
                    role not in after.roles and role in before.roles
                ):
                    try:
                        user_id = after.id
                        email = get_user_email(self.db_conn, user_id)
                        if email:
                            plexremove(self.plex_server, email)
                            removed = remove_email(self.db_conn, user_id)
                            if removed:
                                logger.info(
                                    f"Removed Plex email for {after.name} from database"
                                )
                            else:
                                logger.warning(
                                    f"Could not remove Plex from user {after.name}"
                                )

                            # Update invite status in tracking database
                            try:
                                import sqlite3
                                from datetime import datetime

                                conn = sqlite3.connect("databases/invites.db")
                                cursor = conn.cursor()
                                cursor.execute(
                                    """
                                    UPDATE invites 
                                    SET status = 'revoked'
                                    WHERE discord_user = ? AND status = 'active'
                                """,
                                    (str(after),),
                                )
                                conn.commit()
                                conn.close()
                                logger.info(
                                    f"Marked invite as revoked for {after} in tracking database"
                                )
                            except Exception as e:
                                logger.error(f"Failed to update invite status: {e}")

                            embed = discord.Embed(
                                title="👋 StreamNet Plex Zugriff entfernt",
                                description=(
                                    f"**Hallo {after.mention}!**\n\n"
                                    f"Dein Zugriff auf **{self.plex_server_name}** wurde entfernt.\n\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                    f"📧 Email: `{email}`\n"
                                    f"🎬 Server: **{self.plex_server_name}**\n\n"
                                    f"ℹ️ **Grund:**\n"
                                    f"• Deine Rolle wurde entfernt\n"
                                    f"• Zugriff auf Plex wurde automatisch entzogen\n\n"
                                    f"💡 *Bei Fragen wende dich an <@408885990971670531>*"
                                ),
                                color=0xE5A00D,
                            )
                            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
                            )
                            embed.set_footer(
                                text=f"{self.plex_server_name} • Zugriff entfernt",
                                icon_url="https://cdn.discordapp.com/emojis/1310635856318562334.png",
                            )
                            await after.send(embed=embed)
                    except Exception as e:
                        logger.error(f"Error removing user from Plex: {e}")

                    plex_processed = True
                    break

            if plex_processed:
                break

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Clean up when a member leaves the server"""
        if self.plex_configured and self.use_plex:
            email = get_user_email(self.db_conn, member.id)
            if email:
                plexremove(self.plex_server, email)

        deleted = delete_user(self.db_conn, member.id)
        if deleted:
            logger.info(
                f"Removed {member.name} from database because user left Discord server."
            )

        # Update invite status in tracking database
        try:
            import sqlite3
            from datetime import datetime

            conn = sqlite3.connect("databases/invites.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE invites 
                SET status = 'removed'
                WHERE discord_user = ? AND status IN ('active', 'revoked')
            """,
                (str(member),),
            )
            conn.commit()
            conn.close()
            logger.info(f"Marked invite as removed for {member} in tracking database")
        except Exception as e:
            logger.error(f"Failed to update invite status on member remove: {e}")

    # Commands
    @app_commands.command(name="invite", description="Invite a user to Plex")
    @app_commands.describe(email="The email to invite to Plex")
    @app_commands.checks.has_permissions(administrator=True)
    async def plexinvite(self, interaction: discord.Interaction, email: str):
        """Command to invite a user to Plex"""
        await self.add_to_plex(email, interaction)

    @app_commands.command(name="remove", description="Remove a user from Plex")
    @app_commands.describe(email="The email to remove from Plex")
    @app_commands.checks.has_permissions(administrator=True)
    async def plexremove(self, interaction: discord.Interaction, email: str):
        """Command to remove a user from Plex"""
        await self.remove_from_plex(email, interaction)

    @app_commands.command(name="dbls", description="List the Plex database")
    @app_commands.checks.has_permissions(administrator=True)
    async def dbls(self, interaction: discord.Interaction):
        """Command to list the Plex database"""

        all_users = read_all_users(self.db_conn)

        embed = discord.Embed(title="PlexInviter Database.")
        table = texttable.Texttable()
        table.set_cols_dtype(["t", "t", "t"])
        table.set_cols_align(["c", "c", "c"])
        header = ("#", "DISCORD", "PLEX")
        table.add_row(header)

        for index, user in enumerate(all_users):
            index = index + 1
            # Add check to handle empty user ID
            if user[1] and str(user[1]).strip():
                try:
                    user_id = int(user[1])
                    db_user = self.bot.get_user(user_id)
                    username = db_user.name if db_user else "User Not Found."
                except (ValueError, AttributeError):
                    # Handle invalid user IDs
                    username = f"Invalid ID: {user[1]}"
            else:
                username = "No Discord ID"

            db_email = user[2] if user[2] else "No Plex"

            embed.add_field(
                name=f"**{index}. {username}**",
                value=db_email,
                inline=False,
            )
            table.add_row((index, username, db_email))

        total = str(len(all_users))
        if len(all_users) > 25:
            with open("plex_db.txt", "w") as f:
                table_output = table.draw()
                if table_output:
                    f.write(table_output)

            await interaction.response.send_message(
                f"Database too large! Total: {total}",
                file=discord.File("plex_db.txt"),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="dbadd", description="Add a user to the Plex database")
    @app_commands.describe(
        member="The Discord user to add", email="The Plex email (optional)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def dbadd(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        email: str = "",
    ):
        """Command to add a user to the Plex database"""
        email = email.strip()

        # Check email if provided
        if email and not verifyemail(email):
            await self.embederror(
                interaction, "<:rejected:995614671128244224> Ungültige Email-Adresse."
            )
            return

        try:
            if save_user_email(self.db_conn, str(member.id), email, member.name):
                await self.embedinfo(
                    interaction,
                    "<:approved:995615632961847406> Email wurde zur Datenbank hinzugefügt.",
                )
            else:
                await self.embederror(
                    interaction,
                    "<:rejected:995614671128244224> Es gab einen Fehler beim Hinzufügen dieser Email-Adresse zur Datenbank. Bitte überprüfe die Logs für mehr Informationen.",
                )
        except Exception as e:
            logger.error(f"Error adding user to database: {e}")
            await self.embederror(
                interaction,
                "<:rejected:995614671128244224> Es gab einen Fehler beim Hinzufügen dieser Email-Adresse zur Datenbank. Bitte überprüfe die Logs für mehr Informationen.",
            )

    @app_commands.command(
        name="dbrm", description="Remove a user from the Plex database"
    )
    @app_commands.describe(
        position="The position in the database list (use /dbls to see positions)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def dbrm(self, interaction: discord.Interaction, position: int):
        """Command to remove a user from the Plex database"""
        all_users = read_all_users(self.db_conn)

        try:
            position = int(position) - 1
            if 0 <= position < len(all_users):
                user_id = all_users[position][1]
                discord_user = await self.bot.fetch_user(user_id)
                username = discord_user.name

                if delete_user(self.db_conn, user_id):
                    logger.info(f"Removed {username} from database")
                    await self.embedinfo(
                        interaction,
                        f"<:approved:995615632961847406> {username} wurde aus der Datenbank entfernt.",
                    )
                else:
                    await self.embederror(
                        interaction,
                        "<:rejected:995614671128244224> Konnte diesen Benutzer nicht aus der Datenbank entfernen.",
                    )
            else:
                await self.embederror(
                    interaction,
                    "<:rejected:995614671128244224> Ungültige Position. Bitte verwende /dbls, um die richtige Position zu finden.",
                )
        except Exception as e:
            logger.error(f"Error removing user from database: {e}")
            await self.embederror(
                interaction,
                "<:rejected:995614671128244224> Es gab einen Fehler beim Entfernen dieses Benutzers aus der Datenbank. Bitte überprüfe die Logs für mehr Informationen.",
            )

    @tasks.loop(hours=1)
    async def plex_health_check(self):
        """Check Plex connection every hour and notify admin if it fails"""
        if not self.use_plex or not self.plex_configured:
            return

        try:
            # Try to connect to Plex server
            if self.plex_server:
                # Simple ping to check if server is responsive
                _ = self.plex_server.library.sections()

                # If we get here, connection is successful
                if self.plex_connection_failed:
                    # Connection was down but is now back up
                    self.plex_connection_failed = False
                    logger.info("Plex connection restored")

                    # Notify admin that connection is back
                    if self.admin_user_id:
                        try:
                            admin = await self.bot.fetch_user(self.admin_user_id)
                            embed = discord.Embed(
                                title="✅ Plex Connection Restored",
                                description=(
                                    f"**Good news!**\n\n"
                                    f"Connection to **{self.plex_server_name}** has been restored.\n\n"
                                    f"🎬 Server: **{self.plex_server_name}**\n"
                                    f"✅ Status: **Online**"
                                ),
                                color=0x00FF00,
                            )
                            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
                            )
                            await admin.send(embed=embed)
                        except Exception as e:
                            logger.error(f"Could not send restoration DM to admin: {e}")
        except Exception as e:
            # Connection failed
            if not self.plex_connection_failed:
                # First time failure - notify admin
                self.plex_connection_failed = True
                logger.error(f"Plex health check failed: {e}")

                # Send DM to admin
                if self.admin_user_id:
                    try:
                        admin = await self.bot.fetch_user(self.admin_user_id)
                        embed = discord.Embed(
                            title="⚠️ Plex Connection Failed",
                            description=(
                                f"**Connection issue detected!**\n\n"
                                f"Unable to connect to **{self.plex_server_name}**.\n\n"
                                f"🎬 Server: **{self.plex_server_name}**\n"
                                f"❌ Status: **Offline/Unreachable**\n"
                                f"⚠️ Error: `{str(e)[:100]}`\n\n"
                                f"Please check the server status and network connection."
                            ),
                            color=0xFF0000,
                        )
                        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
                        )
                        await admin.send(embed=embed)
                        logger.info(
                            f"Sent Plex connection failure notification to admin {self.admin_user_id}"
                        )
                    except Exception as dm_error:
                        logger.error(f"Could not send DM to admin: {dm_error}")
                else:
                    logger.warning(
                        "Admin user ID not configured - cannot send Plex failure notification"
                    )

    @plex_health_check.before_loop
    async def before_plex_health_check(self):
        """Wait until the bot is ready before starting the health check"""
        await self.bot.wait_until_ready()

    def cog_unload(self):
        """Stop the health check task when cog is unloaded"""
        self.plex_health_check.cancel()

    async def cog_load(self):
        """Associate commands with a specific guild."""
        guild = discord.Object(GUILD_ID)
        self.bot.tree.add_command(self.plexinvite, guild=guild)
        self.bot.tree.add_command(self.plexremove, guild=guild)
        self.bot.tree.add_command(self.dbls, guild=guild)
        self.bot.tree.add_command(self.dbadd, guild=guild)
        self.bot.tree.add_command(self.dbrm, guild=guild)


async def setup(bot):
    await bot.add_cog(PlexCommands(bot))
    logger.debug("PlexCommands cog loaded.")
