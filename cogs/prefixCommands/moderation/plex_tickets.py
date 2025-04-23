import discord
from discord.ext import commands
from cogs.helpers.logger import logger


class PlexTicketSetupMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="plexticketsmessage", help="Send a plex ticket setup message."
    )
    @commands.has_permissions(administrator=True)
    async def plexticketsmessage(self, ctx):
        try:
            # Send the ticket setup message
            await ctx.send(
                content=(
                    "===============================================\n\n"
                    "<:help:1312507464188690462> **PLEX SUPPORT**\n"
                    "<:icon_reply:1312507800689311854> jeglicher Support für StreamNet Plex.\n\n"
                    "<:invite:1312507843437396060> **PLEX INVITE**\n"
                    "<:icon_reply:1312507800689311854> Anfrage Button für eine StreamNet Plex Einladung.\n\n"
                    "<:movie:1312507878849904752> **PLEX MEDIA**\n"
                    "<:icon_reply:1312507800689311854> Probleme wie : Falsche Tonspuren, Schlechter Ton, Schlechte Qualität, usw....."
                )
            )
        except Exception as error:
            # Handle any errors
            await ctx.send("Some Error Occurred")
            # Log the error if you have a logger setup
            logger.error(f"Error sending ticket setup message: {error}")


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(PlexTicketSetupMessage(bot))
    logger.debug("PlexTicketSetupMessage cog loaded.")
