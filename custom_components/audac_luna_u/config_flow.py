"""Config flow for Audac Luna-U."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import selector

from .client import LunaUClient
from .const import (
    DOMAIN,
    DEFAULT_ADDRESS,
    DEFAULT_PORT,
    DEFAULT_ZONES,
    DEFAULT_INPUTS,
    DEFAULT_GPO_COUNT,
    DEFAULT_POLL_INTERVAL,
    MAX_ZONES,
    MAX_INPUTS,
    MAX_GPO_COUNT,
    CONF_ADDRESS,
    CONF_ZONES,
    CONF_INPUTS,
    CONF_GPO_COUNT,
    CONF_POLL_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
        vol.Optional(CONF_ADDRESS, default=DEFAULT_ADDRESS): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=255)
        ),
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

            await self.async_set_unique_id(f"{host}_{address}")
            self._abort_if_unique_id_configured()

            client = LunaUClient(host, port, address)
            try:
                await client.connect()
            except Exception:
                _LOGGER.exception("Failed to connect to Luna-U")
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=host,
                    data=user_input,
                )
            finally:
                await client.close()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, user_input: dict[str, Any]):
        return await self.async_step_user(user_input)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for counts, poll interval, and input names."""

    def __init__(self) -> None:
        """Initialize the options flow."""
        self._options: dict[str, Any] = {}

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Step 1: Configure counts and poll interval."""
        if user_input is not None:
            self._options = dict(user_input)
            # If there are inputs, show the naming step, otherwise save immediately
            if self._options.get(CONF_INPUTS, DEFAULT_INPUTS) > 0:
                return await self.async_step_input_names()
            return self.async_create_entry(title="", data=self._options)

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ZONES,
                        default=current.get(CONF_ZONES, DEFAULT_ZONES),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=MAX_ZONES, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                    vol.Required(
                        CONF_INPUTS,
                        default=current.get(CONF_INPUTS, DEFAULT_INPUTS),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=MAX_INPUTS, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                    vol.Required(
                        CONF_GPO_COUNT,
                        default=current.get(CONF_GPO_COUNT, DEFAULT_GPO_COUNT),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=MAX_GPO_COUNT, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                    vol.Required(
                        CONF_POLL_INTERVAL,
                        default=current.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=300, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="seconds"
                        )
                    ),
                }
            ),
        )

    async def async_step_input_names(self, user_input: dict[str, Any] | None = None):
        """Step 2: Name each input."""
        if user_input is not None:
            self._options.update(user_input)
            return self.async_create_entry(title="", data=self._options)

        input_count = self._options.get(CONF_INPUTS, DEFAULT_INPUTS)
        current = {**self.config_entry.data, **self.config_entry.options}
        schema: dict = {}
        for i in range(1, input_count + 1):
            key = f"Input {i}"
            schema[vol.Optional(key, default=current.get(key, key))] = str

        return self.async_show_form(
            step_id="input_names",
            data_schema=vol.Schema(schema),
        )
