import discord
from discord.ext import commands
from cogs.helpers.logger import logger


class TvTicketSetupMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tvticketsmessage", help="Send a tv ticket setup message.")
    @commands.has_permissions(administrator=True)
    async def tvticketsmessage(self, ctx):
        try:
            # Send the ticket setup message
            await ctx.send(
                content=(
                    "===============================================\n\n"
                    "<:help:1312507464188690462> **APP SUPPORT**\n"
                    "<:icon_reply:1312507800689311854> jeglicher Support für die StreamNet TV App.\n\n"
                    "<:invite:1312507843437396060> **ABO / HAUSHALT**\n"
                    "<:icon_reply:1312507800689311854> ABO verlängern oder stornieren - Mehrere Haushälte hinzufügen.\n\n"
                    "<:movie:1312507878849904752> **LIVE TV / VOD**\n"
                    "<:icon_reply:1312507800689311854> Live TV und VOD Probleme"
                )
            )
        except Exception as error:
            # Handle any errors
            await ctx.send("Some Error Occurred")
            # Log the error if you have a logger setup
            logger.error(f"Error sending ticket setup message: {error}")


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(TvTicketSetupMessage(bot))
    logger.debug("TvTicketSetupMessage cog loaded.")
