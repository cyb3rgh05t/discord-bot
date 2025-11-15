"""
Manage bot settings.py file
Read, update, and validate configuration
"""

import os
import sys
import re

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "../../config/settings.py")


def get_settings():
    """Read current settings from settings.py with comments"""
    settings = {}
    comments = {}

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            content = f.read()

            # Parse settings and comments using regex
            # Match pattern: KEY = value  # comment
            pattern = r"^([A-Z_]+)\s*=\s*(.+?)(?:\s*#\s*(.+))?$"
            for line in content.split("\n"):
                match = re.match(pattern, line.strip())
                if match:
                    key = match.group(1)
                    value = match.group(2).strip()
                    comment = match.group(3).strip() if match.group(3) else ""

                    # Clean value (remove quotes and trailing whitespace)
                    value = value.strip("\"'").rstrip()

                    settings[key] = value
                    if comment:
                        comments[key] = comment

    except Exception as e:
        print(f"Error reading settings: {e}")

    return {"values": settings, "comments": comments}


def update_settings(new_settings):
    """Update settings.py file with new values while preserving comments"""
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated_lines = []
        for line in lines:
            # Check if this line contains a setting we need to update
            match = re.match(r"^([A-Z_]+)\s*=\s*(.+?)(\s*#.+)?$", line.strip())

            if match:
                key = match.group(1)
                comment = match.group(3) if match.group(3) else ""

                if key in new_settings:
                    value = new_settings[key]

                    # Skip empty values for non-required fields
                    if value == "":
                        updated_lines.append(line)
                        continue

                    # Determine indentation
                    indent = len(line) - len(line.lstrip())
                    indent_str = " " * indent

                    # Handle boolean values
                    if value in ["True", "False"]:
                        new_line = f"{indent_str}{key} = {value}{comment}\n"
                    # Handle numeric values
                    elif value.isdigit():
                        new_line = f"{indent_str}{key} = {value}{comment}\n"
                    else:
                        # Escape special characters for string values
                        escaped_value = value.replace('"', '\\"')
                        new_line = f'{indent_str}{key} = "{escaped_value}"{comment}\n'

                    updated_lines.append(new_line)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Write back with UTF-8 encoding
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

        return True

    except Exception as e:
        print(f"Error updating settings: {e}")
        import traceback

        traceback.print_exc()
        return False


def validate_settings(settings):
    """Validate settings before saving"""
    errors = []

    # Add validation rules here
    required_fields = ["BOT_TOKEN", "GUILD_ID", "COMMAND_PREFIX"]

    for field in required_fields:
        if field in settings and not settings[field]:
            errors.append(f"{field} is required")

    return len(errors) == 0, errors
