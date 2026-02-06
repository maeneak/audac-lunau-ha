"""Utility functions for Audac Luna-U integration."""
from __future__ import annotations

import re

from .const import NAME_DELIMITER


def split_names(raw: str | None, count: int, prefix: str) -> list[str]:
    """Split comma-separated names and pad with defaults."""
    if not raw:
        return [f"{prefix} {i}" for i in range(1, count + 1)]
    parts = [p.strip() for p in raw.split(NAME_DELIMITER)]
    parts = [p for p in parts if p]
    names = []
    for i in range(1, count + 1):
        names.append(parts[i - 1] if i - 1 < len(parts) else f"{prefix} {i}")
    return names


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


def validate_snapshot_name(name: str) -> str:
    """Validate and sanitize snapshot name."""
    # Remove any path separators and restrict to safe characters
    # Only allow alphanumeric, spaces, hyphens, underscores
    sanitized = re.sub(r'[^a-zA-Z0-9 _-]', '', name)
    if not sanitized:
        raise ValueError("Invalid snapshot name")
    return sanitized
