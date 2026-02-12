from __future__ import annotations

import pytest

from tests.conftest import EntityFakeClient
from custom_components.audac_luna_u.coordinator import LunaUCoordinator
from custom_components.audac_luna_u.media_player import LunaZoneMediaPlayer


@pytest.mark.asyncio
async def test_media_player_state_mapping(hass) -> None:
    client = EntityFakeClient()
    coordinator = LunaUCoordinator(hass, client=client, zone_count=1, input_count=2, gpo_count=1)
    coordinator.data = {"zones": {1: {"volume_db": -45.0, "mute": False, "route": 2}}, "gpos": {}}
    coordinator.last_update_success = True

    entity = LunaZoneMediaPlayer(coordinator, uid="uid", zone_index=1, input_names=["Mic", "Music"])

    assert entity.available is True
    assert entity.volume_level == 0.5
    assert entity.is_volume_muted is False
    assert entity.source == "Music"
    assert entity.source_list == ["Off", "Mic", "Music"]


@pytest.mark.asyncio
async def test_media_player_commands_dispatch(hass) -> None:
    client = EntityFakeClient()
    coordinator = LunaUCoordinator(hass, client=client, zone_count=1, input_count=2, gpo_count=1)
    coordinator.data = {"zones": {1: {"volume_db": -60.0, "mute": False, "route": 1}}, "gpos": {}}
    coordinator.last_update_success = True

    entity = LunaZoneMediaPlayer(coordinator, uid="uid", zone_index=1, input_names=["Mic", "Music"])
    await entity.async_set_volume_level(1.0)
    await entity.async_mute_volume(True)
    await entity.async_select_source("Off")

    assert len(client.calls) == 3
    assert client.calls[0]["target"] == "ZONE>1>VOLUME>1"
    assert client.calls[0]["command"] == "VOLUME"
    assert client.calls[0]["arguments"] == "0"
    assert client.calls[1]["command"] == "MUTE"
    assert client.calls[1]["arguments"] == "TRUE"
    assert client.calls[2]["target"] == "ZONE>1>MIXER>1"
    assert client.calls[2]["command"] == "ROUTE"
    assert client.calls[2]["arguments"] == "0"


@pytest.mark.asyncio
async def test_media_player_branch_states(hass) -> None:
    client = EntityFakeClient()
    coordinator = LunaUCoordinator(hass, client=client, zone_count=1, input_count=3, gpo_count=1)
    coordinator.last_update_success = True
    entity = LunaZoneMediaPlayer(coordinator, uid="uid", zone_index=1, input_names=["A", "B", "C"])

    coordinator.data = {"zones": {1: {}}, "gpos": {}}
    assert entity.state.value == "idle"
    assert entity.source is None

    coordinator.data = {"zones": {1: {"route": -1, "mute": False}}, "gpos": {}}
    assert entity.source == "Mixed"

    coordinator.data = {"zones": {1: {"route": 0, "mute": False}}, "gpos": {}}
    assert entity.source == "Off"
    assert entity.state.value == "idle"

    coordinator.data = {"zones": {1: {"route": 99, "mute": False}}, "gpos": {}}
    assert entity.source == "Input 99"

    await entity.async_select_source("does_not_exist")
    assert len(client.calls) == 0


@pytest.mark.asyncio
async def test_media_player_volume_step_and_power_wrappers(hass) -> None:
    client = EntityFakeClient()
    coordinator = LunaUCoordinator(hass, client=client, zone_count=1, input_count=1, gpo_count=1)
    coordinator.data = {"zones": {1: {"volume_db": -50.0, "mute": False, "route": 1}}, "gpos": {}}
    coordinator.last_update_success = True
    entity = LunaZoneMediaPlayer(coordinator, uid="uid", zone_index=1, input_names=["A"])

    await entity.async_volume_up()
    await entity.async_volume_down()
    await entity.async_turn_on()
    await entity.async_turn_off()

    # volume up/down + mute false + mute true
    assert len(client.calls) == 4
    assert client.calls[2]["command"] == "MUTE"
    assert client.calls[2]["arguments"] == "FALSE"
    assert client.calls[3]["arguments"] == "TRUE"
