"""Coordinator for polling Luna-U state."""
from __future__ import annotations

import asyncio
import copy
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import LunaUClient
from .const import DEFAULT_POLL_INTERVAL
from .utils import parse_bool, parse_float, parse_int

_LOGGER = logging.getLogger(__name__)


class LunaUCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """DataUpdateCoordinator for Luna-U."""

    OFFLINE_RETRY_BASE_SECONDS = 15
    OFFLINE_RETRY_MAX_SECONDS = 300

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
        self._offline_failures = 0
        self._was_available = True

    def _next_offline_retry_delay(self) -> int:
        """Return next retry delay for unavailable transport failures."""
        self._offline_failures += 1
        return min(
            self.OFFLINE_RETRY_MAX_SECONDS,
            self.OFFLINE_RETRY_BASE_SECONDS * (2 ** (self._offline_failures - 1)),
        )

    def _mark_available(self) -> None:
        """Reset unavailable state and log recovery transition once."""
        if not self._was_available:
            _LOGGER.info(
                "Luna-U at %s:%s is reachable again",
                self.client.host,
                self.client.port,
            )
        self._was_available = True
        self._offline_failures = 0

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            if not self.client.connected:
                await self.client.ensure_connected()

            zones: dict[int, dict[str, Any]] = {i: {} for i in range(1, self.zone_count + 1)}
            gpos: dict[int, dict[str, Any]] = {i: {} for i in range(1, self.gpo_count + 1)}

            # Bulk query zone volumes
            result = await self.client.get_value("ALL_ZONES", "VOLUME")
            if result:
                values = result.arguments.split("^")
                for i, raw in enumerate(values[: self.zone_count], start=1):
                    parsed = parse_float(raw)
                    _LOGGER.debug("Zone %d volume: raw=%s parsed=%s", i, raw, parsed)
                    zones[i]["volume_db"] = parsed

            # Bulk query zone mutes
            result = await self.client.get_value("ALL_ZONES", "MUTE")
            if result:
                values = result.arguments.split("^")
                for i, raw in enumerate(values[: self.zone_count], start=1):
                    parsed = parse_bool(raw)
                    _LOGGER.debug("Zone %d mute: raw=%s parsed=%s", i, raw, parsed)
                    zones[i]["mute"] = parsed

            # Bulk query zone routes
            result = await self.client.get_value("ALL_ZONES", "ROUTE")
            if result:
                values = result.arguments.split("^")
                for i, raw in enumerate(values[: self.zone_count], start=1):
                    parsed = parse_int(raw)
                    _LOGGER.debug("Zone %d route: raw=%s parsed=%s", i, raw, parsed)
                    zones[i]["route"] = parsed

            # Bulk query GPO states
            result = await self.client.get_value("ALL_GPIO", "GPO_ENABLE")
            if result:
                values = result.arguments.split("^")
                for i, raw in enumerate(values[: self.gpo_count], start=1):
                    parsed = parse_bool(raw)
                    _LOGGER.debug("GPO %d enabled: raw=%s parsed=%s", i, raw, parsed)
                    gpos[i]["enabled"] = parsed

            _LOGGER.debug("Coordinator update complete: zones=%s gpos=%s", zones, gpos)
            self._mark_available()
            return {"zones": zones, "gpos": gpos}
        except (ConnectionError, OSError, TimeoutError, asyncio.TimeoutError) as exc:
            retry_delay = self._next_offline_retry_delay()
            if self._was_available:
                _LOGGER.info(
                    "Luna-U at %s:%s became unavailable: %s",
                    self.client.host,
                    self.client.port,
                    exc,
                )
                self._was_available = False
            else:
                _LOGGER.debug(
                    "Luna-U at %s:%s still unavailable: %s. Next retry in %ss",
                    self.client.host,
                    self.client.port,
                    exc,
                    retry_delay,
                )
            raise UpdateFailed(
                f"Device unavailable: {exc}",
                retry_after=timedelta(seconds=retry_delay),
            ) from exc
        except Exception as exc:
            raise UpdateFailed(str(exc)) from exc

    def update_zone(self, zone: int, **fields: Any) -> None:
        data = copy.deepcopy(self.data or {"zones": {}, "gpos": {}})
        zones = data.get("zones", {})
        zone_data = zones.get(zone, {})
        zone_data.update(fields)
        zones[zone] = zone_data
        data["zones"] = zones
        self.async_set_updated_data(data)

    def update_gpo(self, gpo: int, **fields: Any) -> None:
        data = copy.deepcopy(self.data or {"zones": {}, "gpos": {}})
        gpos = data.get("gpos", {})
        gpo_data = gpos.get(gpo, {})
        gpo_data.update(fields)
        gpos[gpo] = gpo_data
        data["gpos"] = gpos
        self.async_set_updated_data(data)
