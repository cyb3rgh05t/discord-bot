import discord
from discord.ext import commands


class TVCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tvmessage", help="Send LiveTV channel message")
    @commands.has_permissions(administrator=True)
    async def tvmessage(self, ctx):
        try:
            message_content = (
                "=======================================\n\n"
                "**Willkommen bei <:stv:1312506945634177064> StreamNet TV - Ein All-In One IPTV Service.**\n\n"
                "=======================================\n\n"
                "Wie bekomme ich Zutritt zu **StreamNet TV** ?\n\n"
                "➡️ Befolge die Anweisungen für eine **TEST-LINIE** in <#1246173649124200518> !\n\n"
                "Viel Spass beim streamen.. <:stv:1312506945634177064>"
            )

            await ctx.send(content=message_content)
        except Exception as error:
            await ctx.send("Ein Fehler ist aufgetreten.")
            print(f"Error in tv command: {error}")


async def setup(bot):
    await bot.add_cog(TVCommand(bot))
