"""Utility functions for Audac Luna-U integration."""
from __future__ import annotations

import re


def parse_bool(value: str | None) -> bool | None:
    """Parse boolean value from Luna-U response."""
    if value is None:
        return None
    val = value.strip().upper()
    if val == "TRUE":
        return True
    if val == "FALSE":
        return False
    return None


def parse_int(value: str | None) -> int | None:
    """Parse integer value from Luna-U response."""
    if value is None:
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def parse_float(value: str | None) -> float | None:
    """Parse float value from Luna-U response."""
    if value is None:
        return None
    try:
        return float(value.strip())
    except ValueError:
        return None


def validate_snapshot_name(name: str) -> str:
    """Validate and sanitize snapshot name."""
    # Remove any path separators and restrict to safe characters
    # Only allow alphanumeric, spaces, hyphens, underscores
    sanitized = re.sub(r'[^a-zA-Z0-9 _-]', '', name)
    if not sanitized:
        raise ValueError("Invalid snapshot name")
    return sanitized
