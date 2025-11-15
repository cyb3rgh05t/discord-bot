"""
Custom decorators for views
Handles conditional authentication based on settings
"""

from functools import wraps
from flask_login import login_required, current_user
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from config.settings import WEB_AUTH_ENABLED


def auth_required(f):
    """
    Conditional authentication decorator
    Only requires login if WEB_AUTH_ENABLED is True
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if WEB_AUTH_ENABLED:
            # Use Flask-Login's login_required
            return login_required(f)(*args, **kwargs)
        else:
            # No authentication needed
            return f(*args, **kwargs)

    return decorated_function
