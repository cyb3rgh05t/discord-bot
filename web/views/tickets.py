"""
Tickets view - View and manage support tickets
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from web.utils.decorators import auth_required
from web.utils.database_helper import get_tickets, get_ticket_details, close_ticket
from web.utils.bot_interface import get_discord_usernames_bulk, get_discord_username

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")


@tickets_bp.route("/")
@auth_required
def index():
    """Tickets list page"""
    status_filter = request.args.get("status", "all")
    ticket_type = request.args.get("type", "all")  # plex, tv, or all
    page = request.args.get("page", 1, type=int)
    per_page = 10

    # Get all tickets
    all_tickets = get_tickets(status_filter)

    # Filter by ticket type
    if ticket_type == "plex":
        tickets = [t for t in all_tickets if t.get("ticket_type") == "plex"]
    elif ticket_type == "tv":
        tickets = [t for t in all_tickets if t.get("ticket_type") == "tv"]
    else:
        tickets = all_tickets

    # Calculate pagination
    total_tickets = len(tickets)
    total_pages = (total_tickets + per_page - 1) // per_page  # Ceiling division
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_tickets = tickets[start_idx:end_idx]

    # Get usernames for paginated tickets
    user_ids = [
        ticket.get("user_id") for ticket in paginated_tickets if ticket.get("user_id")
    ]
    usernames = get_discord_usernames_bulk(user_ids)

    # Add usernames to tickets
    for ticket in paginated_tickets:
        user_id = ticket.get("user_id")
        ticket["username"] = usernames.get(str(user_id), f"User#{user_id}")

    return render_template(
        "tickets/index.html",
        tickets=paginated_tickets,
        status_filter=status_filter,
        ticket_type=ticket_type,
        page=page,
        total_pages=total_pages,
        total_tickets=total_tickets,
    )


@tickets_bp.route("/<int:ticket_id>")
@auth_required
def view(ticket_id):
    """View ticket details"""
    ticket = get_ticket_details(ticket_id)

    if not ticket:
        flash("Ticket not found", "danger")
        return redirect(url_for("tickets.index"))

    # Get username
    user_id = ticket.get("user_id")
    username = get_discord_username(user_id)
    ticket["username"] = username if username else f"User#{user_id}"

    return render_template("tickets/view.html", ticket=ticket)


@tickets_bp.route("/<int:ticket_id>/close", methods=["POST"])
@auth_required
def close(ticket_id):
    """Close a ticket"""
    try:
        close_ticket(ticket_id)
        return jsonify({"success": True, "message": "Ticket closed"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
