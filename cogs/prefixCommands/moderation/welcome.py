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
            # Create a styled plain text message
            styled_message = (
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🌟 **Willkommen auf unserem Discord Server** 🌟\n"
                "Wir freuen uns, dich in der StreamNet Club Community begrüßen zu dürfen!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🔑 **Wie bekomme ich Zutritt zum StreamNet Club Service?**\n\n"
                "Befolge diese einfachen Schritte:\n\n"
                "**<:tc_1:1364320674398732329>** Bestätige die **REGELN** in <#694495838013095967>\n\n"
                "**<:tc_2:1364320658179358920>** Suche dir ein Projekt aus <#1246852243680919592> oder <#1246852387570978818>\n\n"
                "**<:tc_3:1364320677565431830>** Folge den Anweisungen um Zutritt zu bekommen\n\n"
                "**<:tc_4:1364320663195619338>** Viel Spaß beim Streamen! <:sclub:1310635856318562334>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<:sclub:1310635856318562334> **{ctx.guild.name}** • Streaming leicht gemacht"
            )

            # Send the styled plain text message
            await ctx.send(styled_message)

        except Exception as error:
            # Handle any errors
            await ctx.send("Some Error Occurred")
            # Log the error if you have a logger setup
            logger.error(f"Error sending welcome message: {error}")


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(WelcomeMessage(bot))
    logger.debug("WelcomeMessage cog loaded.")
