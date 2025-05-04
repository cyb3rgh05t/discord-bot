import discord
from discord.ext import commands
from discord import app_commands
from config.settings import BOT_TOKEN, GUILD_ID
from cogs.helpers.logger import logger


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server.")
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = None,
    ):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(
                "You don't have permission to kick members.", ephemeral=True
            )
            return

        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(
                f"{member} has been kicked. Reason: {reason}"
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Failed to kick {member}. Error: {e}"
            )

    async def cog_load(self):
        """Associate commands with a specific guild."""
        guild = discord.Object(GUILD_ID)  # Replace with your GUILD_ID
        self.bot.tree.add_command(self.kick, guild=guild)


async def setup(bot):
    await bot.add_cog(Admin(bot))
