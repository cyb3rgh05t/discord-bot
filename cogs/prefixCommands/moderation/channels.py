import discord
from discord.ext import commands
from cogs.helpers.logger import logger


class TVChannelsMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="channelsmessage", help="Send the TV channel message.")
    @commands.has_permissions(administrator=True)
    async def channelsmessage(self, ctx):
        """Send the TV channel message with a file as a spoiler."""
        try:
            # Define the file path
            file_path = "config/files/channels.pdf"  # Replace with the actual file path
            file_name = "StreamNet_TV_Channels"  # Name to display for the file

            # Attach the file as a spoiler
            file = discord.File(file_path, filename=f"SPOILER_{file_name}")

            await ctx.send(
                content=(
                    "=======================================\n\n"
                    "Hier findest du eine Übersicht unserer <:stv:1312506945634177064> LiveTV Channels:\n\n"
                    "StreamNet TV <:stv:1312506945634177064> Channel Liste:"
                ),
                file=file,  # Attach the file to the message
            )
        except Exception as error:
            await ctx.send("Some Error Occurred")
            print(f"Error sending channels message: {error}")


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(TVChannelsMessage(bot))
