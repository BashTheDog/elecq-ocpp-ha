from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_STATE_UPDATED
from .ocpp_server import ElecqOcppManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Elecq OCPP sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    manager: ElecqOcppManager = data["manager"]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, "elecq_au101")},
        name="Elecq AU101 Charger",
        manufacturer="Elecq",
        model="AU101",
    )

    async_add_entities(
        [
            ElecqPowerSensor(manager, device_info),
            ElecqSmoothedPowerSensor(manager, device_info),
            ElecqEnergySensor(manager, device_info),
            ElecqSessionEnergySensor(manager, device_info),
            ElecqSessionDurationSensor(manager, device_info),
            ElecqChargingStateSensor(manager, device_info),
            ElecqChargerStatusSensor(manager, device_info),
            ElecqDiagnosticsSensor(manager, device_info),
        ]
    )


class ElecqBaseSensor(SensorEntity):
    """Base entity for Elecq sensors."""

    _attr_has_entity_name = True

    def __init__(self, manager: ElecqOcppManager, device_info: DeviceInfo) -> None:
        self._manager = manager
        self._attr_device_info = device_info

    async def async_added_to_hass(self) -> None:
        async def _handle_update() -> None:
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_STATE_UPDATED, _handle_update)
        )


class ElecqPowerSensor(ElecqBaseSensor):
    _attr_name = "Power"
    _attr_unique_id = "elecq_au101_power"
    _attr_native_unit_of_measurement = "kW"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        return self._manager.state.power_kw


class ElecqSmoothedPowerSensor(ElecqBaseSensor):
    _attr_name = "Power (Smoothed)"
    _attr_unique_id = "elecq_au101_power_smoothed"
    _attr_native_unit_of_measurement = "kW"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        return self._manager.state.power_kw_smoothed


class ElecqEnergySensor(ElecqBaseSensor):
    _attr_name = "Total Energy"
    _attr_unique_id = "elecq_au101_energy"
    _attr_native_unit_of_measurement = "kWh"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> Any:
        return self._manager.state.energy_kwh


class ElecqSessionEnergySensor(ElecqBaseSensor):
    _attr_name = "Session Energy"
    _attr_unique_id = "elecq_au101_session_energy"
    _attr_native_unit_of_measurement = "kWh"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> Any:
        return self._manager.state.session_energy_kwh


class ElecqSessionDurationSensor(ElecqBaseSensor):
    _attr_name = "Session Duration"
    _attr_unique_id = "elecq_au101_session_duration"
    _attr_native_unit_of_measurement = "s"
    _attr_device_class = SensorDeviceClass.DURATION

    @property
    def native_value(self) -> Any:
        st = self._manager.state
        if st.session_start is None:
            return None
        now = datetime.now(timezone.utc)
        return int((now - st.session_start).total_seconds())


class ElecqChargingStateSensor(ElecqBaseSensor):
    _attr_name = "Charging State"
    _attr_unique_id = "elecq_au101_charging_state"

    @property
    def native_value(self) -> Any:
        return self._manager.state.last_charging_state


class ElecqChargerStatusSensor(ElecqBaseSensor):
    """Raw OCPP connector status (Available, Occupied, Charging, etc.)."""

    _attr_name = "Charger Status"
    _attr_unique_id = "elecq_au101_charger_status"
    _attr_icon = "mdi:ev-station"

    @property
    def native_value(self) -> Any:
        return self._manager.state.last_status


class ElecqDiagnosticsSensor(ElecqBaseSensor):
    _attr_name = "Diagnostics"
    _attr_unique_id = "elecq_au101_diagnostics"
    _attr_icon = "mdi:clipboard-text-outline"

    @property
    def native_value(self) -> Any:
        return self._manager.state.session_event_type

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        st = self._manager.state
        return {
            "charging_state": st.last_charging_state,
            "trigger_reason": st.session_trigger_reason,
            "transaction_id": st.transaction_id,
            "plugged_in": st.plugged_in,
            "charging": st.charging,
            "last_status": st.last_status,
            "transaction_info": st.last_transaction_info,
            "meter_value": st.last_meter_value,
        }
