"""
Version checker utility
Check for updates from GitHub or version.txt
"""

import requests
import os


def get_current_version():
    """Get current version from version.txt"""
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"


def get_latest_version_github(owner="cyb3rgh05t", repo="discord-bot"):
    """Get latest version from GitHub releases"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return data.get("tag_name", "unknown")

        return None
    except Exception as e:
        print(f"Error fetching version from GitHub: {e}")
        return None


def check_for_updates(owner="cyb3rgh05t", repo="discord-bot"):
    """Check if updates are available"""
    current = get_current_version()
    latest = get_latest_version_github(owner, repo)

    if not latest:
        return {
            "update_available": False,
            "current_version": current,
            "latest_version": "unknown",
            "error": "Could not fetch latest version",
        }

    # Simple version comparison (assumes semantic versioning)
    update_available = latest != current and latest != "unknown"

    return {
        "update_available": update_available,
        "current_version": current,
        "latest_version": latest,
        "error": None,
    }


def get_changelog(owner="cyb3rgh05t", repo="discord-bot", limit=5):
    """Get recent changelog from GitHub releases"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        response = requests.get(url, params={"per_page": limit}, timeout=5)

        if response.status_code == 200:
            releases = response.json()
            changelog = []

            for release in releases:
                changelog.append(
                    {
                        "version": release.get("tag_name"),
                        "name": release.get("name"),
                        "date": release.get("published_at"),
                        "body": release.get("body"),
                        "url": release.get("html_url"),
                    }
                )

            return changelog

        return []
    except Exception as e:
        print(f"Error fetching changelog: {e}")
        return []
