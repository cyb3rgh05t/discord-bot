"""
Services view - Monitor service status and health
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from web.utils.decorators import auth_required
from web.utils.service_monitor import (
    get_service_status,
    get_system_resources,
    restart_bot,
)

services_bp = Blueprint("services", __name__, url_prefix="/services")


@services_bp.route("/")
@auth_required
def index():
    """Services status page"""
    services = get_service_status()
    resources = get_system_resources()

    return render_template(
        "services/index.html", services=services, resources=resources
    )


@services_bp.route("/api/status")
@auth_required
def api_status():
    """API endpoint for service status (for AJAX updates)"""
    services = get_service_status()
    resources = get_system_resources()

    return jsonify({"services": services, "resources": resources})


@services_bp.route("/restart", methods=["POST"])
@auth_required
def restart():
    """Restart the bot (requires appropriate permissions)"""
    try:
        restart_bot()
        return jsonify({"success": True, "message": "Bot restart initiated"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
