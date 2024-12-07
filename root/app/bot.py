import logging
import codecs
import sys
import discord
import os
from discord.ext import commands
from config.settings import (
    BOT_TOKEN,
    GUILD_ID,
    COMMAND_PREFIX,
    LOGGING_LEVEL,
    LOGGING_FORMAT,
    LOGGING_DATEFMT,
    ASCII_LOGO,
)
from cogs.server.server import setup as system_info_setup


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
        logging.info("Cleared all global commands.")

        guild = discord.Object(id=GUILD_ID)

        # Verify guild exists
        try:
            guild_details = await self.fetch_guild(GUILD_ID)
            logging.info(
                f"Found guild '{guild_details.name}' (ID: {guild_details.id})."
            )
        except discord.NotFound:
            logging.error(
                f"Guild with ID {GUILD_ID} not found. Ensure the bot is added to the guild."
            )
            raise

        # Dynamically load all cogs
        cogs_directory = "cogs"
        excluded_dirs = {"__pycache__"}

        for root, dirs, files in os.walk(cogs_directory):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]

            for file in files:
                if file.endswith(".py"):
                    cog_path = os.path.join(root, file).replace(os.sep, ".")[:-3]
                    try:
                        await self.load_extension(cog_path)
                        logging.debug(f"Loaded cog: {cog_path}")
                    except Exception as e:
                        logging.error(f"Failed to load cog {cog_path}: {e}")
        logging.info("Loaded all extensions (cogs).")

        # Sync commands to the specific guild only
        await self.sync_commands(guild)

    async def on_guild_join(self, guild):
        """Handle bot joining a new guild."""
        if guild.id in self.synced_guilds:
            return  # Avoid duplicate syncing

        try:
            logging.info(f"Bot joined guild '{guild.name}' (ID: {guild.id}).")
            await self.sync_commands(guild)
        except Exception as e:
            logging.error(f"Error syncing commands to guild '{guild.name}': {e}")

    async def sync_commands(self, guild):
        """Sync commands for a specific guild."""
        try:
            synced = await self.tree.sync(guild=guild)
            self.synced_guilds.add(guild.id)
            logging.info(f"Synced {len(synced)} commands to guild '{guild.id}'.")
            logging.info(f"Synced commands: {[cmd.name for cmd in synced]}")
        except Exception as e:
            logging.error(f"Error syncing commands to guild '{guild.id}': {e}")

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
                logging.warning(
                    f"Missing permissions to delete command message: {message.content}"
                )

    async def on_guild_join(self, guild):
        try:
            logging.info(f"Bot joined guild '{guild.name}' (ID: {guild.id}).")
            synced = await self.tree.sync(guild=guild)
            logging.info(
                f"Synced {len(synced)} commands to guild '{guild.name}' (ID: {guild.id})."
            )
        except Exception as e:
            logging.error(f"Error syncing commands to new guild: {e}")

    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        if ctx.valid:
            await self.process_commands(message)
            try:
                await message.delete()
            except discord.Forbidden:
                logging.warning(
                    f"Missing permissions to delete command message: {message.content}"
                )


@commands.command(name="sync", help="Manually sync slash commands.")
async def sync(ctx):
    """Manually sync slash commands."""
    try:
        guild = discord.Object(id=ctx.guild.id)
        synced = await ctx.bot.tree.sync(guild=guild)
        await ctx.send(f"Synced {len(synced)} commands to this guild.")
    except Exception as e:
        logging.error(f"Error during manual sync: {e}")
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


def get_version():
    """Reads the version from version.txt."""
    try:
        with open("version.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "unknown"


def configure_logging():
    """Configure logging based on settings."""
    version = get_version()
    logging_level = getattr(logging, LOGGING_LEVEL.upper(), logging.INFO)
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)
    handlers = []

    # UTF-8 Console handler
    class UTF8StreamHandler(logging.StreamHandler):
        def __init__(self, stream=None):
            super().__init__(stream=stream)
            if stream is None:
                stream = sys.stdout
            self.stream = codecs.getwriter("utf-8")(stream.buffer)

    console_handler = UTF8StreamHandler()
    handlers.append(console_handler)

    # Configure logging
    logging.basicConfig(
        level=logging_level,
        format=LOGGING_FORMAT,
        datefmt=LOGGING_DATEFMT,
        handlers=handlers,
    )

    # Display ASCII logo and version
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)
    logging.getLogger("discord.client").setLevel(logging.WARNING)
    logging.info("\n" + ASCII_LOGO)
    logging.info(f"Starting Bot {version}...")
    logging.info("Logging configured successfully.")


# Configure logging before initializing the bot
configure_logging()

# Instantiate the bot
bot = MyBot()

# Add commands to the bot
bot.add_command(sync)
bot.add_command(list_cogs)
bot.add_command(list_guilds)
bot.add_command(list_commands)

# Run the bot
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
