import discord
from discord.ext import commands
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

        # Try to initialize Plex
        self.load_plex_config()

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
            title=f"**{self.plex_server_name} Invite**  🎟️",
            description=message,
            color=0x00FF00,
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
                        embed = discord.Embed(
                            title="",
                            description="**GOTCHA**, wir werden deine Email bearbeiten!",
                            color=0x00FF00,
                        )
                        await after.send(embed=embed)

                        if plexinviter(self.plex_server, email, self.plex_libs):
                            save_user_email(
                                self.db_conn, str(after.id), email, after.name
                            )
                            await asyncio.sleep(5)

                            embed = discord.Embed(
                                title="",
                                description=f"**Whoop, Whoop**\n\n<:approved:995615632961847406> **{email}** \n\nwurde bei **{self.plex_server_name}** hinzugefügt!\n\n➡️ **[{self.plex_server_name} Invite akzeptieren](https://app.plex.tv/desktop/#!/settings/manage-library-access)**",
                                color=0x00FF00,
                            )
                            await after.send(embed=embed)
                        else:
                            embed = discord.Embed(
                                title="",
                                description="<:rejected:995614671128244224> Es gab einen Fehler beim Hinzufügen deiner Email. Bitte kontaktiere <@408885990971670531>.",
                                color=0xF50000,
                            )
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

                            embed = discord.Embed(
                                title="",
                                description=f"<:approved:995615632961847406> Du wurdest bei **{self.plex_server_name}** entfernt!",
                                color=0x00FF00,
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
            user_id = int(user[1])
            db_user = self.bot.get_user(user_id)
            db_email = user[2] if user[2] else "No Plex"

            try:
                username = db_user.name
            except:
                username = "User Not Found."

            embed.add_field(
                name=f"**{index}. {username}**",
                value=db_email,
                inline=False,
            )
            table.add_row((index, username, db_email))

        total = str(len(all_users))
        if len(all_users) > 25:
            with open("plex_db.txt", "w") as f:
                f.write(table.draw())

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
