"""Manage persistent application configuration."""

import json
import os
import sys

from core.models import AppConfig


def _get_config_dir() -> str:
    """Return the config directory path, creating it if needed."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    else:
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    config_dir = os.path.join(base, "ResumeGenerator")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def _get_config_path() -> str:
    return os.path.join(_get_config_dir(), "config.json")


def _detect_experience_file() -> str:
    """Try to find experience_data.json next to the executable/script."""
    # Check next to the main script
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(sys.argv[0]))
    candidate = os.path.join(base, "experience_data.json")
    if os.path.isfile(candidate):
        return candidate
    return ""


def _default_output_dir() -> str:
    """Default output to ~/Documents."""
    docs = os.path.join(os.path.expanduser("~"), "Documents")
    if os.path.isdir(docs):
        return docs
    return os.path.expanduser("~")


def load_config() -> AppConfig:
    """Load config from disk, applying first-run defaults if needed."""
    path = _get_config_path()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            config = AppConfig.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            config = AppConfig()
    else:
        config = AppConfig()

    # Apply first-run defaults for empty fields
    if not config.experience_file:
        config.experience_file = _detect_experience_file()
    if not config.output_directory:
        config.output_directory = _default_output_dir()

    return config


def save_config(config: AppConfig) -> None:
    """Persist config to disk."""
    path = _get_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2)


def get_data_dir() -> str:
    """Return the data directory (same as config dir) for history etc."""
    return _get_config_dir()
