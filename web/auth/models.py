"""
User model for Flask-Login
"""

from flask_login import UserMixin


class User(UserMixin):
    """Simple user model for authentication"""

    def __init__(self, username):
        self.id = username
        self.username = username

    def __repr__(self):
        return f"<User {self.username}>"
