import discord
import logging
from discord.ext import commands


class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="channels", help="Sends the channels channel logo.")
    @commands.has_permissions(administrator=True)
    async def channels(self, ctx):
        """Send a channels channel logo as an image attachment and delete the command message."""
        try:
            # Delete the user's command message
            await ctx.message.delete()

            # Replace with the path to your local image file
            image_path = "./images/channels.png"

            # Create a file attachment
            file = discord.File(image_path, filename="channels.png")

            # Send the image in the channel
            await ctx.send(file=file)

        except Exception as e:
            await ctx.send("Some Error Occurred")
            # Log the error to the console
            print(f"Error sending the channels picture: {e}")


async def setup(bot):
    await bot.add_cog(Channels(bot))
    logging.info("Channels Logo cog loaded.")
