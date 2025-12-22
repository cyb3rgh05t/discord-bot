import codecs
import sys
import discord
import os
import logging
import threading
from datetime import datetime, timezone
from discord.ext import commands
from config.settings import (
    BOT_TOKEN,
    GUILD_ID,
    GUILD_NAME,
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
    ANNOUNCEMENT_ROLE,
    KOFI_CHANNEL_ID,
    ADMIN_USER_ID,
)
from cogs.helpers.logger import logger  # Import the pre-configured logger

# Suppress Discord.py debug logging (must be done before Discord initializes)
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
logging.getLogger("discord.http").setLevel(logging.WARNING)
logging.getLogger("discord.client").setLevel(logging.WARNING)

# Initialize databases
from cogs.helpers.database_init import (
    init_invites_db,
    init_ticket_system_db,
    init_plex_clients_db,
)

# Web UI imports (only if enabled)
try:
    from config.settings import WEB_ENABLED, WEB_HOST, WEB_PORT, WEB_VERBOSE_LOGGING

    if WEB_ENABLED:
        from api.main import app, set_bot_instance

        WEB_UI_AVAILABLE = True
    else:
        WEB_UI_AVAILABLE = False
except ImportError as e:
    WEB_UI_AVAILABLE = False
    logger.warning(f"Web UI dependencies not found. Web interface disabled. Error: {e}")

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
        intents.presences = True
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)

        self.synced_guilds = set()  # Track synced guilds
        self.start_time = None  # Track bot start time

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
                if channel and isinstance(
                    channel,
                    (
                        discord.TextChannel,
                        discord.VoiceChannel,
                        discord.StageChannel,
                        discord.ForumChannel,
                    ),
                ):
                    # Store in global map
                    channel_map[channel_id] = f"{channel.name}"
                    return f"{channel.name}"
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
        # Test debug logging
        logger.debug(
            "Setup hook initialized - if you see this, debug logging is working!"
        )

        guild = discord.Object(id=GUILD_ID)

        # Verify guild exists
        try:
            guild_details = await self.fetch_guild(int(GUILD_ID))
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
            print("---------------------------------------------")
            logger.info(f"Bot configuration loaded:")
            logger.info(f"  → Command Prefix: '{COMMAND_PREFIX}'")
            logger.info(f"  → Guild ID: '{GUILD_ID}'")
            logger.info(f"  → Guild Name: '{GUILD_NAME}'")
            logger.info(f"  → Logging Level: '{LOGGING_LEVEL}'")
            logger.info(f"  → Log File: '/{LOG_FILE}'")
            logger.info(
                f"  → Bot Token: {'[REDACTED]' if BOT_TOKEN else 'NOT SET - REQUIRED'}"
            )
            logger.info(f"  → Admin User ID: '{ADMIN_USER_ID}'")
            logger.info("Discord Channel Configuration:")
            logger.info(f"  → System Channel ID: '{SYSTEM_CHANNEL_ID}'")
            logger.info(f"  → System Channel Name:'{system_channel_name}'")
            logger.info(f"  → Welcome Channel ID: '{WELCOME_CHANNEL_ID}'")
            logger.info(f"  → Welcome Channel Name:'{welcome_channel_name}'")
            logger.info(f"  → Rules Channel ID: '{RULES_CHANNEL_ID}'")
            logger.info(f"  → Rules Channel Name:'{rules_channel_name}'")
            logger.info(f"  → Kofi Channel ID: '{KOFI_CHANNEL_ID}'")
            logger.info(f"  → Kofi Channel Name: '{kofi_channel_name}'")
            logger.info("Discord Categorie Configuration:")
            logger.info(f"  → Ticket Category ID: '{TICKET_CATEGORY_ID}'")
            logger.info(f"  → Ticket Category Name:'{ticket_category_name}'")
            logger.info("Discord Role Configuration:")
            logger.info(f"  → Unverified Role: '{UNVERIFIED_ROLE}'")
            logger.info(f"  → Verified Role: '{VERIFIED_ROLE}'")
            logger.info(f"  → Member Role: '{MEMBER_ROLE}'")
            logger.info(f"  → Staff Role: '{STAFF_ROLE}'")
            logger.info(f"  → Announcement Role: '{ANNOUNCEMENT_ROLE}'")
            print("---------------------------------------------")

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

        # Sync commands globally (for DM-enabled commands like /plex-walkthrough)
        try:
            global_synced = await self.tree.sync()
            logger.info(f"Synced {len(global_synced)} global commands.")
        except Exception as e:
            logger.error(f"Error syncing global commands: {e}")

        # Note: We only sync globally to avoid duplicates
        # Commands will be available both in guilds and DMs

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
        guild_details = await self.fetch_guild(int(GUILD_ID))
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
        # Record start time on first ready event
        if self.start_time is None:
            self.start_time = datetime.now(timezone.utc)
            logger.info(
                f"Bot start time recorded: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )

        if self.user:
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


@commands.command(
    name="syncglobal", help="Manually sync global slash commands (works in DMs)."
)
@commands.is_owner()
async def syncglobal(ctx):
    """Manually sync global slash commands."""
    try:
        synced = await ctx.bot.tree.sync()
        await ctx.send(
            f"Synced {len(synced)} global commands. May take up to 1 hour to appear in DMs."
        )
        logger.info(f"Synced {len(synced)} global commands.")
    except Exception as e:
        logger.error(f"Error during global sync: {e}")
        await ctx.send(f"An error occurred: {e}")


@commands.command(
    name="clearguild", help="Clear all guild-specific commands to remove duplicates."
)
@commands.is_owner()
async def clearguild(ctx):
    """Clear all guild-specific slash commands."""
    try:
        guild = discord.Object(id=ctx.guild.id)
        ctx.bot.tree.clear_commands(guild=guild)
        await ctx.bot.tree.sync(guild=guild)
        await ctx.send(
            f"Cleared all guild-specific commands from this guild. Global commands remain active."
        )
        logger.info(f"Cleared guild-specific commands from guild {ctx.guild.id}.")
    except Exception as e:
        logger.error(f"Error clearing guild commands: {e}")
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


def start_web_ui(bot_instance):
    """Start the FastAPI web UI in a separate thread."""
    if WEB_UI_AVAILABLE:
        try:
            # Set the bot instance for the web UI
            set_bot_instance(bot_instance)

            logger.info(f"Starting FastAPI on {WEB_HOST}:{WEB_PORT}")

            # Run Uvicorn with proper thread handling
            import uvicorn
            import asyncio

            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            config = uvicorn.Config(
                app,
                host=WEB_HOST,
                port=WEB_PORT,
                log_level="error" if not WEB_VERBOSE_LOGGING else "info",
                loop="asyncio",
            )
            server = uvicorn.Server(config)
            loop.run_until_complete(server.serve())
        except Exception as e:
            logger.error(f"Failed to start Web UI: {e}")
    else:
        logger.info("Web UI is disabled")


# Main program
if __name__ == "__main__":
    # Display ASCII logo and version
    version = get_version()
    logger.info("\n" + ASCII_LOGO)
    logger.info(f"Starting Discord Bot...")
    logger.info(f"Version {version}")

    # Initialize databases
    logger.info("Initializing databases...")
    os.makedirs("databases", exist_ok=True)

    # Import database initialization functions
    from cogs.helpers.database_init import (
        init_invites_db,
        init_ticket_system_db,
        init_plex_clients_db,
    )

    try:
        msg1 = init_invites_db()
        logger.info(f"  - {msg1}")
        msg2 = init_ticket_system_db()
        logger.info(f"  - {msg2}")
        msg3 = init_plex_clients_db()
        logger.info(f"  - {msg3}")
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")

    # Create bot instance
    bot = MyBot()

    # Add commands to the bot
    bot.add_command(sync)
    bot.add_command(syncglobal)
    bot.add_command(clearguild)
    bot.add_command(list_cogs)
    bot.add_command(list_guilds)
    bot.add_command(list_commands)

    # Start the web UI if enabled and available
    if WEB_UI_AVAILABLE and WEB_ENABLED:
        threading.Thread(target=start_web_ui, args=(bot,), daemon=True).start()
    # Run the bot
    bot.run(BOT_TOKEN)
