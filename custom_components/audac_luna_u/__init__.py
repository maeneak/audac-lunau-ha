"""Audac Luna-U integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import device_registry as dr

from .client import LunaUClient
from .coordinator import LunaUCoordinator
from .utils import validate_snapshot_name
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
        vol.Optional("device_id"): vol.All(cv.ensure_list, [cv.string]),
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
    try:
        await client.connect()
    except Exception as exc:
        raise ConfigEntryNotReady(str(exc)) from exc

    coordinator = LunaUCoordinator(
        hass,
        client=client,
        zone_count=zone_count,
        input_count=input_count,
        gpo_count=gpo_count,
        poll_interval=poll_interval,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as exc:
        await client.close()
        raise ConfigEntryNotReady(str(exc)) from exc

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_CLIENT: client,
        DATA_COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    # Register apply_snapshot service
    async def async_handle_apply_snapshot(call: ServiceCall) -> None:
        """Handle apply_snapshot service call."""
        try:
            snapshot_name = call.data[ATTR_SNAPSHOT_NAME]
            # Validate and sanitize snapshot name
            sanitized_name = validate_snapshot_name(snapshot_name)
            # Build the snapshot path as expected by the device
            snapshot_path = f"settings/snapshots/{sanitized_name}.snapshot"
            _LOGGER.debug("Applying snapshot: %s", snapshot_path)
            
            targets = []
            if "device_id" in call.data:
                target_devices = set(call.data["device_id"])
                dev_reg = dr.async_get(hass)
                for device_id in target_devices:
                    device = dev_reg.async_get(device_id)
                    if device:
                        for entry_id in device.config_entries:
                            if entry_id in hass.data.get(DOMAIN, {}):
                                targets.append(hass.data[DOMAIN][entry_id][DATA_CLIENT])
            else:
                # Send to all configured clients
                for entry_data in hass.data.get(DOMAIN, {}).values():
                    targets.append(entry_data[DATA_CLIENT])

            # Send to identified clients
            for client in targets:
                try:
                    await client.set_value(
                        target="SNAPSHOTS>1",
                        command="APPLY_SNAPSHOT",
                        arguments=snapshot_path,
                        wait_for_response=False,
                    )
                except Exception as exc:
                    _LOGGER.error("Failed to apply snapshot to device: %s", exc)
        except ValueError as exc:
            _LOGGER.error("Invalid snapshot name: %s", exc)
        except Exception as exc:
            _LOGGER.error("Failed to apply snapshot: %s", exc)

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
        
        # Unregister service if this is the last entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_APPLY_SNAPSHOT)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options updates."""
    await hass.config_entries.async_reload(entry.entry_id)
