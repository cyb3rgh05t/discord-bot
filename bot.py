import codecs
import sys
import discord
import os
import logging
from discord.ext import commands
from config.settings import (
    BOT_TOKEN,
    GUILD_ID,
    COMMAND_PREFIX,
    LOGGING_LEVEL,
    LOG_FILE,
    ASCII_LOGO,
    WELCOME_CHANNEL_ID,
    SYSTEM_CHANNEL_ID,
    TICKET_CATEGORY_ID,
    RULES_CHANNEL_ID,
    UNVERIFIED_ROLE,
    VERIFIED_ROLE,
    MEMBER_ROLE,
    STAFF_ROLE,
    DATABASE_PATH,
    KOFI_CHANNEL_ID,
)
from cogs.helpers.logger import logger  # Import the pre-configured logger

# Global channel map that will be populated with channel IDs and names
channel_map = {}


# Get version information
def get_version():
    """Reads the version from version.txt."""
    try:
        with open("version.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "unknown"


# Function to get channel name from global map - can be imported by other modules
def get_channel_name(channel_id):
    """Get channel name from channel map or return a formatted message if not found."""
    if not channel_id:
        return "Not set"

    # Check if we have it in our channel map
    if channel_id in channel_map:
        return channel_map[channel_id]

    return f"Unknown Channel (ID: {channel_id})"


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)

        self.synced_guilds = set()  # Track synced guilds

    async def get_channel_name(self, guild, channel_id, is_category=False):
        """Get channel or category name from ID and store in global map."""
        global channel_map

        if not channel_id:
            return "Not set"

        try:
            # Fetch channels from the guild
            if is_category:
                # For categories, we need to fetch all channels then filter
                channels = await guild.fetch_channels()
                for channel in channels:
                    if channel.id == channel_id and isinstance(
                        channel, discord.CategoryChannel
                    ):
                        # Store in global map
                        channel_map[channel_id] = f"#{channel.name}"
                        return f"#{channel.name}"
                return "Unknown Category"
            else:
                # For regular channels
                channel = await self.fetch_channel(channel_id)
                if channel:
                    # Store in global map
                    channel_map[channel_id] = f"#{channel.name}"
                    return f"#{channel.name}"
                return "Unknown Channel"
        except discord.NotFound:
            return "Channel not found"
        except discord.Forbidden:
            return "No access to channel"
        except Exception as e:
            logger.debug(f"Error retrieving channel name for ID {channel_id}: {e}")
            return "Error retrieving name"

    async def setup_hook(self):
        """Setup hook for initializing bot operations."""
        # Clear global commands to prevent Discord from auto-registering them
        self.tree.clear_commands(guild=None)
        logger.info("Cleared all global commands.")

        # Test debug logging
        logger.debug(
            "Setup hook initialized - if you see this, debug logging is working!"
        )

        guild = discord.Object(id=GUILD_ID)

        # Verify guild exists
        try:
            guild_details = await self.fetch_guild(GUILD_ID)
            logger.info(f"Found Guild '{guild_details.name}' (ID: {guild_details.id}).")

            # Get channel and category names
            system_channel_name = await self.get_channel_name(
                guild_details, SYSTEM_CHANNEL_ID
            )
            welcome_channel_name = await self.get_channel_name(
                guild_details, WELCOME_CHANNEL_ID
            )
            rules_channel_name = await self.get_channel_name(
                guild_details, RULES_CHANNEL_ID
            )
            ticket_category_name = await self.get_channel_name(
                guild_details, TICKET_CATEGORY_ID, is_category=True
            )
            kofi_channel_name = await self.get_channel_name(
                guild_details, KOFI_CHANNEL_ID
            )

            # Log bot configuration
            version = get_version()
            logger.info(f"Bot configuration loaded:")
            logger.info(f"  → Command Prefix: '{COMMAND_PREFIX}'")
            logger.info(f"  → Guild ID: '{GUILD_ID}'")
            logger.info(f"  → Logging Level: '{LOGGING_LEVEL}'")
            logger.info(f"  → Log File: '/{LOG_FILE}'")
            logger.info(
                f"  → Bot Token: {'[REDACTED]' if BOT_TOKEN else 'NOT SET - REQUIRED'}"
            )
            logger.info(f"  → Database Path: '/{DATABASE_PATH}'")
            logger.info("Discord Channel Configuration:")
            logger.info(f"  → System Channel ID: {SYSTEM_CHANNEL_ID}")
            logger.info(f"  → '{system_channel_name}'")
            logger.info(f"  → Welcome Channel ID: {WELCOME_CHANNEL_ID}")
            logger.info(f"  → '{welcome_channel_name}'")
            logger.info(f"  → Rules Channel ID: {RULES_CHANNEL_ID}")
            logger.info(f"  → '{rules_channel_name}'")
            logger.info(f"  → Kofi Channel ID: {KOFI_CHANNEL_ID}")
            logger.info(f"  → '{kofi_channel_name}'")
            logger.info("Discord Categorie Configuration:")
            logger.info(f"  → Ticket Category ID: {TICKET_CATEGORY_ID}")
            logger.info(f"  → '{ticket_category_name}'")
            logger.info("Discord Role Configuration:")
            logger.info(f"  → Unverified Role: '{UNVERIFIED_ROLE}'")
            logger.info(f"  → Verified Role: '{VERIFIED_ROLE}'")
            logger.info(f"  → Member Role: '{MEMBER_ROLE}'")
            logger.info(f"  → Staff Role: '{STAFF_ROLE}'")

        except discord.NotFound:
            logger.error(
                f"Guild with ID '{GUILD_ID}' not found. Ensure the bot is added to the guild."
            )
            raise

        # Dynamically load all cogs
        cogs_directory = "cogs"
        excluded_dirs = {
            "__pycache__",
            "helpers",
        }  # Added helpers to excluded directories

        for root, dirs, files in os.walk(cogs_directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]

            # Skip the helpers directory
            if "helpers" in root:
                continue

            for file in files:
                if file.endswith(".py"):
                    cog_path = os.path.join(root, file).replace(os.sep, ".")[:-3]
                    try:
                        await self.load_extension(cog_path)
                        logger.debug(f"Loaded cog: {cog_path}")
                    except Exception as e:
                        logger.error(f"Failed to load cog {cog_path}: {e}")
        logger.info("Loaded all extensions.")

        # Sync commands to the specific guild only
        await self.sync_commands(guild)

    async def on_guild_join(self, guild):
        """Handle bot joining a new guild."""
        if guild.id in self.synced_guilds:
            return  # Avoid duplicate syncing

        try:
            logger.info(f"Bot joined guild '{guild.name}' (ID: {guild.id}).")
            await self.sync_commands(guild)
        except Exception as e:
            logger.error(f"Error syncing commands to Guild '{guild.name}': {e}")

    async def sync_commands(self, guild):
        """Sync commands for a specific guild."""
        guild_details = await self.fetch_guild(GUILD_ID)
        try:
            synced = await self.tree.sync(guild=guild)
            self.synced_guilds.add(guild.id)
            logger.info(
                f"Synced {len(synced)} commands to Guild '{guild_details.name}' (ID: {guild.id})."
            )
            logger.debug(f"Synced commands: {[cmd.name for cmd in synced]}")
        except Exception as e:
            logger.error(f"Error syncing commands to Guild '{guild.id}': {e}")

    async def on_message(self, message):
        """Delete user's message after command execution."""
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        if ctx.valid:
            await self.process_commands(message)
            try:
                await message.delete()
            except discord.Forbidden:
                logger.warning(
                    f"Missing permissions to delete command message: {message.content}"
                )

    async def on_ready(self):
        """Event fired when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Bot is ready and connected to Discord!")
        logger.debug("Debug test message - checking if debug logs are visible")


@commands.command(name="sync", help="Manually sync slash commands.")
async def sync(ctx):
    """Manually sync slash commands."""
    try:
        guild = discord.Object(id=ctx.guild.id)
        synced = await ctx.bot.tree.sync(guild=guild)
        await ctx.send(f"Synced {len(synced)} commands to this guild.")
    except Exception as e:
        logger.error(f"Error during manual sync: {e}")
        await ctx.send(f"An error occurred: {e}")


@commands.command(name="list_guilds", help="List all guilds the bot is in.")
async def list_guilds(ctx):
    """List all guilds the bot is in."""
    guilds = ctx.bot.guilds
    guild_list = "\n".join(f"{guild.name} (ID: {guild.id})" for guild in guilds)
    await ctx.send(f"Guilds the bot is in:\n{guild_list}")


@commands.command(name="list_commands", help="List all registered commands.")
async def list_commands(ctx):
    commands = [cmd.name for cmd in ctx.bot.tree.get_commands()]
    await ctx.send(f"Registered commands: {', '.join(commands)}")


@commands.command(name="list_cogs", help="List all loaded cogs.")
async def list_cogs(ctx):
    cogs = ctx.bot.cogs.keys()
    await ctx.send(f"Loaded cogs: {', '.join(cogs)}")


# Main program
if __name__ == "__main__":
    # Display ASCII logo and version
    version = get_version()
    logger.info("\n" + ASCII_LOGO)
    logger.info(f"Starting Discord Bot...")
    logger.info(f"Version {version}")

    # Create bot instance
    bot = MyBot()

    # Add commands to the bot
    bot.add_command(sync)
    bot.add_command(list_cogs)
    bot.add_command(list_guilds)
    bot.add_command(list_commands)

    # Run the bot
    bot.run(BOT_TOKEN)
