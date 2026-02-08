"""Switch platform for Luna-U GPIO outputs."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LunaUConfigEntry, _device_uid
from .const import (
    DOMAIN,
    DEFAULT_GPO_COUNT,
    CONF_GPO_COUNT,
)
from .coordinator import LunaUCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LunaUConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    uid = _device_uid(entry)
    gpo_count = entry.options.get(CONF_GPO_COUNT, DEFAULT_GPO_COUNT)

    async_add_entities(
        LunaGpoSwitch(
            coordinator=coordinator,
            uid=uid,
            gpo_index=i + 1,
        )
        for i in range(gpo_count)
    )


class LunaGpoSwitch(CoordinatorEntity[LunaUCoordinator], SwitchEntity):
    """GPIO output as a switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LunaUCoordinator,
        uid: str,
        gpo_index: int,
    ) -> None:
        super().__init__(coordinator)
        self._gpo = gpo_index
        self._attr_unique_id = f"{uid}_gpo_{gpo_index}"
        self._attr_name = f"GPIO {gpo_index}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{uid}_gpios")},
            name="GPIO Outputs",
            manufacturer="Audac",
            model="Luna-U GPIOs",
            via_device=(DOMAIN, uid),
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
