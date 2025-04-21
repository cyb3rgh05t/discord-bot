import discord
from discord.ext import commands
from cogs.helpers.logger import logger


class TicketSetupMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticketsmessage", help="Send a ticket setup message.")
    @commands.has_permissions(administrator=True)
    async def ticketsmessage(self, ctx):
        try:
            # Send the ticket setup message
            await ctx.send(
                content=(
                    "===============================================\n\n"
                    "<:help:1312507464188690462> **PLEX SUPPORT**\n"
                    "<:icon_reply:1312507800689311854> jeglicher Support für StreamNet Plex oder StreamNet TV.\n\n"
                    "<:invite:1312507843437396060> **PLEX INVITE**\n"
                    "<:icon_reply:1312507800689311854> wie das Button Label schon sagt - Anfrage Button für eine StreamNet Einladung.\n\n"
                    "<:movie:1312507878849904752> **PLEX MEDIA**\n"
                    "<:icon_reply:1312507800689311854> Probleme wie : Falsche Tonspuren, Schlechter Ton, Schlechte Qualität, usw....."
                )
            )
        except Exception as error:
            # Handle any errors
            await ctx.send("Some Error Occurred")
            # Log the error if you have a logger setup
            print(f"Error sending ticket setup message: {error}")


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(TicketSetupMessage(bot))
