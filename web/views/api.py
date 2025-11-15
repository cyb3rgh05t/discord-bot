"""
API endpoints for AJAX requests
Provides JSON responses for dynamic updates
"""

from flask import Blueprint, jsonify
from web.utils.bot_interface import get_bot_status, get_bot_stats
from web.utils.decorators import auth_required
import os
import requests

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/bot-status")
def bot_status():
    """Get current bot status as JSON"""
    status = get_bot_status()
    return jsonify(status)


@api_bp.route("/bot-stats")
def bot_stats():
    """Get bot statistics as JSON"""
    stats = get_bot_stats()
    return jsonify(stats)


@api_bp.route("/version")
def version():
    """Get version information"""
    try:
        # Read current version from version.txt
        version_file = os.path.join(
            os.path.dirname(__file__), "..", "..", "version.txt"
        )
        with open(version_file, "r") as f:
            local_version = f.read().strip()

        # Fetch latest version from GitHub
        try:
            response = requests.get(
                "https://api.github.com/repos/cyb3rgh05t/discord-bot/releases/latest",
                timeout=5,
            )
            if response.status_code == 200:
                latest_release = response.json()
                remote_version = latest_release.get("tag_name", "").lstrip("v")
            else:
                remote_version = local_version
        except:
            remote_version = local_version

        is_update_available = (
            remote_version != local_version if remote_version else False
        )

        return jsonify(
            {
                "local": local_version,
                "remote": remote_version,
                "is_update_available": is_update_available,
                "loading": False,
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "local": "unknown",
                    "remote": None,
                    "is_update_available": False,
                    "loading": False,
                    "error": str(e),
                }
            ),
            500,
        )


@api_bp.route("/check-updates")
def check_updates():
    """Check for bot updates (legacy endpoint)"""
    version_data = version()
    if isinstance(version_data, tuple):
        return version_data
    data = version_data.get_json()

    return jsonify(
        {
            "current_version": data.get("local"),
            "latest_version": data.get("remote"),
            "update_available": data.get("is_update_available", False),
            "message": (
                "Update available"
                if data.get("is_update_available")
                else "You are running the latest version"
            ),
        }
    )
