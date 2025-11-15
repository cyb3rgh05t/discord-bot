"""
Invites view - Manage Plex invites and user access
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from web.utils.decorators import auth_required
from web.utils.database_helper import (
    get_invites,
    add_invite,
    remove_invite,
    get_invite_stats,
)
from web.utils.plex_interface import get_plex_users, get_plex_stats

invites_bp = Blueprint("invites", __name__, url_prefix="/invites")


@invites_bp.route("/")
@auth_required
def index():
    """Invites list page"""
    invites = get_invites()
    stats = get_invite_stats()
    plex_users = get_plex_users()
    plex_stats = get_plex_stats()

    return render_template(
        "invites/index.html",
        invites=invites,
        stats=stats,
        plex_users=plex_users,
        plex_stats=plex_stats,
    )


@invites_bp.route("/add", methods=["POST"])
@auth_required
def add():
    """Add a new invite"""
    try:
        email = request.form.get("email")
        discord_user = request.form.get("discord_user")

        add_invite(email, discord_user)
        flash("Invite added successfully", "success")

    except Exception as e:
        flash(f"Error adding invite: {str(e)}", "danger")

    return redirect(url_for("invites.index"))


@invites_bp.route("/<int:invite_id>/remove", methods=["POST"])
@auth_required
def remove(invite_id):
    """Remove an invite"""
    try:
        remove_invite(invite_id)
        return jsonify({"success": True, "message": "Invite removed"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
