from __future__ import annotations

from dataclasses import dataclass

import pytest
import pytest_socket
from homeassistant.const import CONF_HOST, CONF_PORT
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.audac_luna_u import LunaURuntimeData
from custom_components.audac_luna_u.client import LunaMessage, LunaUClient
from custom_components.audac_luna_u.const import (
    CONF_ADDRESS,
    CONF_GPO_COUNT,
    CONF_INPUTS,
    CONF_POLL_INTERVAL,
    CONF_ZONES,
    DEFAULT_ADDRESS,
    DEFAULT_GPO_COUNT,
    DEFAULT_INPUTS,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_ZONES,
    DOMAIN,
)


def _noop_disable_socket(*args, **kwargs) -> None:
    return None


# pytest-homeassistant-custom-component force-disables sockets in pytest_runtest_setup,
# which breaks ProactorEventLoop startup on Windows due socketpair() internals.
pytest_socket.disable_socket = _noop_disable_socket


@dataclass
class DummyCoordinator:
    zone_count: int = DEFAULT_ZONES
    input_count: int = DEFAULT_INPUTS
    gpo_count: int = DEFAULT_GPO_COUNT
    data: dict | None = None
    last_update_success: bool = True


class FakeLunaClient(LunaUClient):
    def __init__(self, host: str = "127.0.0.1", port: int = DEFAULT_PORT, address: int = DEFAULT_ADDRESS) -> None:
        super().__init__(host, port, address)
        self.calls: list[dict[str, str | bool]] = []
        self.fail_set = False

    async def set_value(
        self,
        target: str,
        command: str,
        arguments: str,
        wait_for_response: bool = False,
        timeout: float = 2.5,
    ) -> LunaMessage | None:
        self.calls.append(
            {
                "target": target,
                "command": command,
                "arguments": arguments,
                "wait_for_response": wait_for_response,
            }
        )
        if self.fail_set:
            raise ConnectionError("simulated set failure")
        return None


class EntityFakeClient:
    """Lightweight fake client for entity-level tests (media_player, switch)."""

    def __init__(self) -> None:
        self.connected = True
        self.host = "127.0.0.1"
        self.port = 5001
        self.calls: list[dict[str, str | bool]] = []

    async def ensure_connected(self) -> None:
        self.connected = True

    async def get_value(self, target: str, command: str):
        return None

    async def set_value(
        self,
        target: str,
        command: str,
        arguments: str,
        wait_for_response: bool = False,
        timeout: float = 2.5,
    ):
        self.calls.append(
            {
                "target": target,
                "command": command,
                "arguments": arguments,
                "wait_for_response": wait_for_response,
            }
        )
        return None


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "127.0.0.1",
            CONF_PORT: DEFAULT_PORT,
            CONF_ADDRESS: DEFAULT_ADDRESS,
        },
        options={
            CONF_ZONES: DEFAULT_ZONES,
            CONF_INPUTS: DEFAULT_INPUTS,
            CONF_GPO_COUNT: DEFAULT_GPO_COUNT,
            CONF_POLL_INTERVAL: DEFAULT_POLL_INTERVAL,
        },
    )


@pytest.fixture
def runtime_entry(mock_config_entry: MockConfigEntry) -> MockConfigEntry:
    client = FakeLunaClient()
    coordinator = DummyCoordinator(data={"zones": {}, "gpos": {}})
    mock_config_entry.runtime_data = LunaURuntimeData(client=client, coordinator=coordinator)  # type: ignore[arg-type]
    return mock_config_entry
