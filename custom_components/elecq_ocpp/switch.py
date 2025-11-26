from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SIGNAL_STATE_UPDATED
from .ocpp_server import ElecqOcppManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Elecq OCPP switch from a config entry."""
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

    async def async_added_to_hass(self) -> None:
        async def _handle_update() -> None:
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_STATE_UPDATED, _handle_update)
        )

    @property
    def is_on(self) -> bool:
        # Driven entirely by manager.state.charging
        return self._manager.state.charging

    @property
    def available(self) -> bool:
        # Only available when:
        #  - the charger is connected (OCPP session up), AND
        #  - the EV is plugged in.
        st = self._manager.state
        return self._manager.is_available and st.plugged_in

    async def async_turn_on(self, **kwargs) -> None:
        """Start charging – but only if EV is plugged in."""
        st = self._manager.state

        # Extra safety: if someone calls service while unavailable
        if not st.plugged_in:
            raise HomeAssistantError(
                "Please plug in the EV before starting charging."
            )

        ok = await self._manager.async_request_start()
        if not ok:
            # Keep UI in sync and notify via error toast
            st.charging = False
            self.async_write_ha_state()
            raise HomeAssistantError(
                "Charger did not accept remote start request."
            )

        # OCPP events will keep state updated; just redraw
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Stop charging."""
        st = self._manager.state

        ok = await self._manager.async_request_stop()
        if not ok:
            # Don't lie about state if stop failed
            self.async_write_ha_state()
            raise HomeAssistantError(
                "Charger did not accept remote stop request."
            )

        st.charging = False
        self.async_write_ha_state()
