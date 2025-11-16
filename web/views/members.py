"""
Members view - Member and role management
Shows all guild members and allows role assignment
"""

from flask import Blueprint, render_template, request, jsonify
from web.utils.decorators import auth_required
from web.utils.logging_helper import log_request, log_success, log_failure, log_error
from web.utils.bot_interface import (
    get_guild_members,
    get_guild_roles,
    add_role_to_member,
    remove_role_from_member,
)

members_bp = Blueprint("members", __name__, url_prefix="/members")


@members_bp.route("/")
@auth_required
def index():
    """Members and roles management page"""
    members = get_guild_members()
    roles = get_guild_roles()

    return render_template(
        "members/index.html",
        members=members,
        roles=roles,
        total_members=len(members),
        total_roles=len(roles),
    )


@members_bp.route("/add_role", methods=["POST"])
@auth_required
def add_role():
    """Add a role to a member"""
    try:
        data = request.get_json()
        log_request("add_role", data)

        if not data:
            return jsonify({"success": False, "error": "No JSON data received"}), 400

        user_id = data.get("user_id")
        role_id = data.get("role_id")

        if not user_id or not role_id:
            return (
                jsonify({"success": False, "error": "Missing user_id or role_id"}),
                400,
            )

        # Convert to int
        try:
            user_id = int(user_id)
            role_id = int(role_id)
        except (ValueError, TypeError) as e:
            return (
                jsonify({"success": False, "error": f"Invalid ID format: {str(e)}"}),
                400,
            )

        result = add_role_to_member(user_id, role_id)

        if result["success"]:
            log_success(result["message"])
            return jsonify(result), 200
        else:
            log_failure(f"Add role failed: {result['error']}")
            return jsonify(result), 400
    except Exception as e:
        log_error(f"Error in add_role: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@members_bp.route("/remove_role", methods=["POST"])
@auth_required
def remove_role():
    """Remove a role from a member"""
    try:
        data = request.get_json()
        log_request("remove_role", data)

        if not data:
            return jsonify({"success": False, "error": "No JSON data received"}), 400

        user_id = data.get("user_id")
        role_id = data.get("role_id")

        if not user_id or not role_id:
            return (
                jsonify({"success": False, "error": "Missing user_id or role_id"}),
                400,
            )

        # Convert to int
        try:
            user_id = int(user_id)
            role_id = int(role_id)
        except (ValueError, TypeError) as e:
            return (
                jsonify({"success": False, "error": f"Invalid ID format: {str(e)}"}),
                400,
            )

        result = remove_role_from_member(user_id, role_id)

        if result["success"]:
            log_success(result["message"])
            return jsonify(result), 200
        else:
            log_failure(f"Remove role failed: {result['error']}")
            return jsonify(result), 400
    except Exception as e:
        log_error(f"Error in remove_role: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
