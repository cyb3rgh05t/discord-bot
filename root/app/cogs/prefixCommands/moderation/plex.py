import discord
from discord.ext import commands


class PlexCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="plexmessage", help="Send Plex channel message")
    @commands.has_permissions(administrator=True)
    async def plexmessage(self, ctx):
        try:
            content = (
                "=======================================\n\n"
                "**Willkommen bei <:splex:1312507090442522819> StreamNet Plex - "
                "Ein täglich upgedateter Deutsch/Englisch Plex Media Server.**\n\n"
                "=======================================\n\n"
                "➡️  Wie bekomme ich Zutritt zum **StreamNet Plex** ?\n\n"
                "**1. **Befolge die Anweisungen für eine **EINLADUNG** in <#825352124547989544> !\n\n"
                "**2. **Folge den Anweisungen vom **<@825635238188285952>** !\n\n"
                "**3. **Akzeptiere die **PLEX-EINLADUNG** für StreamNet in deiner **PLEX EMAIL BOX**!\n"
                "    (für manuelle Aktivierung <#864928903000227850> )\n\n"
                "Viel Spass beim streamen.. <:splex:1312507090442522819>"
            )
            await ctx.send(content=content)
        except Exception as error:
            await ctx.send("Ein Fehler ist aufgetreten.")
            print(f"Error in plex command: {error}")


async def setup(bot):
    await bot.add_cog(PlexCommand(bot))
