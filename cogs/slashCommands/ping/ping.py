import discord
from discord.ext import commands
from discord import app_commands
from config.settings import GUILD_ID
from cogs.helpers.logger import logger


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)  # Convert latency to ms
        await interaction.response.send_message(f"Pong! Latency is {latency}ms.")

    async def cog_load(self):
        """Associate commands with a specific guild."""
        guild = discord.Object(GUILD_ID)  # Replace with your GUILD_ID
        self.bot.tree.add_command(self.ping, guild=guild)


async def setup(bot):
    await bot.add_cog(General(bot))
