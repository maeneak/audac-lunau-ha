"""Coordinator for polling Luna-U state."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import LunaUClient
from .const import DEFAULT_POLL_INTERVAL

_LOGGER = logging.getLogger(__name__)


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    val = value.strip().upper()
    if val == "TRUE":
        return True
    if val == "FALSE":
        return False
    return None


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


class LunaUCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """DataUpdateCoordinator for Luna-U."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LunaUClient,
        zone_count: int,
        input_count: int,
        gpo_count: int,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="audac_luna_u",
            update_interval=timedelta(seconds=poll_interval),
        )
        self.client = client
        self.zone_count = zone_count
        self.input_count = input_count
        self.gpo_count = gpo_count

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            zones: dict[int, dict[str, Any]] = {}
            for zone in range(1, self.zone_count + 1):
                volume_msg = await self.client.get_value(
                    target=f"ZONE>{zone}>VOLUME>1",
                    command="VOLUME",
                )
                mute_msg = await self.client.get_value(
                    target=f"ZONE>{zone}>VOLUME>1",
                    command="MUTE",
                )
                route_msg = await self.client.get_value(
                    target=f"ZONE>{zone}>MIXER>1",
                    command="ROUTE",
                )
                zones[zone] = {
                    "volume_db": _parse_int(volume_msg.arguments) if volume_msg else None,
                    "mute": _parse_bool(mute_msg.arguments) if mute_msg else None,
                    "route": _parse_int(route_msg.arguments) if route_msg else None,
                }

            gpos: dict[int, dict[str, Any]] = {}
            for gpo in range(1, self.gpo_count + 1):
                gpo_msg = await self.client.get_value(
                    target=f"GPO>{gpo}>GPO_TRIGGER>1",
                    command="GPO_ENABLE",
                )
                gpos[gpo] = {
                    "enabled": _parse_bool(gpo_msg.arguments) if gpo_msg else None,
                }

            return {"zones": zones, "gpos": gpos}
        except Exception as exc:
            raise UpdateFailed(str(exc)) from exc

    def update_zone(self, zone: int, **fields: Any) -> None:
        data = dict(self.data or {"zones": {}, "gpos": {}})
        zones = dict(data.get("zones", {}))
        zone_data = dict(zones.get(zone, {}))
        zone_data.update(fields)
        zones[zone] = zone_data
        data["zones"] = zones
        self.async_set_updated_data(data)

    def update_gpo(self, gpo: int, **fields: Any) -> None:
        data = dict(self.data or {"zones": {}, "gpos": {}})
        gpos = dict(data.get("gpos", {}))
        gpo_data = dict(gpos.get(gpo, {}))
        gpo_data.update(fields)
        gpos[gpo] = gpo_data
        data["gpos"] = gpos
        self.async_set_updated_data(data)
