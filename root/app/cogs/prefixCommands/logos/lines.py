import discord
import logging
from discord.ext import commands


class Lines(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lines", help="Sends the lines channel logo.")
    @commands.has_permissions(administrator=True)
    async def lines(self, ctx):
        """Send a lines channel logo as an image attachment and delete the command message."""
        try:
            # Delete the user's command message
            await ctx.message.delete()

            # Replace with the path to your local image file
            image_path = "./images/lines.png"

            # Create a file attachment
            file = discord.File(image_path, filename="lines.png")

            # Send the image in the channel
            await ctx.send(file=file)

        except Exception as e:
            await ctx.send("Some Error Occurred")
            # Log the error to the console
            print(f"Error sending the lines picture: {e}")


async def setup(bot):
    await bot.add_cog(Lines(bot))
    logging.info("Lines Logo cog loaded.")
