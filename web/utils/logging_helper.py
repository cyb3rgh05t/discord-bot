"""
Logging helper for Flask web UI
Provides simple logging functions based on WEB_VERBOSE_LOGGING setting
"""

from flask import current_app
from config.settings import WEB_VERBOSE_LOGGING


def log_debug(message):
    """Log debug message (only in verbose mode)"""
    if WEB_VERBOSE_LOGGING:
        current_app.logger.debug(message)


def log_info(message):
    """Log info message"""
    current_app.logger.info(message)


def log_warning(message):
    """Log warning message"""
    current_app.logger.warning(message)


def log_error(message):
    """Log error message"""
    current_app.logger.error(message)


def log_request(endpoint, data=None):
    """Log incoming request (only in verbose mode)"""
    if WEB_VERBOSE_LOGGING:
        if data:
            current_app.logger.debug(f"{endpoint} - Request data: {data}")
        else:
            current_app.logger.debug(f"{endpoint} - Request received")


def log_success(message):
    """Log successful operation"""
    current_app.logger.info(f"SUCCESS: {message}")


def log_failure(message):
    """Log failed operation"""
    current_app.logger.warning(f"FAILED: {message}")
