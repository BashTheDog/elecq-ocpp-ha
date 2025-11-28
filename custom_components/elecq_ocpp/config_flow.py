from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_PORT,
    CONF_ID_TOKEN,
    CONF_EVSE_ID,
    CONF_CONNECTOR_ID,
    DEFAULT_PORT,
    DEFAULT_ID_TOKEN,
    DEFAULT_EVSE_ID,
    DEFAULT_CONNECTOR_ID,
)


class ElecqOcppConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Elecq OCPP."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title="Elecq AU101 Charger",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_ID_TOKEN, default=DEFAULT_ID_TOKEN): str,
                vol.Required(CONF_EVSE_ID, default=DEFAULT_EVSE_ID): int,
                vol.Required(CONF_CONNECTOR_ID, default=DEFAULT_CONNECTOR_ID): int,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)
