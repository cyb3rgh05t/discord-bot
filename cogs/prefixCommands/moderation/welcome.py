import discord
from discord.ext import commands
from cogs.helpers.logger import logger


class WelcomeMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="welcomemessage", help="Send a welcome message to the channel."
    )
    @commands.has_permissions(administrator=True)
    async def welcomemessage(self, ctx):
        try:
            # Send the welcome message
            await ctx.send(
                "=======================================\n\n"
                "**Willkommen bei <:sclub:1310635856318562334> StreamNet Club's Discord Server**\n\n"
                "=======================================\n\n"
                "➡️  Wie bekomme ich Zutritt zum **StreamNet Club Service** ?\n\n"
                "**1.** Bestätige die **REGELN** in <#694495838013095967> !\n\n"
                "**2.** Suche dir ein Projekt aus  <#1246852243680919592> oder <#1246852387570978818> !\n\n"
                "**3.** Folge den Anweisungen um Zutritt zu bekommen !\n\n"
                "**4.** Viel Spass beim streamen.. <:sclub:1310635856318562334>"
            )
        except Exception as error:
            # Handle any errors
            await ctx.send("Some Error Occurred")
            # Log the error if you have a logger setup
            print(f"Error sending welcome message: {error}")


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(WelcomeMessage(bot))
