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
from .utils import parse_bool, parse_int

_LOGGER = logging.getLogger(__name__)


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
        # Limit concurrent requests to avoid overflowing the client queue or device
        self._semaphore = asyncio.Semaphore(10)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            # Short-circuit if the client is disconnected to avoid flooding
            if not self.client.connected:
                try:
                    await self.client.ensure_connected()
                except ConnectionError as exc:
                    raise UpdateFailed(f"Device unreachable: {exc}") from exc

            # Build all query tasks for parallel execution
            tasks = []
            task_map = []  # Track what each task is for
            
            async def _throttled_get_value(target: str, command: str) -> Any:
                async with self._semaphore:
                    return await self.client.get_value(target, command)

            # Zone queries
            for zone in range(1, self.zone_count + 1):
                tasks.append(_throttled_get_value(f"ZONE>{zone}>VOLUME>1", "VOLUME"))
                task_map.append(("zone", zone, "volume_db"))
                
                tasks.append(_throttled_get_value(f"ZONE>{zone}>VOLUME>1", "MUTE"))
                task_map.append(("zone", zone, "mute"))
                
                tasks.append(_throttled_get_value(f"ZONE>{zone}>MIXER>1", "ROUTE"))
                task_map.append(("zone", zone, "route"))
            
            # GPO queries
            for gpo in range(1, self.gpo_count + 1):
                tasks.append(_throttled_get_value(f"GPO>{gpo}>GPO_TRIGGER>1", "GPO_ENABLE"))
                task_map.append(("gpo", gpo, "enabled"))

            
            # Execute all queries in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Parse results
            zones: dict[int, dict[str, Any]] = {i: {} for i in range(1, self.zone_count + 1)}
            gpos: dict[int, dict[str, Any]] = {i: {} for i in range(1, self.gpo_count + 1)}
            
            for result, (entity_type, entity_id, field) in zip(results, task_map):
                if isinstance(result, Exception):
                    _LOGGER.debug("Query failed for %s %s %s: %s", entity_type, entity_id, field, result)
                    continue
                    
                if entity_type == "zone":
                    if field == "volume_db":
                        zones[entity_id][field] = parse_int(result.arguments) if result else None
                    elif field == "mute":
                        zones[entity_id][field] = parse_bool(result.arguments) if result else None
                    elif field == "route":
                        zones[entity_id][field] = parse_int(result.arguments) if result else None
                elif entity_type == "gpo":
                    if field == "enabled":
                        gpos[entity_id][field] = parse_bool(result.arguments) if result else None

            return {"zones": zones, "gpos": gpos}
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
