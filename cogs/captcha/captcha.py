import discord
from discord.ext import commands
from captcha.image import ImageCaptcha
import random
import string
import os
import logging
from config.settings import GUILD_ID, UNVERIFIED_ROLE, VERIFIED_ROLE
from cogs.helpers.logger import logger


class CaptchaSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.captchas = {}  # Stores user CAPTCHA data

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Assign 'Unverified' role and send CAPTCHA."""
        guild = member.guild

        logger.debug(
            f"on_member_join triggered for {member.name} in guild {guild.name}."
        )

        # Assign 'Unverified' role
        unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE)
        if unverified_role:
            try:
                await member.add_roles(
                    unverified_role,
                    reason="Assigning Unverified role for CAPTCHA verification.",
                )
                logger.info(f"Assigned '{UNVERIFIED_ROLE}' role to {member.name}.")
            except discord.Forbidden:
                logger.error(
                    f"Missing permissions to assign '{UNVERIFIED_ROLE}' role in guild {guild.name}."
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error when assigning '{UNVERIFIED_ROLE}' role: {e}"
                )
        else:
            logger.warning(f"'{UNVERIFIED_ROLE}' role not found in guild {guild.name}.")
            return

        # Generate CAPTCHA
        captcha_text = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        image = ImageCaptcha()
        image_path = f"captcha_{member.id}.png"
        image.write(captcha_text, image_path)

        # Store CAPTCHA data
        self.captchas[member.id] = {
            "text": captcha_text,
            "attempts": 0,
            "max_attempts": 3,
            "guild_id": guild.id,
        }
        logger.debug(f"Generated CAPTCHA for {member.name}: {captcha_text}")

        # Send CAPTCHA via DM
        embed = discord.Embed(
            title=f"Willkommen bei {guild.name}",
            description=f"Hi {member.mention},\n"
            f"um Zugriff auf **{guild.name}** zu erhalten, löse bitte das CAPTCHA unten!",
            color=discord.Color.random(),
        )
        embed.add_field(
            name="Was passiert wenn ich das Captcha nicht ausfülle?",
            value="Du wirst nach 3 Versuchen gekickt, um es erneut zu versuchen!",
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_footer(text="CAPTCHA Verification")

        try:
            # Send the embed first
            await member.send(embed=embed)
            # Then send the CAPTCHA image as a separate message
            await member.send(file=discord.File(image_path))
            await member.send("Bitte antworte mit der Lösung des CAPTCHAs.")
            logger.info(f"Sent CAPTCHA to {member.name} in DMs.")
        except discord.Forbidden:
            logger.warning(
                f"Could not send CAPTCHA to {member.name}. DMs might be disabled."
            )
            system_channel = guild.system_channel
            if system_channel:
                await system_channel.send(
                    f"{member.mention}, bitte stelle sicher, dass Direktnachrichten aktiviert sind! Du kannst deine Direktnachrichten wieder deaktivieren, sobald du das CAPTCHA abgeschlossen hast."
                )
        except Exception as e:
            logger.error(f"Unexpected error when sending CAPTCHA to {member.name}: {e}")
        finally:
            if os.path.exists(image_path):
                os.remove(image_path)
                logger.debug(f"Deleted CAPTCHA image at {image_path}.")
            else:
                logger.warning(f"CAPTCHA image {image_path} not found for deletion.")

    @commands.Cog.listener()
    async def on_message(self, message):
        logger.debug(f"Message received: {message.content} from {message.author}")
        """Validate CAPTCHA responses."""
        if message.author.bot or message.author.id not in self.captchas:
            return

        # Retrieve CAPTCHA data
        user_data = self.captchas[message.author.id]
        guild = self.bot.get_guild(user_data["guild_id"])
        if not guild:
            logger.error(f"Guild with ID {user_data['guild_id']} not found.")
            return

        if message.content.strip().upper() == user_data["text"].upper():
            # CAPTCHA solved
            del self.captchas[message.author.id]
            embed = discord.Embed(
                title="✅ CAPTCHA Solved!",
                description=f"Willkommen, {message.author.mention}! Du hast das CAPTCHA erfolgreich ausgefüllt!",
                color=discord.Color.green(),
            )
            embed.add_field(
                name=f"Dir wurde Zugriff auf **{guild.name}** gewährt.",
                value="<#694495838013095967>",
            )
            embed.set_thumbnail(url=guild.icon.url)
            await message.author.send(embed=embed)

            # Update roles
            member = guild.get_member(message.author.id)
            unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE)
            verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE)
            if member:
                if unverified_role:
                    await member.remove_roles(unverified_role)
                if verified_role:
                    await member.add_roles(verified_role)
        else:
            # Incorrect CAPTCHA
            user_data["attempts"] += 1
            if user_data["attempts"] >= user_data["max_attempts"]:
                # Kick user
                await message.author.send(
                    "❌ Du hast das CAPTCHA nicht erfolgreich ausgefüllt! Bitte versuche es erneut!"
                )
                member = guild.get_member(message.author.id)
                if member:
                    await member.kick(reason="Failed CAPTCHA verification.")
                del self.captchas[message.author.id]
            else:
                # Notify remaining attempts
                await message.author.send(
                    f"❌ Ungültiges CAPTCHA! Du hast noch {user_data['max_attempts'] - user_data['attempts']} Versuche übrig."
                )


async def setup(bot):
    await bot.add_cog(CaptchaSystem(bot))
    logger.debug("CaptchaSystem cog loaded.")
