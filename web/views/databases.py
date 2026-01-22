"""
Databases view - Browse and manage database tables
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from web.utils.decorators import auth_required
from web.utils.database_helper import (
    get_database_tables,
    get_table_data,
    get_table_schema,
    execute_query,
)

databases_bp = Blueprint("databases", __name__, url_prefix="/databases")


@databases_bp.route("/")
@auth_required
def index():
    """Database browser page"""
    tables = get_database_tables()

    # Calculate statistics
    databases = set()
    total_records = 0

    for table in tables:
        databases.add(table["database"])
        # Get record count for each table
        try:
            from web.utils.database_helper import get_db_connection

            conn = get_db_connection(table["database"])
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table['name']}")
            count = cursor.fetchone()[0]
            total_records += count
            conn.close()
        except Exception:
            pass

    stats = {
        "databases": len(databases),
        "tables": len(tables),
        "records": total_records,
    }

    return render_template("databases/index.html", tables=tables, stats=stats)


@databases_bp.route("/table/<table_name>")
@auth_required
def view_table(table_name):
    """View table data"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)

        data = get_table_data(table_name, page, per_page)
        schema = get_table_schema(table_name)

        return render_template(
            "databases/table.html", table_name=table_name, data=data, schema=schema
        )
    except ValueError as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for("databases.index"))
    except Exception as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect(url_for("databases.index"))


@databases_bp.route("/query", methods=["POST"])
@auth_required
def query():
    """Execute custom SQL query (read-only)"""
    try:
        sql = request.form.get("query")
        results = execute_query(sql)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@databases_bp.route("/schema/<db_name>/<table_name>")
@auth_required
def table_schema(db_name, table_name):
    """Get table schema information"""
    try:
        schema = get_table_schema(table_name, db_name)
        return jsonify({"success": True, "columns": schema})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
