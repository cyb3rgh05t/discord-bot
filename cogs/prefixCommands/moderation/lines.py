import discord
from discord.ext import commands
from discord.ui import Button, View


class LinesCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="linesmessage", help="Send lines channel message with button"
    )
    @commands.has_permissions(administrator=True)
    async def linesmessage(self, ctx):
        try:
            # Define the button
            button = Button(
                label="STREAMNET TV TEST LINIE",
                custom_id="create_ticket",  # This is used for handling interaction
                style=discord.ButtonStyle.primary,  # Use primary style for interaction
            )

            # Create a view and add the button
            view = View()
            view.add_item(button)

            # Send the message with the button
            await ctx.send(
                content=(
                    "=======================================\n\n"
                    "Bist du an einer Test Linie für unseren <:stv:1312506945634177064> **LiveTV Service** interessiert?\n\n"
                    "➡️ Eröffne ein Ticket und fordere dir eine an.\n"
                    "=======================================\n\n"
                ),
                view=view,
            )
        except Exception as error:
            await ctx.send("Ein Fehler ist aufgetreten.")
            print(f"Error in lines command: {error}")


async def setup(bot):
    await bot.add_cog(LinesCommand(bot))
