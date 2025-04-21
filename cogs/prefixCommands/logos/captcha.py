import discord
import logging
from discord.ext import commands
from cogs.helpers.logger import logger


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="verify", help="Sends the verify channel logo.")
    @commands.has_permissions(administrator=True)
    async def verify(self, ctx):
        """Send a verify channel logo as an image attachment and delete the command message."""
        try:
            # Delete the user's command message
            await ctx.message.delete()

            # Replace with the path to your local image file
            image_path = "./config/images/verify.png"

            # Create a file attachment
            file = discord.File(image_path, filename="verify.png")

            # Send the image in the channel
            await ctx.send(file=file)

        except Exception as e:
            await ctx.send("Some Error Occurred")
            # Log the error to the console
            print(f"Error sending the verify picture: {e}")


async def setup(bot):
    await bot.add_cog(Verify(bot))
    logger.debug("Verify Logo cog loaded.")
