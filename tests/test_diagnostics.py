from __future__ import annotations

from types import SimpleNamespace

from homeassistant.const import CONF_HOST
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.audac_luna_u import LunaURuntimeData
from custom_components.audac_luna_u.const import CONF_ADDRESS, DOMAIN
from custom_components.audac_luna_u.diagnostics import async_get_config_entry_diagnostics


@pytest.mark.asyncio
async def test_diagnostics_redacts_host_and_reports_runtime_data(hass) -> None:
    client = SimpleNamespace(connected=True)
    coordinator = SimpleNamespace(
        zone_count=8,
        input_count=8,
        gpo_count=12,
        data={"zones": {}, "gpos": {}},
        last_update_success=True,
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "192.168.1.10", "port": 5001, CONF_ADDRESS: 1},
        options={},
    )
    entry.runtime_data = LunaURuntimeData(client=client, coordinator=coordinator)  # type: ignore[arg-type]

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["connected"] is True
    assert result["last_update_success"] is True
    assert result["zone_count"] == 8
    assert result["config_entry"][CONF_HOST] != "192.168.1.10"
