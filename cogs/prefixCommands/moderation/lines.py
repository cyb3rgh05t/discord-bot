# cogs/prefixCommands/moderation/lines.py

import discord
from discord.ext import commands
from discord.ui import Button, View
from cogs.helpers.logger import logger


class LinesCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="linesmessage", help="Send lines channel message with button"
    )
    @commands.has_permissions(administrator=True)
    async def linesmessage(self, ctx):
        try:
            # Define the button - keep the custom_id="create_ticket" for test lines
            button = Button(
                label="LIVE TV TEST LINIE",
                custom_id="create_ticket",  # This will be handled by our new ticket system
                style=discord.ButtonStyle.secondary,
                emoji="<:stv:1312506945634177064>",  # Use your StreamNet TV emoji
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

            # Success message that will auto-delete
            success_msg = await ctx.send("Ticket button created successfully!")
            await success_msg.delete(delay=5)  # Delete after 5 seconds

            logger.info("TV Test Line button created successfully")

        except Exception as error:
            await ctx.send("Ein Fehler ist aufgetreten.")
            logger.error(f"Error in lines command: {error}")


async def setup(bot):
    await bot.add_cog(LinesCommand(bot))
    logger.debug("Lines command cog loaded.")
