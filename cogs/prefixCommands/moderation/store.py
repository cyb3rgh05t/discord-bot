import discord
from discord.ext import commands
from cogs.helpers.logger import logger


class AppStoreMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="appstore", help="Send the App Store channel message.")
    @commands.has_permissions(administrator=True)
    async def appstore(self, ctx):
        """Send the App Store channel message."""
        try:
            await ctx.send(
                content=(
                    "=======================================\n\n"
                    "<:store:1312507116208128020> **StreamNet Store**\n\n"
                    "Hol dir unseren App Store direkt auf dein Android Gerät, lade dir deine lieblings **StreamNet TV App** runter und geniesse das streaming Erlebnis."
                )
            )
        except Exception as error:
            await ctx.send("Some Error Occurred")
            print(f"Error sending app store message: {error}")


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(AppStoreMessage(bot))
