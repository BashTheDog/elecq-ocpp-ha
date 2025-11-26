from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_PORT,
    CONF_ID_TOKEN,
    CONF_EVSE_ID,
    CONF_CONNECTOR_ID,
)
from .ocpp_server import ElecqOcppManager

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """YAML setup (unused)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Elecq OCPP from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    port = entry.data[CONF_PORT]
    id_token = entry.data[CONF_ID_TOKEN]
    evse_id = entry.data[CONF_EVSE_ID]
    connector_id = entry.data[CONF_CONNECTOR_ID]

    manager = ElecqOcppManager(
        hass=hass,
        port=port,
        id_token=id_token,
        evse_id=evse_id,
        connector_id=connector_id,
    )

    await manager.async_start_server()

    hass.data[DOMAIN][entry.entry_id] = {
        "manager": manager,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("Elecq OCPP integration initialized on port %s", port)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    data = hass.data[DOMAIN].pop(entry.entry_id, None)
    if data:
        manager: ElecqOcppManager = data["manager"]
        await manager.async_stop_server()

    return unload_ok
