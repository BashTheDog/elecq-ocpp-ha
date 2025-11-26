from __future__ import annotations

from typing import Any

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
    """Config flow for Elecq OCPP 2.0.1."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial config step."""
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Elecq AU101 OCPP",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_ID_TOKEN, default=DEFAULT_ID_TOKEN): str,
                vol.Required(CONF_EVSE_ID, default=DEFAULT_EVSE_ID): int,
                vol.Required(CONF_CONNECTOR_ID, default=DEFAULT_CONNECTOR_ID): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
