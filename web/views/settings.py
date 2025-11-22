"""
Settings view - Edit and manage bot configuration
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from web.utils.decorators import auth_required
from web.utils.settings_manager import get_settings, update_settings, validate_settings
import os
import sys

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/")
@auth_required
def index():
    """Settings overview page"""
    settings_data = get_settings()
    return render_template(
        "settings/index.html",
        settings=settings_data.get("values", {}),
        comments=settings_data.get("comments", {}),
    )


@settings_bp.route("/edit", methods=["POST"])
@auth_required
def edit():
    """Update settings"""
    try:
        new_settings = request.form.to_dict()

        # Handle checkboxes (they're not sent if unchecked)
        checkbox_fields = [
            "PLEX_ENABLED",
            "WEB_ENABLED",
            "WEB_DEBUG",
            "WEB_AUTH_ENABLED",
        ]
        for field in checkbox_fields:
            if field not in new_settings:
                new_settings[field] = "False"
            else:
                new_settings[field] = "True"

        # Validate settings
        is_valid, errors = validate_settings(new_settings)

        if not is_valid:
            if (
                request.headers.get("X-Requested-With") == "XMLHttpRequest"
                or request.is_json
            ):
                return jsonify({"success": False, "message": "; ".join(errors)}), 400
            for error in errors:
                flash(error, "danger")
            return redirect(url_for("settings.index"))

        # Update settings
        update_settings(new_settings)

        if (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.is_json
        ):
            return jsonify(
                {
                    "success": True,
                    "message": "Settings updated successfully. Restart bot to apply changes.",
                }
            )

        flash("Settings updated successfully. Restart bot to apply changes.", "success")

    except Exception as e:
        if (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.is_json
        ):
            return jsonify({"success": False, "message": str(e)}), 400
        flash(f"Error updating settings: {str(e)}", "danger")

    return redirect(url_for("settings.index"))


@settings_bp.route("/restart-bot", methods=["POST"])
@auth_required
def restart_bot():
    """Restart the bot process"""
    try:
        import signal
        import threading
        import subprocess

        def delayed_restart():
            import time

            time.sleep(1)

            # Try to restart using the same command
            try:
                # Get the Python executable and script path
                python_exe = sys.executable
                script_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "bot.py",
                )

                # Start new process
                subprocess.Popen(
                    [python_exe, script_path],
                    cwd=os.path.dirname(script_path),
                    creationflags=(
                        subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
                    ),
                )

                # Wait a moment then kill current process
                time.sleep(2)
            except Exception as e:
                print(f"Error restarting: {e}")

            # Kill current process
            os.kill(os.getpid(), signal.SIGTERM)

        # Start restart in background thread
        thread = threading.Thread(target=delayed_restart, daemon=True)
        thread.start()

        return jsonify(
            {
                "success": True,
                "message": "Bot restart initiated. Please wait a moment...",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
