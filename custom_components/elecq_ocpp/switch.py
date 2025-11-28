from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SIGNAL_STATE_UPDATED
from .ocpp_server import ElecqOcppManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    manager: ElecqOcppManager = data["manager"]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, "elecq_au101")},
        name="Elecq AU101 Charger",
        manufacturer="Elecq",
        model="AU101",
    )

    async_add_entities([ElecqChargingSwitch(manager, device_info)])


class ElecqChargingSwitch(SwitchEntity):
    """Switch that triggers RequestStartTransaction / RequestStopTransaction."""

    _attr_has_entity_name = True
    _attr_name = "Remote Charging"
    _attr_unique_id = "elecq_au101_remote_charging"

    def __init__(self, manager: ElecqOcppManager, device_info: DeviceInfo) -> None:
        self._manager = manager
        self._attr_device_info = device_info
        # Busy flag: while True, UI will show the entity as "unavailable" (greyed out)
        self._busy: bool = False

    async def async_added_to_hass(self) -> None:
        async def _handle_update() -> None:
            # Whenever the manager state changes (from OCPP events),
            # we re-sync the UI. ON/OFF comes only from charger state.
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_STATE_UPDATED, _handle_update)
        )

    # ---- Core behavior ----

    @property
    def is_on(self) -> bool:
        """ON/OFF is derived ONLY from charger state."""
        return self._manager.state.charging

    @property
    def available(self) -> bool:
        """
        Entity is temporarily greyed out (unavailable) while a command is in flight.

        Otherwise, it's available whenever the charger is connected.
        """
        return self._manager.is_available and not self._busy

    async def async_turn_on(self, **kwargs) -> None:
        """
        User toggles switch ON:

        - If EV is unplugged  -> show error "Please plug in..." and do nothing.
        - Else:
            * Grey out switch (busy=True)
            * Send RequestStartTransaction
            * Ungrey after response
            * If charger accepts     -> state will flip to ON later via OCPP events.
            * If charger rejects     -> stay OFF; we only log a warning.
        """
        st = self._manager.state

        if not st.plugged_in:
            # Don't even try to talk to charger if EV is not connected.
            raise HomeAssistantError(
                "Please plug in the EV before starting charging."
            )

        # Mark as busy/greyed out while request is in flight
        self._busy = True
        self.async_write_ha_state()

        try:
            ok = await self._manager.async_request_start()
        finally:
            # Always clear busy flag once we got a response / finished attempt
            self._busy = False
            # State (is_on) is still driven purely by manager.state.charging
            self.async_write_ha_state()

        if not ok:
            # Charger refused start (e.g. already fully charged or some internal rule).
            # We do NOT raise a HomeAssistantError here, so HA won't leave the switch
            # visually ON. Instead we just log it; the switch will show OFF because
            # charging stays False.
            _LOGGER.warning("Charger did not accept remote start request.")

    async def async_turn_off(self, **kwargs) -> None:
        """
        User toggles switch OFF:

        - If no active transaction or CP -> we still call async_request_stop(); it
          returns False and we just log a warning.
        - Grey out while request in flight, then ungrey.
        - ON/OFF still only changes when charger sends TransactionEvent(Ended) etc.
        """
        # Temporarily grey out while we send RequestStopTransaction
        self._busy = True
        self.async_write_ha_state()

        try:
            ok = await self._manager.async_request_stop()
        finally:
            self._busy = False
            self.async_write_ha_state()

        if not ok:
            _LOGGER.warning("Charger did not accept remote stop request.")
