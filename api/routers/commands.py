"""
Commands API router - Display all bot commands
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from api.routers.auth import get_current_user, User

router = APIRouter(tags=["commands"])


class SlashCommand(BaseModel):
    name: str
    description: str
    type: str = "Slash Command"


class PrefixCommand(BaseModel):
    name: str
    description: str
    aliases: List[str] = []
    type: str = "Prefix Command"


class CommandStats(BaseModel):
    total: int
    slash: int
    prefix: int


class CommandsResponse(BaseModel):
    slash_commands: List[SlashCommand]
    prefix_commands: List[PrefixCommand]
    stats: CommandStats


@router.get("/", response_model=CommandsResponse)
async def get_commands(current_user: User = Depends(get_current_user)):
    """Get all bot commands (slash and prefix)"""
    try:
        from api.main import bot_instance

        bot = bot_instance
        slash_commands = []
        prefix_commands = []

        if bot:
            # Get slash commands
            if hasattr(bot, "tree") and bot.tree:
                for cmd in bot.tree.get_commands():
                    slash_commands.append(
                        SlashCommand(
                            name=cmd.name,
                            description=cmd.description or "No description",
                        )
                    )

            # Get prefix commands
            if bot.commands:
                for cmd in bot.commands:
                    prefix_commands.append(
                        PrefixCommand(
                            name=cmd.name,
                            description=cmd.help or cmd.brief or "No description",
                            aliases=list(cmd.aliases) if cmd.aliases else [],
                        )
                    )

        # Sort alphabetically
        slash_commands.sort(key=lambda x: x.name)
        prefix_commands.sort(key=lambda x: x.name)

        stats = CommandStats(
            total=len(slash_commands) + len(prefix_commands),
            slash=len(slash_commands),
            prefix=len(prefix_commands),
        )

        return CommandsResponse(
            slash_commands=slash_commands,
            prefix_commands=prefix_commands,
            stats=stats,
        )

    except Exception as e:
        print(f"Error fetching commands: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
