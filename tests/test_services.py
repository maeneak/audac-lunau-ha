from __future__ import annotations

from types import SimpleNamespace

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
import pytest
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from tests.conftest import DummyCoordinator, FakeLunaClient
from custom_components.audac_luna_u import LunaURuntimeData, _async_handle_apply_snapshot
from custom_components.audac_luna_u.const import CONF_ADDRESS, DOMAIN


def _call(hass, data: dict) -> SimpleNamespace:
    return SimpleNamespace(hass=hass, data=data)


@pytest.mark.asyncio
async def test_apply_snapshot_invalid_name_raises_validation_error(hass) -> None:
    with pytest.raises(ServiceValidationError):
        await _async_handle_apply_snapshot(_call(hass, {"snapshot_name": "!!!"}))


@pytest.mark.asyncio
async def test_apply_snapshot_no_target_devices_raises_validation_error(hass) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: 5001, CONF_ADDRESS: 1},
    )
    entry.runtime_data = LunaURuntimeData(client=FakeLunaClient(), coordinator=DummyCoordinator())  # type: ignore[arg-type]
    entry.add_to_hass(hass)

    with pytest.raises(ServiceValidationError):
        await _async_handle_apply_snapshot(
            _call(hass, {"snapshot_name": "Lobby Day", "device_id": ["does_not_exist"]})
        )


@pytest.mark.asyncio
async def test_apply_snapshot_runtime_failures_raise_homeassistant_error(hass) -> None:
    failing_client = FakeLunaClient()
    failing_client.fail_set = True
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: 5001, CONF_ADDRESS: 1},
    )
    entry.runtime_data = LunaURuntimeData(client=failing_client, coordinator=DummyCoordinator())  # type: ignore[arg-type]
    entry.add_to_hass(hass)

    with pytest.raises(HomeAssistantError):
        await _async_handle_apply_snapshot(_call(hass, {"snapshot_name": "Lobby Day"}))


@pytest.mark.asyncio
async def test_apply_snapshot_success_writes_expected_command(hass) -> None:
    client = FakeLunaClient()
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: 5001, CONF_ADDRESS: 1},
    )
    entry.runtime_data = LunaURuntimeData(client=client, coordinator=DummyCoordinator())  # type: ignore[arg-type]
    entry.add_to_hass(hass)

    await _async_handle_apply_snapshot(_call(hass, {"snapshot_name": "Lobby Day"}))

    assert len(client.calls) == 1
    assert client.calls[0]["target"] == "SNAPSHOTS>1"
    assert client.calls[0]["command"] == "APPLY_SNAPSHOT"
    assert client.calls[0]["arguments"] == "settings/snapshots/Lobby Day.snapshot"


@pytest.mark.asyncio
async def test_apply_snapshot_no_loaded_devices_raises(hass) -> None:
    with pytest.raises(HomeAssistantError):
        await _async_handle_apply_snapshot(_call(hass, {"snapshot_name": "Lobby Day"}))


@pytest.mark.asyncio
async def test_apply_snapshot_device_target_branch(hass) -> None:
    client = FakeLunaClient()
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: 5001, CONF_ADDRESS: 1},
    )
    entry.runtime_data = LunaURuntimeData(client=client, coordinator=DummyCoordinator())  # type: ignore[arg-type]
    entry.add_to_hass(hass)

    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "target")},
        name="Target Device",
    )

    await _async_handle_apply_snapshot(
        _call(hass, {"snapshot_name": "Lobby Day", "device_id": [device.id]})
    )
    assert len(client.calls) == 1
