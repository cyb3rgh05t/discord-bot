"""Settings endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import re
import asyncio

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
                        # String values - always quote them (including empty strings)
                        # Don't escape quotes if they're already escaped
                        str_value = str(value) if value is not None else ""
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
    """Restart the bot process (Windows-optimized)"""
    try:
        import subprocess
        import sys
        import os as _os

        print("[INFO] ============ BOT RESTART REQUESTED ============")

        current_pid = _os.getpid()
        python_exe = sys.executable
        script_path = _os.path.join(
            _os.path.dirname(_os.path.dirname(_os.path.dirname(__file__))),
            "bot.py",
        )
        work_dir = _os.path.dirname(script_path)

        print(f"[INFO] Current PID: {current_pid}")
        print(f"[INFO] Python: {python_exe}")
        print(f"[INFO] Script: {script_path}")
        print(f"[INFO] Workdir: {work_dir}")

        # Detect containerized environment (Docker/K8s)
        is_container = (
            _os.path.exists("/.dockerenv")
            or _os.environ.get("RUNNING_IN_CONTAINER") == "1"
            or current_pid == 1
        )

        if is_container:
            # In containers, let the orchestrator restart the process/container.
            # Exit after sending response to avoid breaking the HTTP call.
            import threading

            threading.Timer(1.0, lambda: _os._exit(0)).start()
            print(
                "[INFO] Container mode detected. Scheduled exit for orchestrator restart."
            )
        elif _os.name == "nt":
            # Use a detached PowerShell helper to kill this PID and start a fresh bot
            ps_cmd = (
                f"Start-Sleep -Seconds 1; "
                f"Stop-Process -Id {current_pid} -Force; "
                f"Start-Sleep -Seconds 3; "
                f'Start-Process -FilePath "{python_exe}" -ArgumentList "{script_path}" -WorkingDirectory "{work_dir}" -WindowStyle Normal'
            )

            try:
                subprocess.Popen(
                    [
                        "powershell",
                        "-NoProfile",
                        "-WindowStyle",
                        "Hidden",
                        "-Command",
                        ps_cmd,
                    ],
                    creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP),
                )
                print("[INFO] Restart helper launched via PowerShell.")
            except Exception as e:
                print(f"[ERROR] Failed to launch restart helper: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        else:
            # POSIX fallback: spawn a helper shell that kills current PID then starts new
            sh_cmd = (
                f"sleep 1; kill -TERM {current_pid}; sleep 3; "
                f"{python_exe} {script_path} &"
            )
            try:
                subprocess.Popen(
                    ["/bin/sh", "-c", sh_cmd],
                    cwd=work_dir,
                )
                print("[INFO] Restart helper launched via /bin/sh.")
            except Exception as e:
                print(f"[ERROR] Failed to launch restart helper (POSIX): {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # Return immediately; helper will kill this process and start the new one
        return {
            "success": True,
            "message": "Restart scheduled. This process will be terminated, new bot starting...",
        }
    except Exception as e:
        print(f"[ERROR] Restart failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
