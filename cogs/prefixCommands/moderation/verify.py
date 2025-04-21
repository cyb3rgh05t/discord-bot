import discord
from discord.ext import commands
from cogs.helpers.logger import logger


class VerifyMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="verifymessage", help="Send a verification message with an image."
    )
    @commands.has_permissions(administrator=True)
    async def verifymessage(self, ctx):
        try:
            # Path to the image file
            image_path = (
                "./config/images/verify.png"  # Replace with your actual file path
            )

            # Create a Discord File object for the image
            file = discord.File(image_path, filename="verify.png")

            # Send the message with the file
            await ctx.send(
                content=(
                    "➡️ ... warte bis du vom Admin verifiziert wurdest <:approved:995615632961847406>\n\n"
                    "➡️ Bitte erfülle das CAPTCHA in deinen DM's ...\n"
                    "(<:rejected:995614671128244224> Bitte stelle sicher, dass Direktnachrichten aktiviert sind! "
                    "Du kannst deine Direktnachrichten wieder deaktivieren, sobald du das Captcha abgeschlossen hast.)"
                ),
                file=file,
            )
        except Exception as error:
            # Handle any errors
            await ctx.send("Some Error Occurred")
            # Log the error if you have a logger setup
            print(f"Error sending verification message: {error}")


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(VerifyMessage(bot))
