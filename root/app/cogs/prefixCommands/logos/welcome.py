import discord
import logging
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="welcome", help="Sends the welcome channel logo.")
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        """Send a welcome channel logo as an image attachment and delete the command message."""
        try:
            # Delete the user's command message
            await ctx.message.delete()

            # Replace with the path to your local image file
            image_path = "./config/images/streamnet.png"

            # Create a file attachment
            file = discord.File(image_path, filename="streamnet.png")

            # Send the image in the channel
            await ctx.send(file=file)

        except Exception as e:
            await ctx.send("Some Error Occurred")
            # Log the error to the console
            print(f"Error sending the welcome picture: {e}")


async def setup(bot):
    await bot.add_cog(Welcome(bot))
    logging.info("Welcome Logo cog loaded.")
