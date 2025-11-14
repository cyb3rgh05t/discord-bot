import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from typing import Optional


class PlexWalkthroughSteps:
    """Plex walkthrough steps inspired by Wizarr"""

    @staticmethod
    def step_1_welcome(
        server_name: str, user: discord.User
    ) -> tuple[discord.Embed, discord.ui.View]:
        """Step 1: What is Plex?"""
        embed = discord.Embed(
            title="🎬 Willkommen bei StreamNet Plex!",
            description=(
                f"**Hallo {user.mention}!**\n\n"
                f"Gute Nachrichten — Du hast jetzt Zugriff auf unsere **StreamNet VOD Bibliothek** über Plex!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            ),
            color=0xE5A00D,
        )

        embed.add_field(
            name="📺 Was ist Plex?",
            value=(
                "Plex ermöglicht es, Film- und Serienbibliotheken mit Freunden und "
                "Familie zu teilen. Du wurdest eingeladen — Willkommen!\n\u200b"
            ),
            inline=False,
        )

        embed.add_field(
            name="🎬 Was bekommst du?",
            value=(
                "• Zugriff auf ständig aktualisierte Filme und Serien\n"
                "• On-Demand ansehen oder für Offline herunterladen\n"
                "• Personalisierte Watchlists & Empfehlungen"
            ),
            inline=False,
        )

        embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
        )
        embed.set_footer(
            text=f"{server_name} • Schritt 1 von 3",
            icon_url="https://cdn.discordapp.com/emojis/1310635856318562334.png",
        )

        view = discord.ui.View()
        button = discord.ui.Button(
            label="Weiter →",
            style=discord.ButtonStyle.primary,
            custom_id="plex_step_2",
            emoji="▶️",
        )
        view.add_item(button)

        return embed, view

    @staticmethod
    def step_2_download(server_name: str) -> tuple[discord.Embed, discord.ui.View]:
        """Step 2: Download Plex Clients"""
        embed = discord.Embed(
            title="<:splex:1033460420587049021> Plex Clients herunterladen",
            description=(
                "**Plex funktioniert fast überall** — installiere die App auf deinen Lieblingsgeräten:\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            ),
            color=0xE5A00D,
        )

        # Mobile section
        embed.add_field(
            name="📱 Mobile",
            value=(
                "• [iOS](https://apps.apple.com/app/plex/id383457673) (iPhone, iPad)\n"
                "• [Android](https://play.google.com/store/apps/details?id=com.plexapp.android) (Phones, Tablets)"
            ),
            inline=False,
        )

        # Desktop section
        embed.add_field(
            name="🖥️ Desktop",
            value=(
                "• [Windows](https://www.plex.tv/media-server-downloads/#plex-app)\n"
                "• [macOS](https://www.plex.tv/media-server-downloads/#plex-app)\n"
                "• [Linux](https://www.plex.tv/media-server-downloads/#plex-app)"
            ),
            inline=False,
        )

        # Smart TV & Streaming
        embed.add_field(
            name="📺 Smart TV & Streaming",
            value=(
                "Apple TV • Fire TV • Roku • Chromecast\n"
                "Samsung TV • LG TV • Android TV"
            ),
            inline=False,
        )

        # Consoles & Web
        embed.add_field(
            name="🎮 Konsolen & Web",
            value=(
                "• PlayStation 4/5 • Xbox One/Series\n"
                "• [🌐 Web App](https://app.plex.tv/desktop/) (Direkt im Browser)"
            ),
            inline=False,
        )

        embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
        )
        # Remove broken image URL
        embed.set_footer(
            text=f"{server_name} • Schritt 2 von 3",
            icon_url="https://cdn.discordapp.com/emojis/1310635856318562334.png",
        )

        view = discord.ui.View()
        download_btn = discord.ui.Button(
            label="⬇️ Alle Clients anzeigen",
            style=discord.ButtonStyle.link,
            url="https://www.plex.tv/media-server-downloads/#plex-app",
        )
        next_btn = discord.ui.Button(
            label="Weiter →",
            style=discord.ButtonStyle.primary,
            custom_id="plex_step_3",
            emoji="▶️",
        )
        view.add_item(download_btn)
        view.add_item(next_btn)

        return embed, view

    @staticmethod
    def step_3_tips(server_name: str) -> tuple[discord.Embed, discord.ui.View]:
        """Step 3: Tips for best experience"""
        embed = discord.Embed(
            title="🎞️ Tipps für die beste Erfahrung",
            description=(
                "Plex verwendet manchmal niedrige Qualität oder zeigt eigene Werbung. "
                "So behebst du das:\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            ),
            color=0xE5A00D,
        )

        embed.add_field(
            name="1️⃣ Trailer & Extras deaktivieren",
            value="Einstellungen → Erfahrung → deaktiviere *Kinematische Trailer anzeigen*",
            inline=False,
        )

        embed.add_field(
            name="2️⃣ Originalqualität erzwingen",
            value="Einstellungen → Wiedergabe → stelle *Automatisch* auf *Original*",
            inline=False,
        )

        embed.add_field(
            name="3️⃣ Kabelverbindung nutzen",
            value="Verwende eine kabelgebundene Verbindung für ruckelfreies 4K (bei Smart-TVs)",
            inline=False,
        )

        embed.add_field(
            name="💡 Zusätzliche Tipps",
            value=(
                "• Erstelle Watchlists für deine Lieblingsinhalte\n"
                "• Nutze die Discover-Funktion für Empfehlungen\n"
                "• Downloads für Offline-Wiedergabe (mobil)\n"
                "• Passe Untertitel und Audio nach Bedarf an"
            ),
            inline=False,
        )
        embed.set_image(url="attachment://plex.png")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
        )
        embed.set_footer(
            text=f"{server_name} • Schritt 3 von 3",
            icon_url="https://cdn.discordapp.com/emojis/1310635856318562334.png",
        )

        view = discord.ui.View()
        plex_btn = discord.ui.Button(
            label="🎬 Zu Plex gehen",
            style=discord.ButtonStyle.link,
            url="https://app.plex.tv/desktop/",
        )
        finish_btn = discord.ui.Button(
            label="✅ Fertig!",
            style=discord.ButtonStyle.success,
            custom_id="plex_walkthrough_complete",
        )
        view.add_item(plex_btn)
        view.add_item(finish_btn)

        return embed, view


class PlexWalkthrough(commands.Cog):
    """Plex walkthrough wizard for new users"""

    def __init__(self, bot):
        self.bot = bot
        self.server_name = "StreamNet Plex"  # Will be loaded from config

        # Load server name from config if available
        try:
            from config.settings import PLEX_SERVER_NAME

            self.server_name = PLEX_SERVER_NAME
        except:
            pass

    async def send_walkthrough(self, user: discord.User):
        """Send the complete Plex walkthrough to a user"""
        try:
            # Send introduction message in separate DM
            intro_embed = discord.Embed(
                title="<:splex:1033460420587049021> StreamNet Plex Setup Guide",
                description=(
                    f"Ich helfe dir jetzt beim Einrichten von Plex!\n\n"
                    f"Dieser kurze Guide (3 Schritte) zeigt dir:\n"
                    f"• Was Plex ist und was du bekommst\n"
                    f"• Wo du die Apps herunterladen kannst\n"
                    f"• Tipps für die beste Qualität\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f'Klicke auf **"Los geht\'s!"** um zu starten.'
                ),
                color=0xE5A00D,
            )
            intro_embed.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
            )
            intro_embed.set_footer(
                text=f"{self.server_name} • Setup Guide",
                icon_url="https://cdn.discordapp.com/emojis/1310635856318562334.png",
            )

            intro_view = discord.ui.View()
            start_btn = discord.ui.Button(
                label="Los geht's!",
                style=discord.ButtonStyle.success,
                custom_id="plex_walkthrough_start",
                emoji="🚀",
            )
            intro_view.add_item(start_btn)

            await user.send(embed=intro_embed, view=intro_view)

            # Wait for user to click start button
            def check_start(interaction: discord.Interaction):
                return (
                    interaction.user.id == user.id
                    and interaction.data is not None
                    and interaction.data.get("custom_id") == "plex_walkthrough_start"
                )

            try:
                start_interaction = await self.bot.wait_for(
                    "interaction", timeout=600.0, check=check_start
                )
                await start_interaction.response.defer()
            except asyncio.TimeoutError:
                await user.send(
                    "⏳ Setup Guide Zeitüberschreitung. Du kannst jederzeit mit `/plex-walkthrough` neu starten."
                )
                return False

            # Step 1: Welcome
            embed1, view1 = PlexWalkthroughSteps.step_1_welcome(self.server_name, user)
            msg1 = await user.send(embed=embed1, view=view1)

            # Wait for user to click "Weiter" or timeout after 5 minutes
            def check(interaction: discord.Interaction):
                return (
                    interaction.user.id == user.id
                    and interaction.data is not None
                    and interaction.data.get("custom_id") == "plex_step_2"
                )

            try:
                interaction = await self.bot.wait_for(
                    "interaction", timeout=300.0, check=check
                )
                await interaction.response.defer()

                # Step 2: Download
                embed2, view2 = PlexWalkthroughSteps.step_2_download(self.server_name)
                msg2 = await user.send(embed=embed2, view=view2)

                # Wait for step 3
                def check2(interaction: discord.Interaction):
                    return (
                        interaction.user.id == user.id
                        and interaction.data is not None
                        and interaction.data.get("custom_id") == "plex_step_3"
                    )

                interaction2 = await self.bot.wait_for(
                    "interaction", timeout=300.0, check=check2
                )
                await interaction2.response.defer()

                # Step 3: Tips
                embed3, view3 = PlexWalkthroughSteps.step_3_tips(self.server_name)
                plex_banner = discord.File(
                    "config/images/plex.png", filename="plex.png"
                )
                msg3 = await user.send(file=plex_banner, embed=embed3, view=view3)

                # Wait for finish
                def check3(interaction: discord.Interaction):
                    return (
                        interaction.user.id == user.id
                        and interaction.data is not None
                        and interaction.data.get("custom_id")
                        == "plex_walkthrough_complete"
                    )

                interaction3 = await self.bot.wait_for(
                    "interaction", timeout=300.0, check=check3
                )
                await interaction3.response.send_message(
                    "<:splex:1033460420587049021> Setup abgeschlossen!\n\nViel Spaß mit StreamNet Plex! 🍿",
                    ephemeral=True,
                )

            except asyncio.TimeoutError:
                # User didn't respond in time
                await user.send(
                    "⏳ Zeitüberschreitung. Du kannst den Walkthrough jederzeit mit `/plex-walkthrough` neu starten."
                )

        except discord.Forbidden:
            # Can't send DM to user
            return False
        except Exception as e:
            print(f"Error sending walkthrough: {e}")
            return False

        return True

    @app_commands.command(
        name="plex-walkthrough", description="Zeige den Plex Setup-Guide an"
    )
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def walkthrough_command(self, interaction: discord.Interaction):
        """Manual command to start the walkthrough"""
        # In DMs, no need for confirmation message
        if interaction.guild is None:
            await interaction.response.defer(ephemeral=True)
            user = interaction.user
            if isinstance(user, discord.Member):
                user = await self.bot.fetch_user(user.id)
            await self.send_walkthrough(user)
        else:
            # In server, send confirmation
            await interaction.response.send_message(
                "📬 Ich sende dir den Plex Walkthrough per DM!", ephemeral=True
            )
            user = interaction.user
            if isinstance(user, discord.Member):
                user = await self.bot.fetch_user(user.id)
            await self.send_walkthrough(user)


async def setup(bot):
    await bot.add_cog(PlexWalkthrough(bot))
