import discord
from datetime import datetime, timedelta


async def embed_error(recipient, message, ephemeral=True):
    """Send an error embed message."""
    embed = discord.Embed(title="", description=message, color=0xF50000)
    await send_embed(recipient, embed, ephemeral)


async def embed_info(recipient, message, ephemeral=True):
    """Send an info embed message."""
    embed = discord.Embed(title="", description=message, color=0x00FF00)
    await send_embed(recipient, embed, ephemeral)


async def embed_title(recipient, message, ephemeral=True):
    """Send a titled embed message."""
    embed = discord.Embed(title=message, color=0x00FF00)
    await send_embed(recipient, embed, ephemeral)


async def embed_email(recipient, message, server_name, ephemeral=True):
    """Send an email embed message with expiration date."""
    time = (datetime.now() + timedelta(hours=24)).strftime("%d. %B %Y | %H:%M:%S")
    embed = discord.Embed(
        title=f"**{server_name} Invite**  🎟️", description=message, color=0x00FF00
    )
    embed.add_field(name="Gültig bis:", value=f"``{time}``", inline=False)
    await send_embed(recipient, embed, ephemeral)


async def embed_error_email(recipient, message, ephemeral=True):
    """Send an error embed message for email errors."""
    embed = discord.Embed(title="", description=message, color=0xF50000)
    embed.add_field(
        name="Mögliche Fehler:",
        value="``•`` Fehlerhaftes **EMail**-Format.\n``•`` Du bist schon bei **StreamNet** angemeldet.\n``•`` Die angegebene Email ist nicht bei **Plex** registriert.\n``•`` Username anstadt **EMail** angegeben",
        inline=False,
    )
    await send_embed(recipient, embed, ephemeral)


async def embed_info_accept(recipient, message, ephemeral=True):
    """Send an acceptance info embed message."""
    embed = discord.Embed(title="", description=message, color=0x00FF00)
    await send_embed(recipient, embed, ephemeral)


async def embed_custom(recipient, title, fields, ephemeral=True):
    """Send a custom embed message with fields."""
    embed = discord.Embed(title=title)
    for k in fields:
        embed.add_field(name=str(k), value=str(fields[k]), inline=True)
    await send_embed(recipient, embed, ephemeral)


async def send_info(recipient, message, ephemeral=True):
    """Send a plain text message."""
    if isinstance(recipient, discord.InteractionResponse):
        await recipient.send_message(message, ephemeral=ephemeral)
    elif (
        isinstance(recipient, discord.User)
        or isinstance(recipient, discord.member.Member)
        or isinstance(recipient, discord.Webhook)
    ):
        await recipient.send(message)


async def send_embed(recipient, embed, ephemeral=True):
    """Send an embed message to the appropriate recipient."""
    if (
        isinstance(recipient, discord.User)
        or isinstance(recipient, discord.member.Member)
        or isinstance(recipient, discord.Webhook)
    ):
        await recipient.send(embed=embed)
    elif isinstance(recipient, discord.InteractionResponse):
        await recipient.send_message(embed=embed, ephemeral=ephemeral)
