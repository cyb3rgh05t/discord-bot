import discord
import logging
from discord.ext import commands
from cogs.helpers.logger import logger


class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rules", help="Sends the rules channel logo.")
    @commands.has_permissions(administrator=True)
    async def rules(self, ctx):
        """Send a rules channel logo as an image attachment and delete the command message."""
        try:
            # Delete the user's command message
            await ctx.message.delete()

            # Replace with the path to your local image file
            image_path = "./config/images/rules.png"

            # Create a file attachment
            file = discord.File(image_path, filename="rules.png")

            # Send the image in the channel
            await ctx.send(file=file)

        except Exception as e:
            await ctx.send("Some Error Occurred")
            # Log the error to the console
            print(f"Error sending the rules picture: {e}")


async def setup(bot):
    await bot.add_cog(Rules(bot))
    logger.debug("Rules Logo cog loaded.")
