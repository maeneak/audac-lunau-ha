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
    """Handle options flow with per-entity name configuration."""

    def __init__(self) -> None:
        """Initialise mutable state for the multi-step flow."""
        self._options: dict[str, Any] = {}

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Step 1: Configure counts and poll interval."""
        if user_input is not None:
            self._options = dict(user_input)
            return await self.async_step_zone_names()

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ZONES,
                        default=current.get(CONF_ZONES, DEFAULT_ZONES),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=64)),
                    vol.Optional(
                        CONF_INPUTS,
                        default=current.get(CONF_INPUTS, DEFAULT_INPUTS),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=64)),
                    vol.Optional(
                        CONF_GPO_COUNT,
                        default=current.get(CONF_GPO_COUNT, DEFAULT_GPO_COUNT),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=64)),
                    vol.Optional(
                        CONF_POLL_INTERVAL,
                        default=current.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=300)),
                }
            ),
        )

    async def async_step_zone_names(self, user_input: dict[str, Any] | None = None):
        """Step 2: Name each zone."""
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_input_names()

        zone_count = self._options.get(CONF_ZONES, DEFAULT_ZONES)
        current = {**self.config_entry.data, **self.config_entry.options}
        schema: dict = {}
        for i in range(1, zone_count + 1):
            key = f"Zone {i}"
            schema[vol.Optional(key, default=current.get(key, key))] = str

        return self.async_show_form(
            step_id="zone_names",
            data_schema=vol.Schema(schema),
        )

    async def async_step_input_names(self, user_input: dict[str, Any] | None = None):
        """Step 3: Name each input."""
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_gpo_names()

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

    async def async_step_gpo_names(self, user_input: dict[str, Any] | None = None):
        """Step 4: Name each GPIO output."""
        if user_input is not None:
            self._options.update(user_input)
            # Strip orphaned name keys from previous higher counts
            self._prune_stale_name_keys()
            return self.async_create_entry(title="", data=self._options)

        gpo_count = self._options.get(CONF_GPO_COUNT, DEFAULT_GPO_COUNT)
        current = {**self.config_entry.data, **self.config_entry.options}
        schema: dict = {}
        for i in range(1, gpo_count + 1):
            key = f"GPIO {i}"
            schema[vol.Optional(key, default=current.get(key, key))] = str

        return self.async_show_form(
            step_id="gpo_names",
            data_schema=vol.Schema(schema),
        )

    def _prune_stale_name_keys(self) -> None:
        """Remove name keys that exceed the current counts."""
        import re

        limits = {"Zone": self._options.get(CONF_ZONES, DEFAULT_ZONES),
                  "Input": self._options.get(CONF_INPUTS, DEFAULT_INPUTS),
                  "GPIO": self._options.get(CONF_GPO_COUNT, DEFAULT_GPO_COUNT)}
        pattern = re.compile(r"^(Zone|Input|GPIO) (\d+)$")
        stale = [
            k for k in self._options
            if (m := pattern.match(k)) and int(m.group(2)) > limits.get(m.group(1), 0)
        ]
        for k in stale:
            del self._options[k]
