"""Diagnostics support for Audac Luna-U."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST

from . import LunaUConfigEntry

TO_REDACT = {CONF_HOST}


async def async_get_config_entry_diagnostics(
    hass: Any,
    entry: LunaUConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator
    client = entry.runtime_data.client

    return {
        "config_entry": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "connected": client.connected,
        "zone_count": coordinator.zone_count,
        "input_count": coordinator.input_count,
        "gpo_count": coordinator.gpo_count,
        "coordinator_data": coordinator.data,
        "last_update_success": coordinator.last_update_success,
    }
