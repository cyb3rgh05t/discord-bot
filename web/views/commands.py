"""
Commands view - Display all bot commands
"""

from flask import Blueprint, render_template
from web.utils.decorators import auth_required
from web.utils.bot_interface import get_bot_instance

commands_bp = Blueprint("commands", __name__, url_prefix="/commands")


@commands_bp.route("/")
@auth_required
def index():
    """Commands listing page"""
    bot = get_bot_instance()

    slash_commands = []
    prefix_commands = []

    if bot:
        # Get slash commands
        if hasattr(bot, "tree") and bot.tree:
            for cmd in bot.tree.get_commands():
                slash_commands.append(
                    {
                        "name": cmd.name,
                        "description": cmd.description or "No description",
                        "type": "Slash Command",
                    }
                )

        # Get prefix commands
        if bot.commands:
            for cmd in bot.commands:
                prefix_commands.append(
                    {
                        "name": cmd.name,
                        "description": cmd.help or cmd.brief or "No description",
                        "aliases": list(cmd.aliases) if cmd.aliases else [],
                        "type": "Prefix Command",
                    }
                )

    # Sort alphabetically
    slash_commands.sort(key=lambda x: x["name"])
    prefix_commands.sort(key=lambda x: x["name"])

    stats = {
        "total": len(slash_commands) + len(prefix_commands),
        "slash": len(slash_commands),
        "prefix": len(prefix_commands),
    }

    return render_template(
        "commands/index.html",
        slash_commands=slash_commands,
        prefix_commands=prefix_commands,
        stats=stats,
    )
