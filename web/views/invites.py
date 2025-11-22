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
    # Get pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    search = request.args.get("search", "", type=str)

    invites = get_invites()

    # Filter by search if provided
    if search:
        search_lower = search.lower()
        invites = [
            inv
            for inv in invites
            if search_lower in inv.get("email", "").lower()
            or search_lower in inv.get("discord_user", "").lower()
        ]

    # Calculate pagination
    total_invites = len(invites)
    total_pages = (total_invites + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_invites = invites[start_idx:end_idx]

    stats = get_invite_stats()
    plex_users = get_plex_users()
    plex_stats = get_plex_stats()

    return render_template(
        "invites/index.html",
        invites=paginated_invites,
        stats=stats,
        plex_users=plex_users,
        plex_stats=plex_stats,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_invites=total_invites,
        search=search,
    )


@invites_bp.route("/add", methods=["POST"])
@auth_required
def add():
    """Add a new invite"""
    try:
        email = request.form.get("email")
        discord_user = request.form.get("discord_user")

        add_invite(email, discord_user)

        # Check if it's an AJAX request
        if (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.is_json
        ):
            return jsonify({"success": True, "message": "Invite added successfully"})

        flash("Invite added successfully", "success")

    except Exception as e:
        if (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.is_json
        ):
            return jsonify({"success": False, "message": str(e)}), 400

        flash(f"Error adding invite: {str(e)}", "danger")

    return redirect(url_for("invites.index"))


@invites_bp.route("/<int:invite_id>/remove", methods=["POST"])
@auth_required
def remove(invite_id):
    """Remove an invite and remove Plex role from Discord user"""
    try:
        # Get invite data before deletion
        invite_data = remove_invite(invite_id)

        if not invite_data:
            return jsonify({"success": False, "message": "Invite not found"}), 404

        # Remove Plex role from Discord user if discord_user exists
        discord_user = invite_data.get("discord_user")
        if discord_user:
            from web.utils.bot_interface import remove_role_from_member
            from config.settings import PLEX_ROLES

            # Extract user ID from discord_user (format: "username (ID)" or just "ID")
            user_id = None
            if "(" in discord_user and ")" in discord_user:
                # Extract ID from "username (ID)" format
                user_id = discord_user.split("(")[-1].split(")")[0].strip()
            else:
                # Assume it's just the ID
                user_id = discord_user.strip()

            # Try to convert to int to validate it's a Discord ID
            try:
                user_id = int(user_id)

                # Get role ID from PLEX_ROLES setting
                # PLEX_ROLES might be a role name or ID
                role_identifier = PLEX_ROLES

                # Remove the role
                result = remove_role_from_member(user_id, role_identifier)

                if not result.get("success"):
                    print(
                        f"Warning: Could not remove Plex role from user {user_id}: {result.get('error')}"
                    )
            except (ValueError, TypeError) as e:
                print(
                    f"Warning: Could not parse Discord user ID from '{discord_user}': {e}"
                )

        return jsonify(
            {"success": True, "message": "Invite removed and Plex access revoked"}
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
