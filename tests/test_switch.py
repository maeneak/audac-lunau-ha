from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests.conftest import EntityFakeClient
from custom_components.audac_luna_u import LunaURuntimeData
from custom_components.audac_luna_u.const import CONF_GPO_COUNT, DOMAIN
from custom_components.audac_luna_u.coordinator import LunaUCoordinator
from custom_components.audac_luna_u.switch import LunaGpoSwitch, async_setup_entry


@pytest.mark.asyncio
async def test_switch_state_and_commands(hass) -> None:
    client = EntityFakeClient()
    coordinator = LunaUCoordinator(hass, client=client, zone_count=1, input_count=1, gpo_count=1)
    coordinator.data = {"zones": {}, "gpos": {1: {"enabled": False}}}
    coordinator.last_update_success = True

    entity = LunaGpoSwitch(coordinator, uid="uid", gpo_index=1)
    assert entity.available is True
    assert entity.is_on is False

    await entity.async_turn_on()
    await entity.async_turn_off()

    assert len(client.calls) == 2
    assert client.calls[0]["target"] == "GPO>1>GPO_TRIGGER>1"
    assert client.calls[0]["command"] == "GPO_ENABLE"
    assert client.calls[0]["arguments"] == "TRUE"
    assert client.calls[1]["arguments"] == "FALSE"


@pytest.mark.asyncio
async def test_switch_async_setup_entry_adds_entities(hass) -> None:
    client = EntityFakeClient()
    coordinator = LunaUCoordinator(hass, client=client, zone_count=1, input_count=1, gpo_count=3)
    entry = MockConfigEntry(domain=DOMAIN, data={"host": "127.0.0.1"}, options={CONF_GPO_COUNT: 3})
    entry.runtime_data = LunaURuntimeData(client=client, coordinator=coordinator)  # type: ignore[arg-type]

    added: list[LunaGpoSwitch] = []
    await async_setup_entry(hass, entry, lambda entities: added.extend(list(entities)))
    assert len(added) == 3
