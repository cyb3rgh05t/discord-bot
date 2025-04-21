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
)
from cogs.helpers.logger import logger  # Import the pre-configured logger


# Get version information
def get_version():
    """Reads the version from version.txt."""
    try:
        with open("version.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "unknown"


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)

        self.synced_guilds = set()  # Track synced guilds

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
            logger.info(f"Found guild '{guild_details.name}' (ID: {guild_details.id}).")
        except discord.NotFound:
            logger.error(
                f"Guild with ID {GUILD_ID} not found. Ensure the bot is added to the guild."
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
        logger.info("Loaded all extensions (cogs).")

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
            logger.error(f"Error syncing commands to guild '{guild.name}': {e}")

    async def sync_commands(self, guild):
        """Sync commands for a specific guild."""
        try:
            synced = await self.tree.sync(guild=guild)
            self.synced_guilds.add(guild.id)
            logger.info(f"Synced {len(synced)} commands to guild '{guild.id}'.")
            logger.debug(f"Synced commands: {[cmd.name for cmd in synced]}")
        except Exception as e:
            logger.error(f"Error syncing commands to guild '{guild.id}': {e}")

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
    logger.info(f"Starting Bot {version}...")

    # Create bot instance
    bot = MyBot()

    # Add commands to the bot
    bot.add_command(sync)
    bot.add_command(list_cogs)
    bot.add_command(list_guilds)
    bot.add_command(list_commands)

    # Run the bot
    bot.run(BOT_TOKEN)
