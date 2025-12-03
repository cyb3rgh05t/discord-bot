"""Settings endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import re

router = APIRouter()


class SettingsResponse(BaseModel):
    values: Dict[str, str]
    comments: Dict[str, str]


class UpdateSettingsRequest(BaseModel):
    settings: Dict[str, Any]


SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config",
    "settings.py",
)


def get_settings_data():
    """Read current settings from settings.py with comments"""
    settings = {}
    comments = {}

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            content = f.read()

            # Parse settings and comments using regex
            # Match pattern: KEY = value  # comment
            # Use greedy match for value to capture everything before comment
            pattern = r"^([A-Z_]+)\s*=\s*(.+?)(?:\s+#\s*(.+))?$"
            for line in content.split("\n"):
                match = re.match(pattern, line.strip())
                if match:
                    key = match.group(1)
                    value = match.group(2).strip()
                    comment = match.group(3).strip() if match.group(3) else ""

                    # Clean value (remove quotes and trailing whitespace)
                    # Handle different value types
                    if value in ("True", "False"):
                        settings[key] = value
                    elif value.startswith('"') and value.endswith('"'):
                        settings[key] = value[1:-1]  # Remove quotes
                    elif value.startswith("'") and value.endswith("'"):
                        settings[key] = value[1:-1]  # Remove quotes
                    else:
                        settings[key] = value

                    if comment:
                        comments[key] = comment

    except Exception as e:
        print(f"Error reading settings: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading settings: {e}")

    return {"values": settings, "comments": comments}


def update_settings_file(new_settings: Dict[str, Any]):
    """Update settings.py file with new values while preserving comments"""
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Skip these fields (they have special formatting)
        skip_fields = ["ASCII_LOGO"]

        # Split into lines for processing
        lines = content.split("\n")
        updated_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip multi-line strings (triple quotes)
            if '"""' in line or "'''" in line:
                # Find the closing triple quotes
                quote_type = '"""' if '"""' in line else "'''"
                updated_lines.append(line)
                i += 1

                # If triple quotes don't close on same line, keep reading
                if line.count(quote_type) == 1:
                    while i < len(lines):
                        updated_lines.append(lines[i])
                        if quote_type in lines[i]:
                            break
                        i += 1
                i += 1
                continue

            # Check if this line contains a setting we need to update
            # Match with better pattern that captures full value including spaces
            match = re.match(r"^(\s*)([A-Z_]+)\s*=\s*(.+?)(\s+#.+)?$", line)

            if match:
                indent_str = match.group(1)
                key = match.group(2)
                old_value = match.group(3).strip()
                comment = match.group(4) if match.group(4) else ""

                if key in skip_fields or key not in new_settings:
                    updated_lines.append(line)
                else:
                    value = new_settings[key]

                    # Skip empty values for non-required fields
                    if value == "" or value is None:
                        updated_lines.append(line)
                        i += 1
                        continue

                    # Handle boolean values
                    if isinstance(value, bool) or value in (
                        "True",
                        "False",
                        True,
                        False,
                    ):
                        bool_val = "True" if value in ("True", True, 1) else "False"
                        new_line = f"{indent_str}{key} = {bool_val}{comment}"
                    # Handle numeric values (but not strings that look like numbers)
                    elif isinstance(value, int) or (
                        isinstance(value, str)
                        and value.isdigit()
                        and not old_value.startswith('"')
                    ):
                        new_line = f"{indent_str}{key} = {value}{comment}"
                    else:
                        # String values - always quote them
                        # Don't escape quotes if they're already escaped
                        str_value = str(value)
                        new_line = f'{indent_str}{key} = "{str_value}"{comment}'

                    updated_lines.append(new_line)
            else:
                updated_lines.append(line)

            i += 1

        # Write back with UTF-8 encoding
        with open(SETTINGS_FILE, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(updated_lines))

        return True

    except Exception as e:
        print(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating settings: {e}")


@router.get("/", response_model=SettingsResponse)
async def get_settings():
    """Get bot settings"""
    data = get_settings_data()
    return SettingsResponse(values=data["values"], comments=data["comments"])


@router.post("/")
async def update_settings(request: UpdateSettingsRequest):
    """Update bot settings"""
    try:
        # Handle checkboxes (keep as boolean, not string)
        checkbox_fields = [
            "PLEX_ENABLED",
            "WEB_ENABLED",
            "WEB_VERBOSE_LOGGING",
            "WEB_AUTH_ENABLED",
            "KOFI_ENABLED",
        ]

        # Ensure boolean fields are actual booleans
        for field in checkbox_fields:
            if field in request.settings:
                # Convert string "True"/"False" or boolean to Python bool
                val = request.settings[field]
                if isinstance(val, str):
                    # Handle both "True"/"False" and "true"/"false"
                    request.settings[field] = val in ("True", "true", "1", "yes", "YES")
                else:
                    request.settings[field] = bool(val)

        update_settings_file(request.settings)

        return {
            "success": True,
            "message": "Settings updated successfully. Restart bot to apply changes.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restart-bot")
async def restart_bot():
    """Restart the bot process"""
    try:
        import signal
        import threading
        import subprocess
        import sys
        import time

        def delayed_restart():
            time.sleep(1)

            try:
                # Get the Python executable and script path
                python_exe = sys.executable
                script_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "bot.py",
                )

                # Start new process
                subprocess.Popen(
                    [python_exe, script_path],
                    cwd=os.path.dirname(script_path),
                    creationflags=(
                        subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
                    ),
                )

                # Wait a moment then kill current process
                time.sleep(2)
            except Exception as e:
                print(f"Error restarting: {e}")

            # Kill current process
            os.kill(os.getpid(), signal.SIGTERM)

        # Start restart in background thread
        thread = threading.Thread(target=delayed_restart, daemon=True)
        thread.start()

        return {
            "success": True,
            "message": "Bot restart initiated. Please wait a moment...",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
