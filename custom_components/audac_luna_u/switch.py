"""Switch platform for Luna-U GPIO outputs."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DEFAULT_GPO_COUNT,
    CONF_GPO_COUNT,
    CONF_GPO_NAMES,
    DATA_COORDINATOR,
    NAME_DELIMITER,
)
from .coordinator import LunaUCoordinator


def _split_names(raw: str | None, count: int, prefix: str) -> list[str]:
    if not raw:
        return [f"{prefix} {i}" for i in range(1, count + 1)]
    parts = [p.strip() for p in raw.split(NAME_DELIMITER)]
    parts = [p for p in parts if p]
    names = []
    for i in range(1, count + 1):
        names.append(parts[i - 1] if i - 1 < len(parts) else f"{prefix} {i}")
    return names


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: LunaUCoordinator = data[DATA_COORDINATOR]

    gpo_count = entry.options.get(CONF_GPO_COUNT, DEFAULT_GPO_COUNT)
    gpo_names = _split_names(
        entry.options.get(CONF_GPO_NAMES) or entry.data.get(CONF_GPO_NAMES),
        gpo_count,
        "GPIO",
    )

    entities = [
        LunaGpoSwitch(
            coordinator=coordinator,
            entry_id=entry.entry_id,
            gpo_index=i + 1,
            gpo_name=gpo_names[i],
        )
        for i in range(gpo_count)
    ]
    async_add_entities(entities)


class LunaGpoSwitch(CoordinatorEntity[LunaUCoordinator], SwitchEntity):
    """GPIO output as a switch."""

    _attr_should_poll = False

    def __init__(
        self,
        coordinator: LunaUCoordinator,
        entry_id: str,
        gpo_index: int,
        gpo_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._gpo = gpo_index
        self._name = gpo_name

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_gpo_{self._gpo}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="Audac Luna-U",
            manufacturer="Audac",
            model="Luna-U",
        )

    @property
    def is_on(self) -> bool | None:
        state = self.coordinator.data.get("gpos", {}).get(self._gpo, {}) if self.coordinator.data else {}
        return state.get("enabled")

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.client.set_value(
            target=f"GPO>{self._gpo}>GPO_TRIGGER>1",
            command="GPO_ENABLE",
            arguments="TRUE",
            wait_for_response=False,
        )
        self.coordinator.update_gpo(self._gpo, enabled=True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.client.set_value(
            target=f"GPO>{self._gpo}>GPO_TRIGGER>1",
            command="GPO_ENABLE",
            arguments="FALSE",
            wait_for_response=False,
        )
        self.coordinator.update_gpo(self._gpo, enabled=False)
