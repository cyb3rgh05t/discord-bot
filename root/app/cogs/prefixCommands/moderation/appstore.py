import discord
from discord.ext import commands


class StoreLinkCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="storemessage", help="Send store link embed")
    @commands.has_permissions(administrator=True)
    async def storemessage(self, ctx):
        try:
            embed = discord.Embed(color=discord.Color.dark_gray())
            embed.add_field(
                name="<:store:1312507116208128020> StreamNet Store",
                value=(
                    "<:icon_reply:1312507800689311854>Downloader App Code: 732041\n"
                    "<:icon_reply:1312507800689311854>[Download Link](https://aftv.news/732041)"
                ),
                inline=False,
            )

            await ctx.send(embed=embed)
        except Exception as error:
            await ctx.send("Ein Fehler ist aufgetreten.")
            print(f"Error in storelink command: {error}")


async def setup(bot):
    await bot.add_cog(StoreLinkCommand(bot))
