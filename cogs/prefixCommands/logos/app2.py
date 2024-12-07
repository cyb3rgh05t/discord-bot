import discord
import logging
from discord.ext import commands


class App2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="app2", help="Sends the app channel logo.")
    @commands.has_permissions(administrator=True)
    async def app2(self, ctx):
        """Send a app channel logo as an image attachment and delete the command message."""
        try:
            # Delete the user's command message
            await ctx.message.delete()

            # Replace with the path to your local image file
            image_path = "./config/images/app2.png"

            # Create a file attachment
            file = discord.File(image_path, filename="app2.png")

            # Send the image in the channel
            await ctx.send(file=file)

        except Exception as e:
            await ctx.send("Some Error Occurred")
            # Log the error to the console
            print(f"Error sending the app picture: {e}")


async def setup(bot):
    await bot.add_cog(App2(bot))
    logging.info("App Logo cog loaded.")
