"""Audac Luna-U integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re
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


@dataclass
class LunaURuntimeData:
    """Runtime data for a Luna-U config entry."""

    client: LunaUClient
    coordinator: LunaUCoordinator


type LunaUConfigEntry = ConfigEntry[LunaURuntimeData]


def _cleanup_legacy_naming_keys(options: dict) -> dict:
    """Remove legacy zone/GPIO name keys from options."""
    pattern = re.compile(r"^(Zone|GPIO) \d+$")
    cleaned = {k: v for k, v in options.items() if not pattern.match(k)}

    if len(cleaned) != len(options):
        _LOGGER.info(
            "Migrated config: removed %d legacy naming keys",
            len(options) - len(cleaned)
        )

    return cleaned


def _device_uid(entry: ConfigEntry) -> str:
    """Return a stable device identifier base from config entry data."""
    host = entry.data[CONF_HOST]
    address = entry.data.get(CONF_ADDRESS, DEFAULT_ADDRESS)
    return f"{host}_{address}"


async def async_setup_entry(hass: HomeAssistant, entry: LunaUConfigEntry) -> bool:
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    address = entry.data.get(CONF_ADDRESS, DEFAULT_ADDRESS)

    # Clean up legacy zone/GPIO naming keys from older installations
    if entry.options:
        cleaned_options = _cleanup_legacy_naming_keys(dict(entry.options))
        if cleaned_options != entry.options:
            hass.config_entries.async_update_entry(entry, options=cleaned_options)

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

    entry.runtime_data = LunaURuntimeData(client=client, coordinator=coordinator)

    # Register the main Luna-U controller device
    uid = _device_uid(entry)
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, uid)},
        name="Audac Luna-U",
        manufacturer="Audac",
        model="Luna-U",
        configuration_url=f"http://{host}:{port}",
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    # Register apply_snapshot service (once per domain)
    if not hass.services.has_service(DOMAIN, SERVICE_APPLY_SNAPSHOT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_APPLY_SNAPSHOT,
            _async_handle_apply_snapshot,
            schema=APPLY_SNAPSHOT_SCHEMA,
        )

    return True


async def _async_handle_apply_snapshot(call: ServiceCall) -> None:
    """Handle apply_snapshot service call."""
    hass = call.hass
    try:
        snapshot_name = call.data[ATTR_SNAPSHOT_NAME]
        sanitized_name = validate_snapshot_name(snapshot_name)
        snapshot_path = f"settings/snapshots/{sanitized_name}.snapshot"
        _LOGGER.debug("Applying snapshot: %s", snapshot_path)

        targets: list[LunaUClient] = []
        if "device_id" in call.data:
            target_devices = set(call.data["device_id"])
            dev_reg = dr.async_get(hass)
            for device_id in target_devices:
                device = dev_reg.async_get(device_id)
                if device:
                    for eid in device.config_entries:
                        entry = hass.config_entries.async_get_entry(eid)
                        if entry and hasattr(entry, "runtime_data") and entry.runtime_data:
                            targets.append(entry.runtime_data.client)
        else:
            for entry in hass.config_entries.async_entries(DOMAIN):
                if hasattr(entry, "runtime_data") and entry.runtime_data:
                    targets.append(entry.runtime_data.client)

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


async def async_unload_entry(hass: HomeAssistant, entry: LunaUConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.client.close()

        # Unregister service if no entries remain
        if not hass.config_entries.async_entries(DOMAIN):
            hass.services.async_remove(DOMAIN, SERVICE_APPLY_SNAPSHOT)
    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: LunaUConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:
    """Allow removal of child devices (zones/GPIOs) that are no longer needed."""
    uid = _device_uid(config_entry)
    # Don't allow removing the main controller device
    if (DOMAIN, uid) in device_entry.identifiers:
        return False
    return True


async def _async_update_listener(hass: HomeAssistant, entry: LunaUConfigEntry) -> None:
    """Handle options updates."""
    await hass.config_entries.async_reload(entry.entry_id)
