import discord
import logging
from discord.ext import commands


class InviteCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="invitemessage", help="Send invite channel message")
    @commands.has_permissions(administrator=True)
    async def invitemessage(self, ctx):
        try:
            await ctx.send(
                content=(
                    "=======================================\n\n"
                    "**SPENDEN** sind das A und O damit dieses **Projekt** am Leben bleibt.\n\n"
                    "Deshalb frage ich für jede **Server Einladung** eine kleine **Spende** um die Server und alles was ansteht zu bezahlen...\n\n"
                    "➡️  Betätige eine **Spende** indem du den Anweisungen in <#912755161078849598> folgst.\n\n"
                    "➡️  Nach einer **Spende** eröffne ein **Invite-Ticket** in <#995631213995905094>, poste die Spenden-Bestätigung "
                    "und frage nach einer **StreamNet Einladung**. Nach Bestätigung des **Staff Teams** wird dir der <@825635238188285952> Bot per **DM** schreiben. "
                    "Folge diesen Anweisungen.\n\n"
                    "➡️  **NACHDEM** du hinzugefügt worden bist, kannst du die **EINLADUNG** in deiner **MAILBOX** *(Mailbox der Email welche du dem Bot angegeben hast)* akzeptieren.\n"
                    "***(sollte der Link in der email nicht klappen, dann kannst du die Einladung auch manuell akzeptieren. Mehr dazu im <#864928903000227850>***)"
                )
            )
        except Exception as error:
            await ctx.send("Ein Fehler ist aufgetreten.")
            print(f"Error in invite command: {error}")


async def setup(bot):
    await bot.add_cog(InviteCommand(bot))
