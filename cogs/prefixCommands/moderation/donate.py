import discord
from discord.ext import commands
from cogs.helpers.logger import logger


class DonationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="donatemessage", help="Send a donate channel message.")
    @commands.has_permissions(administrator=True)
    async def donatemessage(self, ctx):
        """Send the donation message."""
        try:
            await ctx.send(
                content=(
                    "=======================================\n\n"
                    "🚨 **HELP2STAYONLINE** 🚨\n\n"
                    "**StreamNet Plex** ist mein **Hobby**, doch habe ich und werde noch viel **Arbeit** reinstecken, "
                    "deshalb bitte ich euch User mir manschmal zu helfen in dem ihr spendet damit die **Server** "
                    "und **Premium Accounts** der Indexer bezahlt werden koennen, um euch das **beste Erlebnis** zu "
                    "präsentieren <:sclub:1312507027951452160> .\n\n"
                    "➡️  Die Server Wartungen und Accounts kommen auf ungefähr 120-130 € im Monat, diese möchte ich gerne so gut wie möglich durch Spenden abgedeckt haben.\n\n"
                    "➡️  Ist es die erste Spende für die Server Einladung <#825352124547989544> wird euch die **StreamNet..er** Rolle vergeben.\n\n"
                    "➡️  Nach einigen weiteren Spenden werde ich euch eine **Supporter** Rolle vergeben. *(kann bis zu 24h dauern)*\n\n"
                    "Durch diese Rolle sehe ich dass euch StreamNet gefällt und richtig bei Gelegenheit unterstützt.\n\n"
                    "➡️  Um eine Spende zu betätigen bitte ich euch über folgende Optionen zu spenden:"
                )
            )
        except Exception as error:
            await ctx.send("Some Error Occurred")
            print(f"Error sending donation message: {error}")

    @commands.command(name="paylink", help="Send donation payment links.")
    @commands.has_permissions(administrator=True)
    async def paylink(self, ctx):
        """Send the donation payment links embed."""
        try:
            embed = discord.Embed(color=discord.Color.dark_grey())
            embed.add_field(
                name="💗 Ko-Fi",
                value=(
                    "<:icon_reply:1312507800689311854> "
                    "[Support StreamNet Club](https://ko-fi.com/streamnetclub)"
                ),
                inline=False,
            )
            await ctx.send(embed=embed)
        except Exception as error:
            await ctx.send("Some Error Occurred")
            print(f"Error sending payment links: {error}")

    @commands.command(name="thankyou", help="Send a thank-you message.")
    @commands.has_permissions(administrator=True)
    async def thankyou(self, ctx):
        """Send a thank-you message."""
        try:
            await ctx.send(
                content="\n\nIch bedanke mich für den Support <:sclub:1312507027951452160>. "
            )
        except Exception as error:
            await ctx.send("Some Error Occurred")
            print(f"Error sending thank-you message: {error}")


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(DonationCommands(bot))
