"""
Authentication routes - Login/logout functionality
Only active when WEB_AUTH_ENABLED is True
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from web.auth.models import User
from web.utils.auth_helper import verify_credentials

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember", False)

        if verify_credentials(username, password):
            user = User(username)
            login_user(user, remember=remember)

            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """Logout"""
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))
