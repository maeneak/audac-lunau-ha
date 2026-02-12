from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from homeassistant.const import CONF_HOST, CONF_PORT
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.audac_luna_u import (
    ATTR_SNAPSHOT_NAME,
    LunaURuntimeData,
    SERVICE_APPLY_SNAPSHOT,
    _cleanup_legacy_naming_keys,
    _device_uid,
    async_remove_config_entry_device,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.audac_luna_u.const import CONF_ADDRESS, DOMAIN


def test_cleanup_legacy_naming_keys() -> None:
    original = {"Zone 1": "Lobby", "GPIO 1": "Out", "poll_interval": 10}
    cleaned = _cleanup_legacy_naming_keys(original)
    assert cleaned == {"poll_interval": 10}


@pytest.mark.asyncio
async def test_setup_entry_registers_service(hass) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: 5001, CONF_ADDRESS: 1},
        options={"poll_interval": 10},
    )
    entry.add_to_hass(hass)

    with (
        patch.object(hass.config_entries, "async_forward_entry_setups", AsyncMock(return_value=True)),
        patch("custom_components.audac_luna_u.LunaUClient.connect", new=AsyncMock()),
        patch("custom_components.audac_luna_u.LunaUCoordinator.async_config_entry_first_refresh", new=AsyncMock()),
    ):
        assert await async_setup_entry(hass, entry) is True

    assert hass.services.has_service(DOMAIN, SERVICE_APPLY_SNAPSHOT)
    assert hasattr(entry, "runtime_data")


@pytest.mark.asyncio
async def test_unload_entry_closes_client_and_removes_service(hass) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: 5001, CONF_ADDRESS: 1},
    )
    entry.add_to_hass(hass)

    fake_client = SimpleNamespace(close=AsyncMock())
    fake_coordinator = SimpleNamespace()
    entry.runtime_data = LunaURuntimeData(client=fake_client, coordinator=fake_coordinator)  # type: ignore[arg-type]

    hass.services.async_register(DOMAIN, SERVICE_APPLY_SNAPSHOT, lambda call: None)
    assert hass.services.has_service(DOMAIN, SERVICE_APPLY_SNAPSHOT)

    with (
        patch.object(hass.config_entries, "async_unload_platforms", AsyncMock(return_value=True)),
        patch.object(hass.config_entries, "async_entries", return_value=[entry]),
    ):
        assert await async_unload_entry(hass, entry) is True

    fake_client.close.assert_awaited_once()
    assert not hass.services.has_service(DOMAIN, SERVICE_APPLY_SNAPSHOT)


@pytest.mark.asyncio
async def test_async_remove_config_entry_device_blocks_main_controller(hass) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: 5001, CONF_ADDRESS: 1},
    )
    uid = _device_uid(entry)
    main_device = SimpleNamespace(identifiers={(DOMAIN, uid)})
    child_device = SimpleNamespace(identifiers={(DOMAIN, f"{uid}_zone_1")})

    assert await async_remove_config_entry_device(hass, entry, main_device) is False
    assert await async_remove_config_entry_device(hass, entry, child_device) is True
