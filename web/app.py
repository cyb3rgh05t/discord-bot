"""
Main Flask application for Discord Bot Web UI
Runs alongside the Discord bot in the same container
"""

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
import os
import sys
import logging

# Add parent directory to path to import bot config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.settings import (
    WEB_ENABLED,
    WEB_PORT,
    WEB_HOST,
    WEB_AUTH_ENABLED,
    WEB_SECRET_KEY,
    WEB_VERBOSE_LOGGING,
)

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = WEB_SECRET_KEY

# Configure Flask logging to write to logs/web.log
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "web.log")

file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)

# Set log level based on WEB_VERBOSE_LOGGING
if WEB_VERBOSE_LOGGING:
    file_handler.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
else:
    file_handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)

app.logger.addHandler(file_handler)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # type: ignore

# Bot instance will be set by the main bot.py
bot_instance = None


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    if WEB_AUTH_ENABLED:
        from web.auth.models import User

        return User(user_id)
    return None


def set_bot_instance(bot):
    """Set the bot instance for the web UI to access"""
    global bot_instance
    bot_instance = bot


# Register blueprints
from web.views.dashboard import dashboard_bp
from web.views.settings import settings_bp
from web.views.tickets import tickets_bp
from web.views.invites import invites_bp
from web.views.databases import databases_bp
from web.views.services import services_bp
from web.views.api import api_bp
from web.views.about import about_bp
from web.views.members import members_bp

app.register_blueprint(dashboard_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(tickets_bp)
app.register_blueprint(invites_bp)
app.register_blueprint(databases_bp)
app.register_blueprint(services_bp)
app.register_blueprint(api_bp)
app.register_blueprint(about_bp)
app.register_blueprint(members_bp)

# Register auth blueprint if enabled
if WEB_AUTH_ENABLED:
    from web.auth.routes import auth_bp

    app.register_blueprint(auth_bp)


@app.route("/")
def index():
    """Redirect to dashboard"""
    return redirect(url_for("dashboard.index"))


@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    from web.utils.version_checker import get_current_version

    return {
        "version": get_current_version(),
        "bot_status": get_bot_status_for_template(),
        "config": app.config,
    }


def get_bot_status_for_template():
    """Get bot status for template context"""
    try:
        from web.utils.bot_interface import get_bot_status

        return get_bot_status()
    except:
        return {"online": False, "latency": 0, "uptime": "N/A", "guilds": 0, "users": 0}


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template("errors/500.html"), 500


if __name__ == "__main__":
    # For standalone testing
    app.run(host=WEB_HOST, port=WEB_PORT, debug=WEB_DEBUG)
