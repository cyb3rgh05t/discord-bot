import discord
from discord.ext import commands


class LiveLinkCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="liveabo", help="Send TV channel payment links embed")
    @commands.has_permissions(administrator=True)
    async def liveabo(self, ctx):
        try:
            embed = discord.Embed(
                title="<:stv:1312506945634177064> STREAMNET TV - ABO PREISE",
                color=discord.Color.dark_gray(),
            )

            embed.add_field(
                name="<:stv:1312506945634177064> 1 Jahr + 2 Geräte",
                value="<:icon_reply:1312507800689311854>150€",
                inline=False,
            )
            embed.add_field(
                name="<:stv:1312506945634177064> 1 Jahr + 1 Gerät",
                value="<:icon_reply:1312507800689311854>100€",
                inline=False,
            )
            embed.add_field(
                name="<:stv:1312506945634177064> 6 Monate + 1 Gerät",
                value="<:icon_reply:1312507800689311854>55€",
                inline=False,
            )
            embed.add_field(
                name="<:stv:1312506945634177064> 1 Monat + 1 Gerät",
                value="<:icon_reply:1312507800689311854>10€",
                inline=False,
            )
            embed.add_field(
                name="<:stv:1312506945634177064> + pro Gerät",
                value="<:icon_reply:1312507800689311854>50€",
                inline=False,
            )
            embed.add_field(
                name="💗 PAYPAL",
                value="<:icon_reply:1312507800689311854>[PayPal.me](https://paypal.me/IveFlammang)",
                inline=False,
            )

            await ctx.send(embed=embed)

        except Exception as error:
            await ctx.send("Ein Fehler ist aufgetreten.")
            print(f"Error in livelink command: {error}")


async def setup(bot):
    await bot.add_cog(LiveLinkCommand(bot))
