from __future__ import annotations

from datetime import timedelta
import logging

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.audac_luna_u.client import LunaMessage
from custom_components.audac_luna_u.coordinator import LunaUCoordinator

try:
    UpdateFailed("probe", retry_after=timedelta(seconds=1))
    SUPPORTS_RETRY_AFTER = True
except TypeError:
    SUPPORTS_RETRY_AFTER = False


class CoordinatorFakeClient:
    def __init__(self) -> None:
        self.connected = True
        self.host = "127.0.0.1"
        self.port = 5001
        self._fail_connect = False
        self._data_error: Exception | None = None

    async def ensure_connected(self) -> None:
        if self._fail_connect:
            raise ConnectionError("unreachable")
        self.connected = True

    async def get_value(self, target: str, command: str) -> LunaMessage | None:
        if self._data_error is not None:
            raise self._data_error
        if target == "ALL_ZONES" and command == "VOLUME":
            return LunaMessage("", "", "GET_RSP", target, command, "-10^-20", "U")
        if target == "ALL_ZONES" and command == "MUTE":
            return LunaMessage("", "", "GET_RSP", target, command, "FALSE^TRUE", "U")
        if target == "ALL_ZONES" and command == "ROUTE":
            return LunaMessage("", "", "GET_RSP", target, command, "1^0", "U")
        if target == "ALL_GPIO" and command == "GPO_ENABLE":
            return LunaMessage("", "", "GET_RSP", target, command, "TRUE", "U")
        return None


@pytest.mark.asyncio
async def test_update_success_parses_payloads(hass) -> None:
    client = CoordinatorFakeClient()
    coordinator = LunaUCoordinator(hass, client=client, zone_count=2, input_count=2, gpo_count=1)

    data = await coordinator._async_update_data()

    assert data["zones"][1]["volume_db"] == -10.0
    assert data["zones"][2]["volume_db"] == -20.0
    assert data["zones"][1]["mute"] is False
    assert data["zones"][2]["mute"] is True
    assert data["zones"][1]["route"] == 1
    assert data["zones"][2]["route"] == 0
    assert data["gpos"][1]["enabled"] is True
    assert coordinator._offline_failures == 0
    assert coordinator._was_available is True


@pytest.mark.asyncio
@pytest.mark.skipif(not SUPPORTS_RETRY_AFTER, reason="Requires UpdateFailed(retry_after=...) support")
async def test_update_unavailable_uses_retry_after_backoff(hass, caplog: pytest.LogCaptureFixture) -> None:
    client = CoordinatorFakeClient()
    client.connected = False
    client._fail_connect = True
    coordinator = LunaUCoordinator(hass, client=client, zone_count=1, input_count=1, gpo_count=1)
    caplog.set_level(logging.DEBUG, logger="custom_components.audac_luna_u.coordinator")

    expected = [15, 30, 60, 120, 240, 300]
    for seconds in expected:
        with pytest.raises(UpdateFailed) as err:
            await coordinator._async_update_data()
        assert err.value.retry_after == timedelta(seconds=seconds)

    unavailable_logs = [r for r in caplog.records if "became unavailable" in r.message]
    assert len(unavailable_logs) == 1


@pytest.mark.asyncio
@pytest.mark.skipif(not SUPPORTS_RETRY_AFTER, reason="Requires UpdateFailed(retry_after=...) support")
async def test_update_logs_recovery_once(hass, caplog: pytest.LogCaptureFixture) -> None:
    client = CoordinatorFakeClient()
    client.connected = False
    client._fail_connect = True
    coordinator = LunaUCoordinator(hass, client=client, zone_count=1, input_count=1, gpo_count=1)
    caplog.set_level(logging.INFO, logger="custom_components.audac_luna_u.coordinator")

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    client._fail_connect = False
    await coordinator._async_update_data()
    await coordinator._async_update_data()

    recovery_logs = [r for r in caplog.records if "reachable again" in r.message]
    assert len(recovery_logs) == 1


@pytest.mark.asyncio
async def test_non_connection_errors_do_not_get_offline_retry_after(hass) -> None:
    client = CoordinatorFakeClient()
    client._data_error = ValueError("bad payload")
    coordinator = LunaUCoordinator(hass, client=client, zone_count=1, input_count=1, gpo_count=1)

    with pytest.raises(UpdateFailed) as err:
        await coordinator._async_update_data()

    assert getattr(err.value, "retry_after", None) is None
