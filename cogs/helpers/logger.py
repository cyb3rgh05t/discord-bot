import logging
import traceback
import sys
import os

# Try to import settings, with fallbacks if import fails
try:
    from config.settings import LOGGING_LEVEL, LOG_FILE

    # Convert string level name to actual logging level constant
    numeric_level = getattr(logging, LOGGING_LEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        print(f"Invalid log level: {LOGGING_LEVEL}, falling back to INFO")
        numeric_level = logging.INFO
    log_level = numeric_level
    log_file = LOG_FILE
except (ImportError, AttributeError) as e:
    print(f"Could not import logging settings: {e}, using defaults")
    # Default values if settings import fails
    log_level = logging.INFO
    log_file = "logs/bot.log"

# ANSI Color codes
COLORS = {
    "RESET": "\033[0m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "MAGENTA": "\033[95m",
    "BOLD": "\033[1m",
}


class DiscordFilter(logging.Filter):
    """Filter to completely block discord library logs"""

    def filter(self, record):
        # Block all discord.* logs so we can handle them separately
        if record.name.startswith("discord."):
            return False
        return True


class StreamlinedFormatter(logging.Formatter):
    """Custom formatter for consistent, readable logs with color support"""

    def format(self, record):
        """Format log records with log level after timestamp"""
        # Get the timestamp
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")

        # Special handling for Discord library messages
        if record.name.startswith("discord."):
            # Skip RESUMED session messages
            if "RESUMED session" in record.getMessage():
                return None

            if "Attempting a reconnect" in record.getMessage():
                reconnect_time = record.getMessage().split()[-1]
                msg = (
                    f"Discord connection refreshing (reconnecting in {reconnect_time})"
                )
                return f"[{timestamp}] {self.colorize('[INFO]', COLORS['BLUE'])} {self.colorize(msg, COLORS['BLUE'])}"

            if "WebSocket closed" in record.getMessage():
                code = "1000" if "1000" in record.getMessage() else "unknown"
                msg = f"Discord connection reset (code: {code})"
                return f"[{timestamp}] {self.colorize('[INFO]', COLORS['CYAN'])} {self.colorize(msg, COLORS['CYAN'])}"

            if "logging in using static token" in record.getMessage():
                return f"[{timestamp}] {self.colorize('[INFO]', COLORS['GREEN'])} {self.colorize('Discord bot logging in', COLORS['GREEN'])}"

            if (
                "Shard ID" in record.getMessage()
                and "connected to Gateway" in record.getMessage()
            ):
                if "Session ID:" in record.getMessage():
                    session_id = (
                        record.getMessage()
                        .split("Session ID: ")[-1]
                        .strip()
                        .split(")")[0]
                    )
                    session_short = session_id[:8] + "..."
                else:
                    session_short = "unknown"
                msg = f"Discord connection established (Session: {session_short})"
                return f"[{timestamp}] {self.colorize('[INFO]', COLORS['GREEN'])} {self.colorize(msg, COLORS['GREEN'])}"

            # Filter out other Discord messages that we don't care about
            important_patterns = [
                "logging in",
                "Shard ID",
                "Websocket closed",
                "Attempting a reconnect",
                "RESUMED session",
            ]
            for pattern in important_patterns:
                if pattern in record.getMessage():
                    break
            else:
                # None of our important patterns found, don't log this message
                return None

        # Choose color based on log level
        level_color = COLORS["RESET"]
        if record.levelno >= logging.CRITICAL:
            level_color = COLORS["RED"] + COLORS["BOLD"]
        elif record.levelno >= logging.ERROR:
            level_color = COLORS["RED"]
        elif record.levelno >= logging.WARNING:
            level_color = COLORS["YELLOW"]
        elif record.levelno >= logging.INFO:
            level_color = COLORS["GREEN"]
        elif record.levelno >= logging.DEBUG:
            level_color = COLORS["BLUE"]

        # Format log message with level after timestamp
        log_msg = f"[{timestamp}] {self.colorize(f'[{record.levelname}]', level_color)} {self.colorize(record.getMessage(), level_color)}"

        # Add traceback info for exceptions, formatted nicely
        if record.exc_info:
            # Format the traceback
            exc_text = self._format_traceback(record.exc_info)
            log_msg = f"{log_msg}\n{exc_text}"

        return log_msg

    def colorize(self, text, color):
        """Apply color to text and reset afterward"""
        return f"{color}{text}{COLORS['RESET']}"

    def _format_traceback(self, exc_info):
        """Format traceback in a compact, readable way"""
        tb_lines = traceback.format_exception(*exc_info)

        # Extract the most relevant parts
        error_type = tb_lines[-1].strip()
        error_location = ""

        # Find the most relevant frame (our code, not library code)
        for line in reversed(tb_lines[1:-1]):
            if "/site-packages/" not in line:
                error_location = line.strip()
                break

        if not error_location and len(tb_lines) > 2:
            error_location = tb_lines[-2].strip()

        # Format it nicely
        formatted = f"Exception: {self.colorize(error_type, COLORS['RED'])}"
        if error_location:
            formatted += (
                f"\n   Location: {self.colorize(error_location, COLORS['YELLOW'])}"
            )

        return formatted


def setup_logging(log_file=None, log_level=None):
    """Configure application-wide logging"""
    # Use parameters if provided, otherwise use the globals (from settings)
    if log_file is None:
        log_file = log_file_global
    if log_level is None:
        log_level = log_level_global

    # Print the log level we're trying to use
    print(f"Setting up logging with level: {logging.getLevelName(log_level)}")

    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create the formatter
    formatter = StreamlinedFormatter()

    # Configure Discord-specific loggers first
    # This must be done before configuring root logger
    discord_loggers = [
        logging.getLogger("discord"),
        logging.getLogger("discord.http"),
        logging.getLogger("discord.gateway"),
        logging.getLogger("discord.client"),
    ]

    # Completely disable discord's default handlers
    for discord_logger in discord_loggers:
        discord_logger.handlers = []
        discord_logger.propagate = False  # Don't propagate to root logger
        discord_logger.setLevel(log_level)  # Use the configured log level

        # Add our handlers directly to discord loggers
        discord_handler = logging.StreamHandler()
        discord_handler.setFormatter(formatter)
        discord_handler.setLevel(log_level)  # Use the configured log level
        discord_logger.addHandler(discord_handler)

        # Also log discord messages to file
        discord_file_handler = logging.FileHandler(log_file, encoding="utf-8")
        discord_file_handler.setFormatter(formatter)
        discord_file_handler.setLevel(log_level)  # Use the configured log level
        discord_logger.addHandler(discord_file_handler)

    # Create console handler for non-discord logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(
        DiscordFilter()
    )  # Block all discord.* logs from root logger
    console_handler.setLevel(log_level)  # Explicitly set handler level

    # Create file handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(DiscordFilter())  # Block all discord.* logs from root logger
    file_handler.setLevel(log_level)  # Explicitly set handler level

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)  # Set the root logger level

    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add our handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Create a logger instance for this application
    app_logger = logging.getLogger("discord_bot")
    app_logger.setLevel(log_level)

    # Print a confirmation of logging level
    if log_level <= logging.DEBUG:
        app_logger.debug("Debug logging is enabled")

    # Print a startup message
    app_logger.info("Logging system initialized")

    return app_logger


# Store the globals for use in setup_logging function
log_level_global = log_level
log_file_global = log_file

# Initialize and export logger for importing
logger = setup_logging(log_file=log_file, log_level=log_level)


# Add a simple test to ensure DEBUG messages work
if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
