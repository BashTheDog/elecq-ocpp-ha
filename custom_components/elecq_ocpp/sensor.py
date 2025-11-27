from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
)
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from .const import DOMAIN, SIGNAL_STATE_UPDATED
from .ocpp_server import ElecqOcppManager


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

    entities: list[SensorEntity] = [
        ElecqPowerSensor(manager, device_info),
        ElecqSmoothedPowerSensor(manager, device_info),
        ElecqEnergySensor(manager, device_info),
        ElecqSessionEnergySensor(manager, device_info),
        ElecqStatusSensor(manager, device_info),
    ]
    async_add_entities(entities)


class _BaseElecqSensor(SensorEntity):
    def __init__(self, manager: ElecqOcppManager, device_info: DeviceInfo) -> None:
        self._manager = manager
        self._attr_device_info = device_info

    async def async_added_to_hass(self) -> None:
        async def _handle_update() -> None:
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_STATE_UPDATED, _handle_update)
        )


class ElecqPowerSensor(_BaseElecqSensor):
    _attr_has_entity_name = True
    _attr_name = "Power"
    _attr_unique_id = "elecq_au101_power"
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        return self._manager.state.power_kw


class ElecqSmoothedPowerSensor(_BaseElecqSensor):
    _attr_has_entity_name = True
    _attr_name = "Power (Smoothed)"
    _attr_unique_id = "elecq_au101_power_smoothed"
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        return self._manager.state.power_kw_smoothed


class ElecqEnergySensor(_BaseElecqSensor):
    _attr_has_entity_name = True
    _attr_name = "Total Energy"
    _attr_unique_id = "elecq_au101_energy"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        return self._manager.state.energy_kwh


class ElecqSessionEnergySensor(_BaseElecqSensor):
    _attr_has_entity_name = True
    _attr_name = "Session Energy"
    _attr_unique_id = "elecq_au101_session_energy"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self):
        return self._manager.state.session_energy_kwh


class ElecqStatusSensor(_BaseElecqSensor):
    _attr_has_entity_name = True
    _attr_name = "Charger Status"
    _attr_unique_id = "elecq_au101_status"

    @property
    def native_value(self):
        return self._manager.state.last_status or "Unknown"
