"""Audac Luna-U integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
import homeassistant.helpers.config_validation as cv

from .client import LunaUClient
from .coordinator import LunaUCoordinator
from .const import (
    DOMAIN,
    DEFAULT_PORT,
    DEFAULT_ADDRESS,
    DEFAULT_ZONES,
    DEFAULT_INPUTS,
    DEFAULT_GPO_COUNT,
    DEFAULT_POLL_INTERVAL,
    CONF_ADDRESS,
    CONF_ZONES,
    CONF_INPUTS,
    CONF_GPO_COUNT,
    CONF_POLL_INTERVAL,
    DATA_CLIENT,
    DATA_COORDINATOR,
)

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER, Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)

SERVICE_APPLY_SNAPSHOT = "apply_snapshot"
ATTR_SNAPSHOT_NAME = "snapshot_name"

APPLY_SNAPSHOT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_SNAPSHOT_NAME): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    address = entry.data.get(CONF_ADDRESS, DEFAULT_ADDRESS)

    zone_count = entry.options.get(CONF_ZONES, DEFAULT_ZONES)
    input_count = entry.options.get(CONF_INPUTS, DEFAULT_INPUTS)
    gpo_count = entry.options.get(CONF_GPO_COUNT, DEFAULT_GPO_COUNT)
    poll_interval = entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

    client = LunaUClient(host, port, address)
    await client.connect()

    coordinator = LunaUCoordinator(
        hass,
        client=client,
        zone_count=zone_count,
        input_count=input_count,
        gpo_count=gpo_count,
        poll_interval=poll_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_CLIENT: client,
        DATA_COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register apply_snapshot service
    async def async_handle_apply_snapshot(call: ServiceCall) -> None:
        """Handle apply_snapshot service call."""
        snapshot_name = call.data[ATTR_SNAPSHOT_NAME]
        # Build the snapshot path as expected by the device
        snapshot_path = f"settings/snapshots/{snapshot_name}.snapshot"
        _LOGGER.debug("Applying snapshot: %s", snapshot_path)
        # Send to all configured clients
        for entry_data in hass.data[DOMAIN].values():
            client: LunaUClient = entry_data[DATA_CLIENT]
            await client.set_value(
                target="SNAPSHOTS>1",
                command="APPLY_SNAPSHOT",
                arguments=snapshot_path,
                wait_for_response=False,
            )

    # Only register service once for the domain
    if not hass.services.has_service(DOMAIN, SERVICE_APPLY_SNAPSHOT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_APPLY_SNAPSHOT,
            async_handle_apply_snapshot,
            schema=APPLY_SNAPSHOT_SCHEMA,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        client: LunaUClient = data[DATA_CLIENT]
        await client.close()
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
