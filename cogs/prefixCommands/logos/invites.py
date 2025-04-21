import discord
import logging
from discord.ext import commands
from cogs.helpers.logger import logger


class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="invites", help="Sends the invites channel logo.")
    @commands.has_permissions(administrator=True)
    async def invites(self, ctx):
        """Send a invites channel logo as an image attachment and delete the command message."""
        try:
            # Delete the user's command message
            await ctx.message.delete()

            # Replace with the path to your local image file
            image_path = "./config/images/invites.png"

            # Create a file attachment
            file = discord.File(image_path, filename="invites.png")

            # Send the image in the channel
            await ctx.send(file=file)

        except Exception as e:
            await ctx.send("Some Error Occurred")
            # Log the error to the console
            print(f"Error sending the invites picture: {e}")


async def setup(bot):
    await bot.add_cog(Invites(bot))
    logger.debug("Invites Logo cog loaded.")
