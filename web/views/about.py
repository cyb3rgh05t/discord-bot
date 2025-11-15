"""
About page blueprint
Displays version info, system info, and support links
"""

from flask import Blueprint, render_template
from web.utils.bot_interface import get_bot_status, get_bot_stats
from web.utils.decorators import auth_required
import platform
import os
import psutil

about_bp = Blueprint("about", __name__, url_prefix="/about")


@about_bp.route("/")
def index():
    """Display about page"""

    # Get bot info
    bot_status = get_bot_status()
    bot_stats = get_bot_stats()

    # Get system info
    system_info = {
        "os": platform.system(),
        "os_version": platform.release(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "total_memory": round(psutil.virtual_memory().total / (1024**3), 2),  # GB
    }

    # Get version from file
    version_file = os.path.join(os.path.dirname(__file__), "..", "..", "version.txt")
    try:
        with open(version_file, "r") as f:
            version = f.read().strip()
    except:
        version = "unknown"

    return render_template(
        "about/index.html",
        bot_status=bot_status,
        bot_stats=bot_stats,
        system_info=system_info,
        version=version,
        page="about",
    )
