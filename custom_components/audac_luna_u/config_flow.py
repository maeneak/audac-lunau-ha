"""Config flow for Audac Luna-U."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT

from .client import LunaUClient
from .const import (
    DOMAIN,
    DEFAULT_ADDRESS,
    DEFAULT_PORT,
    DEFAULT_ZONES,
    DEFAULT_INPUTS,
    DEFAULT_GPO_COUNT,
    DEFAULT_POLL_INTERVAL,
    CONF_ADDRESS,
    CONF_ZONES,
    CONF_INPUTS,
    CONF_GPO_COUNT,
    CONF_POLL_INTERVAL,
    CONF_ZONE_NAMES,
    CONF_INPUT_NAMES,
    CONF_GPO_NAMES,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_ADDRESS, default=DEFAULT_ADDRESS): int,
        vol.Optional(CONF_ZONE_NAMES, default=""): str,
        vol.Optional(CONF_INPUT_NAMES, default=""): str,
        vol.Optional(CONF_GPO_NAMES, default=""): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Audac Luna-U."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            address = user_input.get(CONF_ADDRESS, DEFAULT_ADDRESS)

            try:
                client = LunaUClient(host, port, address)
                await client.connect()
                await client.close()
            except Exception:  # pragma: no cover - network dependent
                _LOGGER.exception("Failed to connect to Luna-U")
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=host,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, user_input: dict[str, Any]):
        return await self.async_step_user(user_input)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ZONES,
                        default=self.config_entry.options.get(CONF_ZONES, DEFAULT_ZONES),
                    ): vol.Coerce(int),
                    vol.Optional(
                        CONF_INPUTS,
                        default=self.config_entry.options.get(CONF_INPUTS, DEFAULT_INPUTS),
                    ): vol.Coerce(int),
                    vol.Optional(
                        CONF_GPO_COUNT,
                        default=self.config_entry.options.get(CONF_GPO_COUNT, DEFAULT_GPO_COUNT),
                    ): vol.Coerce(int),
                    vol.Optional(
                        CONF_POLL_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
                        ),
                    ): vol.Coerce(int),
                    vol.Optional(
                        CONF_ZONE_NAMES,
                        default=self.config_entry.options.get(CONF_ZONE_NAMES, ""),
                    ): str,
                    vol.Optional(
                        CONF_INPUT_NAMES,
                        default=self.config_entry.options.get(CONF_INPUT_NAMES, ""),
                    ): str,
                    vol.Optional(
                        CONF_GPO_NAMES,
                        default=self.config_entry.options.get(CONF_GPO_NAMES, ""),
                    ): str,
                }
            ),
        )
