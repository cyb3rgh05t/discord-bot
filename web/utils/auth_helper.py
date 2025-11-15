"""
Authentication helper functions
Handle user verification and password management
"""

import hashlib
import os


def verify_credentials(username, password):
    """
    Verify user credentials
    For now, uses simple username/password from settings
    Can be extended to use database or external auth
    """
    try:
        from config.settings import WEB_USERNAME, WEB_PASSWORD

        # Simple comparison (in production, use proper password hashing)
        return username == WEB_USERNAME and verify_password(password, WEB_PASSWORD)
    except ImportError:
        # Fallback if not configured
        return False


def verify_password(plain_password, hashed_password):
    """
    Verify password against hash
    For simple implementation, just compare directly
    In production, use bcrypt or similar
    """
    # If password is already hashed (starts with expected hash format)
    if hashed_password.startswith("$"):
        # Use proper password library here (bcrypt, scrypt, etc.)
        pass

    # Simple comparison for now
    return plain_password == hashed_password


def hash_password(password):
    """
    Hash a password
    In production, use bcrypt or scrypt
    """
    # Simple SHA256 for demonstration (NOT secure for production)
    return hashlib.sha256(password.encode()).hexdigest()
