import discord
from discord.ext import commands
from discord import app_commands
import os
import re
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from config.settings import GUILD_ID
from cogs.helpers.logger import logger


class PlexSettings(commands.Cog):
    """Commands for configuring Plex settings"""

    def __init__(self, bot):
        self.bot = bot
        self.settings_path = "config/settings.py"

        # Load settings from settings.py
        self.load_settings()

    def load_settings(self):
        """Load Plex settings from settings.py"""
        try:
            # Import all settings directly
            from config import settings

            # Convert to appropriate types
            self.plex_user = getattr(settings, "PLEX_USER", "")
            self.plex_pass = getattr(settings, "PLEX_PASS", "")
            self.plex_server_name = getattr(settings, "PLEX_SERVER_NAME", "")
            self.plex_token = getattr(settings, "PLEX_TOKEN", "")
            self.plex_base_url = getattr(settings, "PLEX_BASE_URL", "")

            # Handle roles - could be string or list
            plex_roles = getattr(settings, "PLEX_ROLES", [])
            self.plex_roles = (
                plex_roles.split(",") if isinstance(plex_roles, str) else plex_roles
            )

            # Handle libraries - could be string or list
            plex_libs = getattr(settings, "PLEX_LIBS", ["all"])
            self.plex_libs = (
                plex_libs.split(",") if isinstance(plex_libs, str) else plex_libs
            )

            # Get enabled status
            self.plex_enabled = getattr(settings, "PLEX_ENABLED", False)

            # Log configuration in a clean, one-by-one format
            logger.info(f"Plex configuration loaded:")
            logger.info(
                f"  → Plex Status: {'Enabled' if self.plex_enabled else 'Disabled'}"
            )
            logger.info(
                f"  → Plex Server: {self.plex_server_name if self.plex_server_name else 'Not configured'}"
            )

            # Log roles in a cleaner format
            if self.plex_roles:
                logger.info(f"  → Plex Roles: {', '.join(self.plex_roles)}")
            else:
                logger.info(f"  → Plex Roles: None configured")

            # Log libraries in a cleaner format
            if self.plex_libs:
                logger.info(f"  → Plex Share: {len(self.plex_libs)} Libraries")
                logger.debug(f"Plex Shared Libraries: {', '.join(self.plex_libs)}")
            else:
                logger.info(f"  → Libraries: None configured")

            # Log auth method but mask sensitive data
            if self.plex_token:
                logger.info(f"  → PlexAuth method: Token")
                print("---------------------------------------------")
            elif self.plex_user and self.plex_pass:
                logger.info(f"  → PlexAuth method: Credentials")
                print("---------------------------------------------")
            else:
                logger.info(f"  → PlexAuth method: Not configured")
                print("---------------------------------------------")

            return True
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not load Plex settings from settings.py: {e}")
            # Set default values
            self.plex_user = ""
            self.plex_pass = ""
            self.plex_server_name = ""
            self.plex_token = ""
            self.plex_base_url = ""
            self.plex_roles = []
            self.plex_libs = ["all"]
            self.plex_enabled = False
            return False

    def read_settings_file(self):
        """Read the settings.py file content"""
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r") as f:
                return f.read()
        else:
            logger.error(f"Settings file not found at {self.settings_path}")
            return None

    def write_settings_file(self, content):
        """Write the updated content to settings.py"""
        try:
            with open(self.settings_path, "w") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error writing to settings file: {e}")
            return False

    def update_setting(self, content, setting_name, value):
        """Update a setting in settings.py content"""
        # Convert value to appropriate string representation
        if isinstance(value, bool):
            value_str = str(value)
        elif isinstance(value, (int, float)):
            value_str = str(value)
        elif isinstance(value, str):
            value_str = f'"{value}"'
        elif isinstance(value, list):
            value_str = f'"{",".join(str(v) for v in value)}"'
        else:
            value_str = f'"{str(value)}"'

        # Try to find and update the setting
        pattern = rf"{setting_name}\s*=\s*.*"
        replacement = f"{setting_name} = {value_str}"

        # If the setting exists, update it
        if re.search(pattern, content):
            updated_content = re.sub(pattern, replacement, content)
            return updated_content
        else:
            # If setting doesn't exist, add it at the end
            return f"{content}\n{setting_name} = {value_str}\n"

    # Embed message functions
    async def embedinfo(self, interaction, message):
        """Send an info embed message"""
        embed = discord.Embed(title="", description=message, color=0x00FF00)
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            # Response already sent, use followup
            await interaction.followup.send(embed=embed, ephemeral=True)

    async def embederror(self, interaction, message):
        """Send an error embed message"""
        embed = discord.Embed(title="", description=message, color=0xF50000)
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            # Response already sent, use followup
            await interaction.followup.send(embed=embed, ephemeral=True)

    # Commands
    @app_commands.command(name="setup", description="Setup Plex integration")
    @app_commands.describe(
        username="Plex username",
        password="Plex password",
        server_name="Plex server name",
        base_url="Plex base URL (optional)",
        save_token="Save token instead of credentials (recommended)",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(
        self,
        interaction: discord.Interaction,
        username: str,
        password: str,
        server_name: str,
        base_url: str = "",
        save_token: bool = True,
    ):
        """Command to setup Plex integration"""
        await interaction.response.defer(ephemeral=True)

        try:
            # Test connection
            account = MyPlexAccount(username, password)
            plex = account.resource(server_name).connect()

            # Read current settings
            content = self.read_settings_file()
            if not content:
                await self.embederror(
                    interaction,
                    "❌ Could not read settings file. Please check the logs for more information.",
                )
                return

            if save_token:
                # Save token
                content = self.update_setting(content, "PLEX_TOKEN", plex._token)
                content = self.update_setting(
                    content,
                    "PLEX_BASE_URL",
                    plex._baseurl if not base_url else base_url,
                )
                content = self.update_setting(content, "PLEX_SERVER_NAME", server_name)

                # Clear credentials
                content = self.update_setting(content, "PLEX_USER", "")
                content = self.update_setting(content, "PLEX_PASS", "")

                # Update local variables
                self.plex_token = plex._token
                self.plex_base_url = plex._baseurl if not base_url else base_url
                self.plex_server_name = server_name
                self.plex_user = ""
                self.plex_pass = ""
            else:
                # Save credentials
                content = self.update_setting(content, "PLEX_USER", username)
                content = self.update_setting(content, "PLEX_PASS", password)
                content = self.update_setting(content, "PLEX_SERVER_NAME", server_name)

                # Clear token
                content = self.update_setting(content, "PLEX_TOKEN", "")
                content = self.update_setting(content, "PLEX_BASE_URL", "")

                # Update local variables
                self.plex_user = username
                self.plex_pass = password
                self.plex_server_name = server_name
                self.plex_token = ""
                self.plex_base_url = ""

            # Enable Plex
            content = self.update_setting(content, "PLEX_ENABLED", True)
            self.plex_enabled = True

            # Write updated settings
            if not self.write_settings_file(content):
                await self.embederror(
                    interaction,
                    "❌ Could not write to settings file. Please check the logs for more information.",
                )
                return

            logger.info(f"Plex authentication updated:")
            logger.info(f"  → Server: {server_name}")
            logger.info(f"  → Auth method: {'Token' if save_token else 'Credentials'}")

            await self.embedinfo(
                interaction,
                "✅ Plex authentication details updated.\n"
                "Please restart the bot or reload the Plex cogs for the changes to take effect.",
            )
        except Exception as e:
            if "(429)" in str(e):
                await self.embederror(
                    interaction, "❌ Too many requests. Please try again later."
                )
            else:
                await self.embederror(
                    interaction, f"❌ Error connecting to Plex: {str(e)}"
                )
            logger.error(f"Error connecting to Plex: {e}")

    @app_commands.command(
        name="addrole", description="Add a role for automatic Plex invites"
    )
    @app_commands.describe(role="The role to add for automatic Plex invites")
    @app_commands.checks.has_permissions(administrator=True)
    async def addrole(self, interaction: discord.Interaction, role: discord.Role):
        """Command to add a role for automatic Plex invites"""
        # Check if role already exists
        if role.name in self.plex_roles:
            await self.embederror(
                interaction,
                f"❌ Rolle '{role.name}' ist bereits für automatische Plex-Einladungen konfiguriert.",
            )
            return

        # Add role to local list
        self.plex_roles.append(role.name)

        # Update settings.py
        content = self.read_settings_file()
        if not content:
            await self.embederror(
                interaction,
                "❌ Could not read settings file. Please check the logs for more information.",
            )
            return

        content = self.update_setting(content, "PLEX_ROLES", self.plex_roles)

        if not self.write_settings_file(content):
            await self.embederror(
                interaction,
                "❌ Could not write to settings file. Please check the logs for more information.",
            )
            return

        logger.info(f"Plex role added: '{role.name}'")

        await self.embedinfo(
            interaction,
            f"✅ Rolle '{role.name}' wurde für automatische Plex-Einladungen hinzugefügt.\n"
            "Bitte starte den Bot neu oder lade die Plex-Cogs neu, damit die Änderungen wirksam werden.",
        )

    @app_commands.command(
        name="removerole", description="Remove a role from automatic Plex invites"
    )
    @app_commands.describe(role="The role to remove from automatic Plex invites")
    @app_commands.checks.has_permissions(administrator=True)
    async def removerole(self, interaction: discord.Interaction, role: discord.Role):
        """Command to remove a role from automatic Plex invites"""
        # Check if role exists
        if role.name not in self.plex_roles:
            await self.embederror(
                interaction,
                f"❌ Rolle '{role.name}' ist nicht für automatische Plex-Einladungen konfiguriert.",
            )
            return

        # Remove role from local list
        self.plex_roles.remove(role.name)

        # Update settings.py
        content = self.read_settings_file()
        if not content:
            await self.embederror(
                interaction,
                "❌ Could not read settings file. Please check the logs for more information.",
            )
            return

        content = self.update_setting(content, "PLEX_ROLES", self.plex_roles)

        if not self.write_settings_file(content):
            await self.embederror(
                interaction,
                "❌ Could not write to settings file. Please check the logs for more information.",
            )
            return

        logger.info(f"Plex role removed: '{role.name}'")

        await self.embedinfo(
            interaction,
            f"✅ Rolle '{role.name}' wurde aus der automatischen Plex-Einladungsliste entfernt.\n"
            "Bitte starte den Bot neu oder lade die Plex-Cogs neu, damit die Änderungen wirksam werden.",
        )

    @app_commands.command(
        name="setuplibs", description="Setup Plex libraries for sharing"
    )
    @app_commands.describe(
        libraries="Comma-separated list of libraries to share (use 'all' for all libraries)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setuplibs(self, interaction: discord.Interaction, libraries: str):
        """Command to setup Plex libraries for sharing"""
        if not libraries:
            await self.embederror(interaction, "❌ Bibliotheksliste ist leer.")
            return

        # Clean up the library list
        library_list = [lib.strip() for lib in libraries.split(",")]
        self.plex_libs = library_list

        # Update settings.py
        content = self.read_settings_file()
        if not content:
            await self.embederror(
                interaction,
                "❌ Could not read settings file. Please check the logs for more information.",
            )
            return

        content = self.update_setting(content, "PLEX_LIBS", library_list)

        if not self.write_settings_file(content):
            await self.embederror(
                interaction,
                "❌ Could not write to settings file. Please check the logs for more information.",
            )
            return

        logger.info(f"Plex libraries updated:")
        if len(library_list) <= 5:
            logger.info(f"  → Libraries: {', '.join(library_list)}")
        else:
            logger.info(
                f"  → Libraries: {', '.join(library_list[:5])}... ({len(library_list)} total)"
            )

        await self.embedinfo(
            interaction,
            f"✅ Plex-Bibliotheken wurden aktualisiert: {', '.join(library_list)}\n"
            "Bitte starte den Bot neu oder lade die Plex-Cogs neu, damit die Änderungen wirksam werden.",
        )

    @app_commands.command(name="enable", description="Enable Plex integration")
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self, interaction: discord.Interaction):
        """Command to enable Plex integration"""
        # Check if already enabled
        if self.plex_enabled:
            await self.embederror(
                interaction, "❌ Plex-Integration ist bereits aktiviert."
            )
            return

        # Update local state
        self.plex_enabled = True

        # Update settings.py
        content = self.read_settings_file()
        if not content:
            await self.embederror(
                interaction,
                "❌ Could not read settings file. Please check the logs for more information.",
            )
            return

        content = self.update_setting(content, "PLEX_ENABLED", True)

        if not self.write_settings_file(content):
            await self.embederror(
                interaction,
                "❌ Could not write to settings file. Please check the logs for more information.",
            )
            return

        logger.info("Plex integration: Enabled")

        await self.embedinfo(
            interaction,
            "✅ Plex-Integration wurde aktiviert.\n"
            "Bitte starte den Bot neu oder lade die Plex-Cogs neu, damit die Änderungen wirksam werden.",
        )

    @app_commands.command(name="disable", description="Disable Plex integration")
    @app_commands.checks.has_permissions(administrator=True)
    async def disable(self, interaction: discord.Interaction):
        """Command to disable Plex integration"""
        # Check if already disabled
        if not self.plex_enabled:
            await self.embederror(
                interaction, "❌ Plex-Integration ist bereits deaktiviert."
            )
            return

        # Update local state
        self.plex_enabled = False

        # Update settings.py
        content = self.read_settings_file()
        if not content:
            await self.embederror(
                interaction,
                "❌ Could not read settings file. Please check the logs for more information.",
            )
            return

        content = self.update_setting(content, "PLEX_ENABLED", False)

        if not self.write_settings_file(content):
            await self.embederror(
                interaction,
                "❌ Could not write to settings file. Please check the logs for more information.",
            )
            return

        logger.info("Plex integration: Disabled")

        await self.embedinfo(
            interaction,
            "✅ Plex-Integration wurde deaktiviert.\n"
            "Bitte starte den Bot neu oder lade die Plex-Cogs neu, damit die Änderungen wirksam werden.",
        )

    async def cog_load(self):
        """Associate commands with a specific guild."""
        guild = discord.Object(GUILD_ID)
        self.bot.tree.add_command(self.setup, guild=guild)
        self.bot.tree.add_command(self.addrole, guild=guild)
        self.bot.tree.add_command(self.removerole, guild=guild)
        self.bot.tree.add_command(self.setuplibs, guild=guild)
        self.bot.tree.add_command(self.enable, guild=guild)
        self.bot.tree.add_command(self.disable, guild=guild)


async def setup(bot):
    await bot.add_cog(PlexSettings(bot))
    logger.debug("Plex settings module loaded successfully")
