import discord
from discord.ext import commands
from discord import app_commands
import os
import configparser
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from config.settings import GUILD_ID
from cogs.helpers.logger import logger  # Updated import

# Configuration file path
CONFIG_PATH = "config/plex_config.ini"
CONFIG_SECTION = "plex_settings"

# Ensure config directory exists
os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)


class PlexSettings(commands.Cog):
    """Commands for configuring Plex settings"""

    def __init__(self, bot):
        self.bot = bot

        # Initialize config
        self.config = configparser.ConfigParser()
        self.load_config()

        # Get settings
        self.plex_roles = self.get_config_value("plex_roles", [])
        if isinstance(self.plex_roles, str) and self.plex_roles:
            self.plex_roles = self.plex_roles.split(",")
        elif not isinstance(self.plex_roles, list):
            self.plex_roles = []

        self.plex_libs = self.get_config_value("plex_libs", ["all"])
        if isinstance(self.plex_libs, str) and self.plex_libs:
            self.plex_libs = self.plex_libs.split(",")
        elif not isinstance(self.plex_libs, list):
            self.plex_libs = ["all"]

    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(CONFIG_PATH):
            self.config.read(CONFIG_PATH)
            if not self.config.has_section(CONFIG_SECTION):
                self.config.add_section(CONFIG_SECTION)
        else:
            self.config.add_section(CONFIG_SECTION)
            self.save_config()

    def save_config(self):
        """Save configuration to file"""
        with open(CONFIG_PATH, "w") as configfile:
            self.config.write(configfile)

    def get_config_value(self, key, default=None):
        """Get a value from the configuration"""
        try:
            return self.config.get(CONFIG_SECTION, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def set_config_value(self, key, value):
        """Set a value in the configuration"""
        if not self.config.has_section(CONFIG_SECTION):
            self.config.add_section(CONFIG_SECTION)
        self.config.set(CONFIG_SECTION, key, str(value))
        self.save_config()

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

            if save_token:
                # Save token
                self.set_config_value("plex_token", plex._token)
                self.set_config_value(
                    "plex_base_url", plex._baseurl if not base_url else base_url
                )
                self.set_config_value("plex_server_name", server_name)

                # Clear credentials
                self.set_config_value("plex_user", "")
                self.set_config_value("plex_pass", "")
            else:
                # Save credentials
                self.set_config_value("plex_user", username)
                self.set_config_value("plex_pass", password)
                self.set_config_value("plex_server_name", server_name)

                # Clear token
                self.set_config_value("plex_token", "")
                self.set_config_value("plex_base_url", "")

            # Try to update settings.py if available
            try:
                settings_path = "config/settings.py"
                if os.path.exists(settings_path):
                    with open(settings_path, "r") as f:
                        content = f.read()

                    if save_token:
                        # Update token settings
                        if "PLEX_TOKEN" in content:
                            content = self.update_setting(
                                content, "PLEX_TOKEN", plex._token
                            )
                        else:
                            content += f'\nPLEX_TOKEN = "{plex._token}"\n'

                        if "PLEX_BASE_URL" in content:
                            content = self.update_setting(
                                content,
                                "PLEX_BASE_URL",
                                plex._baseurl if not base_url else base_url,
                            )
                        else:
                            content += f'\nPLEX_BASE_URL = "{plex._baseurl if not base_url else base_url}"\n'

                        if "PLEX_SERVER_NAME" in content:
                            content = self.update_setting(
                                content, "PLEX_SERVER_NAME", server_name
                            )
                        else:
                            content += f'\nPLEX_SERVER_NAME = "{server_name}"\n'
                    else:
                        # Update credential settings
                        if "PLEX_USER" in content:
                            content = self.update_setting(
                                content, "PLEX_USER", username
                            )
                        else:
                            content += f'\nPLEX_USER = "{username}"\n'

                        if "PLEX_PASS" in content:
                            content = self.update_setting(
                                content, "PLEX_PASS", password
                            )
                        else:
                            content += f'\nPLEX_PASS = "{password}"\n'

                        if "PLEX_SERVER_NAME" in content:
                            content = self.update_setting(
                                content, "PLEX_SERVER_NAME", server_name
                            )
                        else:
                            content += f'\nPLEX_SERVER_NAME = "{server_name}"\n'

                    with open(settings_path, "w") as f:
                        f.write(content)
            except Exception as e:
                logger.warning(f"Could not update settings.py: {e}")

            # Enable Plex
            self.set_config_value("plex_enabled", "True")

            await self.embedinfo(
                interaction,
                "✅ Plex authentication details updated.\n"
                "Please restart the bot or reload the Plex cogs for the changes to take effect.",
            )

            logger.info("Plex authentication details updated")
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

    def update_setting(self, content, setting_name, value):
        """Update a setting in settings.py"""
        import re

        # Try to match the setting with both single and double quotes
        pattern = rf'{setting_name}\s*=\s*[\'"].*?[\'"]'
        replacement = f'{setting_name} = "{value}"'

        # Replace the setting
        return re.sub(pattern, replacement, content)

    @app_commands.command(
        name="addrole", description="Add a role for automatic Plex invites"
    )
    @app_commands.describe(role="The role to add for automatic Plex invites")
    @app_commands.checks.has_permissions(administrator=True)
    async def addrole(self, interaction: discord.Interaction, role: discord.Role):
        """Command to add a role for automatic Plex invites"""
        # Load current roles
        plex_roles = self.plex_roles

        # Check if role already exists
        if role.name in plex_roles:
            await self.embederror(
                interaction,
                f"❌ Rolle '{role.name}' ist bereits für automatische Plex-Einladungen konfiguriert.",
            )
            return

        # Add role
        plex_roles.append(role.name)

        # Save roles
        self.set_config_value("plex_roles", ",".join(plex_roles))

        # Try to update settings.py if available
        try:
            settings_path = "config/settings.py"
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    content = f.read()

                if "PLEX_ROLES" in content:
                    content = self.update_setting(
                        content, "PLEX_ROLES", ",".join(plex_roles)
                    )
                else:
                    content += f'\nPLEX_ROLES = "{",".join(plex_roles)}"\n'

                with open(settings_path, "w") as f:
                    f.write(content)
        except Exception as e:
            logger.warning(f"Could not update settings.py: {e}")

        # Update instance variable
        self.plex_roles = plex_roles

        await self.embedinfo(
            interaction,
            f"✅ Rolle '{role.name}' wurde für automatische Plex-Einladungen hinzugefügt.\n"
            "Bitte starte den Bot neu oder lade die Plex-Cogs neu, damit die Änderungen wirksam werden.",
        )

        logger.info(f"Added role '{role.name}' for automatic Plex invites")

    @app_commands.command(
        name="removerole", description="Remove a role from automatic Plex invites"
    )
    @app_commands.describe(role="The role to remove from automatic Plex invites")
    @app_commands.checks.has_permissions(administrator=True)
    async def removerole(self, interaction: discord.Interaction, role: discord.Role):
        """Command to remove a role from automatic Plex invites"""
        # Load current roles
        plex_roles = self.plex_roles

        # Check if role exists
        if role.name not in plex_roles:
            await self.embederror(
                interaction,
                f"❌ Rolle '{role.name}' ist nicht für automatische Plex-Einladungen konfiguriert.",
            )
            return

        # Remove role
        plex_roles.remove(role.name)

        # Save roles
        self.set_config_value("plex_roles", ",".join(plex_roles))

        # Try to update settings.py if available
        try:
            settings_path = "config/settings.py"
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    content = f.read()

                if "PLEX_ROLES" in content:
                    content = self.update_setting(
                        content, "PLEX_ROLES", ",".join(plex_roles)
                    )
                else:
                    content += f'\nPLEX_ROLES = "{",".join(plex_roles)}"\n'

                with open(settings_path, "w") as f:
                    f.write(content)
        except Exception as e:
            logger.warning(f"Could not update settings.py: {e}")

        # Update instance variable
        self.plex_roles = plex_roles

        await self.embedinfo(
            interaction,
            f"✅ Rolle '{role.name}' wurde aus der automatischen Plex-Einladungsliste entfernt.\n"
            "Bitte starte den Bot neu oder lade die Plex-Cogs neu, damit die Änderungen wirksam werden.",
        )

        logger.info(f"Removed role '{role.name}' from automatic Plex invites")

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

        # Save libraries
        self.set_config_value("plex_libs", ",".join(library_list))

        # Try to update settings.py if available
        try:
            settings_path = "config/settings.py"
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    content = f.read()

                if "PLEX_LIBS" in content:
                    content = self.update_setting(
                        content, "PLEX_LIBS", ",".join(library_list)
                    )
                else:
                    content += f'\nPLEX_LIBS = "{",".join(library_list)}"\n'

                with open(settings_path, "w") as f:
                    f.write(content)
        except Exception as e:
            logger.warning(f"Could not update settings.py: {e}")

        # Update instance variable
        self.plex_libs = library_list

        await self.embedinfo(
            interaction,
            f"✅ Plex-Bibliotheken wurden aktualisiert: {', '.join(library_list)}\n"
            "Bitte starte den Bot neu oder lade die Plex-Cogs neu, damit die Änderungen wirksam werden.",
        )

        logger.info(f"Updated Plex libraries: {', '.join(library_list)}")

    @app_commands.command(name="enable", description="Enable Plex integration")
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self, interaction: discord.Interaction):
        """Command to enable Plex integration"""
        # Check if already enabled
        if self.get_config_value("plex_enabled", "False").lower() == "true":
            await self.embederror(
                interaction, "❌ Plex-Integration ist bereits aktiviert."
            )
            return

        # Enable Plex
        self.set_config_value("plex_enabled", "True")

        # Try to update settings.py if available
        try:
            settings_path = "config/settings.py"
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    content = f.read()

                if "PLEX_ENABLED" in content:
                    content = self.update_setting(content, "PLEX_ENABLED", "True")
                else:
                    content += "\nPLEX_ENABLED = True\n"

                with open(settings_path, "w") as f:
                    f.write(content)
        except Exception as e:
            logger.warning(f"Could not update settings.py: {e}")

        await self.embedinfo(
            interaction,
            "✅ Plex-Integration wurde aktiviert.\n"
            "Bitte starte den Bot neu oder lade die Plex-Cogs neu, damit die Änderungen wirksam werden.",
        )

        logger.info("Plex integration enabled")

    @app_commands.command(name="disable", description="Disable Plex integration")
    @app_commands.checks.has_permissions(administrator=True)
    async def disable(self, interaction: discord.Interaction):
        """Command to disable Plex integration"""
        # Check if already disabled
        if self.get_config_value("plex_enabled", "False").lower() != "true":
            await self.embederror(
                interaction, "❌ Plex-Integration ist bereits deaktiviert."
            )
            return

        # Disable Plex
        self.set_config_value("plex_enabled", "False")

        # Try to update settings.py if available
        try:
            settings_path = "config/settings.py"
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    content = f.read()

                if "PLEX_ENABLED" in content:
                    content = self.update_setting(content, "PLEX_ENABLED", "False")
                else:
                    content += "\nPLEX_ENABLED = False\n"

                with open(settings_path, "w") as f:
                    f.write(content)
        except Exception as e:
            logger.warning(f"Could not update settings.py: {e}")

        await self.embedinfo(
            interaction,
            "✅ Plex-Integration wurde deaktiviert.\n"
            "Bitte starte den Bot neu oder lade die Plex-Cogs neu, damit die Änderungen wirksam werden.",
        )

        logger.info("Plex integration disabled")

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
    logger.debug("PlexSettings cog loaded.")
