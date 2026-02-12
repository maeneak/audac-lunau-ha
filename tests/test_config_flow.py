from __future__ import annotations

from unittest.mock import AsyncMock, patch

import custom_components.audac_luna_u.config_flow as cfg_flow_module
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.data_entry_flow import FlowResultType
from packaging.version import Version
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.audac_luna_u.const import (
    CONF_ADDRESS,
    CONF_GPO_COUNT,
    CONF_INPUTS,
    CONF_POLL_INTERVAL,
    CONF_ZONES,
    DEFAULT_ADDRESS,
    DEFAULT_PORT,
    DOMAIN,
)

SOURCE_USER = "user"
SOURCE_RECONFIGURE = "reconfigure"
REQUIRES_NEW_HA = Version(HA_VERSION) < Version("2025.11.0")


@pytest.mark.asyncio
async def test_user_flow_creates_entry(hass) -> None:
    user_input = {CONF_HOST: "127.0.0.1", CONF_PORT: 5001, CONF_ADDRESS: 1}
    with (
        patch("custom_components.audac_luna_u.config_flow.LunaUClient.connect", new=AsyncMock()),
        patch("custom_components.audac_luna_u.config_flow.LunaUClient.close", new=AsyncMock()),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data=user_input,
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "127.0.0.1"
    assert result["data"] == user_input


@pytest.mark.asyncio
async def test_user_flow_cannot_connect(hass) -> None:
    with (
        patch(
            "custom_components.audac_luna_u.config_flow.LunaUClient.connect",
            new=AsyncMock(side_effect=ConnectionError("offline")),
        ),
        patch("custom_components.audac_luna_u.config_flow.LunaUClient.close", new=AsyncMock()),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data={CONF_HOST: "127.0.0.1", CONF_PORT: 5001, CONF_ADDRESS: 1},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"]["base"] == "cannot_connect"


@pytest.mark.asyncio
@pytest.mark.skipif(REQUIRES_NEW_HA, reason="Requires Home Assistant 2025.11+ reconfigure flow APIs")
async def test_reconfigure_flow_updates_entry(hass) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: DEFAULT_PORT, CONF_ADDRESS: DEFAULT_ADDRESS},
    )
    entry.add_to_hass(hass)

    with (
        patch("custom_components.audac_luna_u.config_flow.LunaUClient.connect", new=AsyncMock()),
        patch("custom_components.audac_luna_u.config_flow.LunaUClient.close", new=AsyncMock()),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
            data={CONF_HOST: "127.0.0.2", CONF_PORT: 5002, CONF_ADDRESS: 2},
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"


@pytest.mark.asyncio
@pytest.mark.skipif(REQUIRES_NEW_HA, reason="Requires Home Assistant 2025.11+ options flow APIs")
async def test_options_flow(hass) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: DEFAULT_PORT, CONF_ADDRESS: DEFAULT_ADDRESS},
        options={
            CONF_ZONES: 8,
            CONF_INPUTS: 2,
            CONF_GPO_COUNT: 12,
            CONF_POLL_INTERVAL: 10,
            "Input 1": "A",
            "Input 2": "B",
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_ZONES: 4,
            CONF_INPUTS: 2,
            CONF_GPO_COUNT: 6,
            CONF_POLL_INTERVAL: 20,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "input_names"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"Input 1": "Mic", "Input 2": "Music"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_ZONES] == 4
    assert result["data"]["Input 1"] == "Mic"


@pytest.mark.asyncio
async def test_reconfigure_step_direct_show_form() -> None:
    flow = cfg_flow_module.ConfigFlow()
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: DEFAULT_PORT, CONF_ADDRESS: DEFAULT_ADDRESS},
    )
    flow._get_reconfigure_entry = lambda: entry  # type: ignore[attr-defined]
    flow.async_show_form = lambda **kwargs: kwargs  # type: ignore[assignment]

    result = await flow.async_step_reconfigure()
    assert result["step_id"] == "reconfigure"
    assert "data_schema" in result


@pytest.mark.asyncio
async def test_reconfigure_step_direct_success() -> None:
    flow = cfg_flow_module.ConfigFlow()
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: DEFAULT_PORT, CONF_ADDRESS: DEFAULT_ADDRESS},
    )
    flow._get_reconfigure_entry = lambda: entry  # type: ignore[attr-defined]
    flow.async_update_reload_and_abort = (  # type: ignore[assignment]
        lambda _entry, data: {"type": "abort", "reason": "reconfigure_successful", "data": data}
    )

    with (
        patch("custom_components.audac_luna_u.config_flow.LunaUClient.connect", new=AsyncMock()),
        patch("custom_components.audac_luna_u.config_flow.LunaUClient.close", new=AsyncMock()),
    ):
        result = await flow.async_step_reconfigure(
            {CONF_HOST: "127.0.0.2", CONF_PORT: 5002, CONF_ADDRESS: 2}
        )

    assert result["reason"] == "reconfigure_successful"
    assert result["data"][CONF_HOST] == "127.0.0.2"


@pytest.mark.asyncio
async def test_reconfigure_step_direct_cannot_connect() -> None:
    flow = cfg_flow_module.ConfigFlow()
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: DEFAULT_PORT, CONF_ADDRESS: DEFAULT_ADDRESS},
    )
    flow._get_reconfigure_entry = lambda: entry  # type: ignore[attr-defined]
    flow.async_show_form = lambda **kwargs: kwargs  # type: ignore[assignment]

    with (
        patch(
            "custom_components.audac_luna_u.config_flow.LunaUClient.connect",
            new=AsyncMock(side_effect=ConnectionError("offline")),
        ),
        patch("custom_components.audac_luna_u.config_flow.LunaUClient.close", new=AsyncMock()),
    ):
        result = await flow.async_step_reconfigure(
            {CONF_HOST: "127.0.0.2", CONF_PORT: 5002, CONF_ADDRESS: 2}
        )

    assert result["errors"]["base"] == "cannot_connect"
    assert result["step_id"] == "reconfigure"


@pytest.mark.asyncio
async def test_options_flow_handler_direct_paths() -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: DEFAULT_PORT, CONF_ADDRESS: DEFAULT_ADDRESS},
        options={CONF_INPUTS: 2, "Input 1": "A", "Input 2": "B"},
    )

    handler = cfg_flow_module.OptionsFlowHandler()
    handler.config_entry = entry  # type: ignore[attr-defined]
    handler.async_show_form = lambda **kwargs: kwargs  # type: ignore[assignment]
    handler.async_create_entry = lambda title, data: {"title": title, "data": data}  # type: ignore[assignment]

    form = await handler.async_step_init(None)
    assert form["step_id"] == "init"

    next_form = await handler.async_step_init(
        {
            CONF_ZONES: 4,
            CONF_INPUTS: 2,
            CONF_GPO_COUNT: 6,
            CONF_POLL_INTERVAL: 20,
        }
    )
    assert next_form["step_id"] == "input_names"

    create_no_inputs = await handler.async_step_init(
        {
            CONF_ZONES: 2,
            CONF_INPUTS: 0,
            CONF_GPO_COUNT: 1,
            CONF_POLL_INTERVAL: 10,
        }
    )
    assert create_no_inputs["data"][CONF_INPUTS] == 0

    names_form = await handler.async_step_input_names(None)
    assert names_form["step_id"] == "input_names"

    created = await handler.async_step_input_names({"Input 1": "Mic", "Input 2": "Music"})
    assert created["data"]["Input 1"] == "Mic"
