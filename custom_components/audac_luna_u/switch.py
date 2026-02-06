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
    DATA_COORDINATOR,
)
from .coordinator import LunaUCoordinator
from .utils import get_entity_names


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: LunaUCoordinator = data[DATA_COORDINATOR]

    gpo_count = entry.options.get(CONF_GPO_COUNT, DEFAULT_GPO_COUNT)
    gpo_names = get_entity_names(entry.options, gpo_count, "GPIO")

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

    _attr_has_entity_name = True

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

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

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
