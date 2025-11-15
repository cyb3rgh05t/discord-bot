"""
Dashboard view - Main overview page
Shows bot status, statistics, and quick info
"""

from flask import Blueprint, render_template
from flask_login import login_required
from web.utils.decorators import auth_required
from web.utils.bot_interface import get_bot_status, get_bot_stats

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@auth_required
def index():
    """Main dashboard page"""
    bot_status = get_bot_status()
    bot_stats = get_bot_stats()

    return render_template(
        "dashboard/index.html", bot_status=bot_status, bot_stats=bot_stats
    )
