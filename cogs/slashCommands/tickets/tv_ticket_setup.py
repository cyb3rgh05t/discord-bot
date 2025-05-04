import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from config.settings import GUILD_ID, DATABASE_PATH
from cogs.helpers.logger import logger
from cogs.slashCommands.tickets.base_ticket_setup import BaseTicketSetup


class TVTicketSetup(BaseTicketSetup):
    """Cog for setting up the TV ticket system"""

    def __init__(self, bot):
        super().__init__(
            bot=bot, db_path=f"{DATABASE_PATH}/ticket_system.db", table_prefix="tv"
        )

    @app_commands.command(
        name="tvticketsetup", description="Setup your TV ticket panel"
    )
    @app_commands.describe(
        channel="Select a ticket creation channel",
        category="Select the ticket channels parent category",
        transcripts="Select a ticket transcripts channel",
        helpers="Select the ticket helpers role",
        everyone="Provide the @everyone role",
        description="Set a description of the ticket system",
        firstbutton="Select a name for your first button",
        secondbutton="Select a name for your second button",
        thirdbutton="Select a name for your third button",
    )
    async def tvticketsetup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        category: discord.CategoryChannel,
        transcripts: discord.TextChannel,
        helpers: discord.Role,
        everyone: discord.Role,
        description: str,
        firstbutton: str,
        secondbutton: str,
        thirdbutton: str,
    ):
        """Set up the TV ticket system."""
        guild = interaction.guild

        try:
            # Define button names and emojis
            buttons = [firstbutton, secondbutton, thirdbutton]
            emojis = [
                "<:help:1312507464188690462>",
                "<:invite:1312507843437396060>",
                "<:movie:1312507878849904752>",
            ]  # Replace with your preferred emojis

            # Create buttons
            class TicketButtons(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                    for i, button_name in enumerate(buttons):
                        self.add_item(
                            discord.ui.Button(
                                label=button_name,
                                custom_id=f"tv_{button_name}",
                                style=[
                                    discord.ButtonStyle.danger,
                                    discord.ButtonStyle.secondary,
                                    discord.ButtonStyle.success,
                                ][i],
                                emoji=emojis[i],
                            )
                        )

            # Create embed with TV specifics
            embed = discord.Embed(
                title=f"{guild.name} | Live TV Ticket System",
                description=description,
                color=discord.Color.random(),
            )
            embed.set_thumbnail(
                url="https://github.com/cyb3rgh05t/brands-logos/blob/master/StreamNet/club/discord/s_tv.png?raw=true"
            )
            # Send the message to the specified channel
            ticket_message = await channel.send(embed=embed, view=TicketButtons())

            # Save the panel to the database
            self.save_ticket_panel(
                guild.id,
                channel.id,
                ticket_message.id,
                category.id,
                transcripts.id,
                helpers.id,
                everyone.id,
                description,
                buttons,
            )

            await interaction.response.send_message(
                "TV ticket system setup successfully!", ephemeral=True
            )
            logger.info(f"TV ticket system setup complete for guild {guild.name}")

        except Exception as e:
            logger.error(f"Error during TV ticket setup: {e}")
            await interaction.response.send_message(
                f"An error occurred while setting up the TV ticket system: {str(e)}",
                ephemeral=True,
            )

    @commands.Cog.listener()
    async def on_ready(self):
        """Reinitialize ticket panels for all guilds on bot startup."""
        for guild in self.bot.guilds:
            await self.reinitialize_ticket_panel(guild)

    async def cog_load(self):
        """Associate commands with a specific guild."""
        guild = discord.Object(GUILD_ID)
        self.bot.tree.add_command(self.tvticketsetup, guild=guild)


async def setup(bot):
    await bot.add_cog(TVTicketSetup(bot))
    logger.debug("TVTicketSetup cog loaded.")
