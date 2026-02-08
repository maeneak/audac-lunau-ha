"""Media player platform for Luna-U zones."""
from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LunaUConfigEntry, _device_uid
from .const import (
    DOMAIN,
    DEFAULT_ADDRESS,
    DEFAULT_INPUTS,
    DEFAULT_ZONES,
    CONF_ADDRESS,
    CONF_INPUTS,
    CONF_ZONES,
)
from .coordinator import LunaUCoordinator

MIN_DB = -90
MAX_DB = 0
VOLUME_STEP = 0.05  # 5% volume step for up/down


def _db_to_level(db: float | None) -> float | None:
    if db is None:
        return None
    db = max(MIN_DB, min(MAX_DB, db))
    return (db - MIN_DB) / (MAX_DB - MIN_DB)


def _level_to_db(level: float) -> int:
    level = max(0.0, min(1.0, level))
    db = MIN_DB + (MAX_DB - MIN_DB) * level
    return int(round(db))


def _get_input_names(config: dict, count: int) -> list[str]:
    """Get input names from config."""
    return [
        config.get(f"Input {i}", f"Input {i}")
        for i in range(1, count + 1)
    ]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LunaUConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    uid = _device_uid(entry)

    zone_count = entry.options.get(CONF_ZONES, DEFAULT_ZONES)
    input_count = entry.options.get(CONF_INPUTS, DEFAULT_INPUTS)
    input_names = _get_input_names(entry.options, input_count)

    async_add_entities(
        LunaZoneMediaPlayer(
            coordinator=coordinator,
            uid=uid,
            zone_index=i + 1,
            input_names=input_names,
        )
        for i in range(zone_count)
    )


class LunaZoneMediaPlayer(CoordinatorEntity[LunaUCoordinator], MediaPlayerEntity):
    """Representation of a Luna-U zone."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
    )

    def __init__(
        self,
        coordinator: LunaUCoordinator,
        uid: str,
        zone_index: int,
        input_names: list[str],
    ) -> None:
        super().__init__(coordinator)
        self._zone = zone_index
        self._input_names = input_names
        self._attr_unique_id = f"{uid}_zone_{zone_index}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{uid}_zone_{zone_index}")},
            name=f"Zone {zone_index}",
            manufacturer="Audac",
            model="Luna-U Zone",
            via_device=(DOMAIN, uid),
        )

    @property
    def _zone_state(self) -> dict:
        """Return the current zone state dict."""
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get("zones", {}).get(self._zone, {})

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the zone."""
        zone_state = self._zone_state
        muted = zone_state.get("mute")
        route = zone_state.get("route")
        if muted is None or route is None:
            return MediaPlayerState.IDLE
        if muted or route == 0:
            return MediaPlayerState.IDLE
        return MediaPlayerState.PLAYING

    @property
    def volume_level(self) -> float | None:
        return _db_to_level(self._zone_state.get("volume_db"))

    @property
    def is_volume_muted(self) -> bool | None:
        return self._zone_state.get("mute")

    @property
    def source_list(self) -> list[str]:
        return ["Off"] + self._input_names

    @property
    def source(self) -> str | None:
        """Return the current source."""
        route = self._zone_state.get("route")
        if route is None:
            return None
        if route == -1:
            return "Mixed"
        if route == 0:
            return "Off"
        if 1 <= route <= len(self._input_names):
            return self._input_names[route - 1]
        return f"Input {route}"

    async def async_set_volume_level(self, volume: float) -> None:
        db = _level_to_db(volume)
        await self.coordinator.client.set_value(
            target=f"ZONE>{self._zone}>VOLUME>1",
            command="VOLUME",
            arguments=str(db),
            wait_for_response=False,
        )
        self.coordinator.update_zone(self._zone, volume_db=db)

    async def async_mute_volume(self, mute: bool) -> None:
        await self.coordinator.client.set_value(
            target=f"ZONE>{self._zone}>VOLUME>1",
            command="MUTE",
            arguments="TRUE" if mute else "FALSE",
            wait_for_response=False,
        )
        self.coordinator.update_zone(self._zone, mute=mute)

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        if source == "Off":
            route = 0
        else:
            try:
                route = self._input_names.index(source) + 1
            except ValueError:
                return
        await self.coordinator.client.set_value(
            target=f"ZONE>{self._zone}>MIXER>1",
            command="ROUTE",
            arguments=str(route),
            wait_for_response=False,
        )
        self.coordinator.update_zone(self._zone, route=route)

    async def async_volume_up(self) -> None:
        """Increase volume by step."""
        current = self.volume_level or 0.0
        new_level = min(1.0, current + VOLUME_STEP)
        await self.async_set_volume_level(new_level)

    async def async_volume_down(self) -> None:
        """Decrease volume by step."""
        current = self.volume_level or 0.0
        new_level = max(0.0, current - VOLUME_STEP)
        await self.async_set_volume_level(new_level)

    async def async_turn_on(self) -> None:
        """Turn on the zone (unmute)."""
        await self.async_mute_volume(False)

    async def async_turn_off(self) -> None:
        """Turn off the zone (mute)."""
        await self.async_mute_volume(True)
