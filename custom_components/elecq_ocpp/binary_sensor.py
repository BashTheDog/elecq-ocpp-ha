from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
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
    data = hass.data[DOMAIN][entry.entry_id]
    manager: ElecqOcppManager = data["manager"]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, "elecq_au101")},
        name="Elecq AU101 Charger",
        manufacturer="Elecq",
        model="AU101",
    )

    entities: list[BinarySensorEntity] = [
        ElecqPluggedInBinarySensor(manager, device_info),
        ElecqChargingBinarySensor(manager, device_info),
    ]
    async_add_entities(entities)


class _BaseElecqBinarySensor(BinarySensorEntity):
    def __init__(self, manager: ElecqOcppManager, device_info: DeviceInfo) -> None:
        self._manager = manager
        self._attr_device_info = device_info

    async def async_added_to_hass(self) -> None:
        async def _handle_update() -> None:
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_STATE_UPDATED, _handle_update)
        )


class ElecqPluggedInBinarySensor(_BaseElecqBinarySensor):
    _attr_has_entity_name = True
    _attr_name = "Plugged In"
    _attr_unique_id = "elecq_au101_plugged_in"
    _attr_device_class = BinarySensorDeviceClass.PLUG

    @property
    def is_on(self) -> bool:
        return self._manager.state.plugged_in


class ElecqChargingBinarySensor(_BaseElecqBinarySensor):
    _attr_has_entity_name = True
    _attr_name = "Charging"
    _attr_unique_id = "elecq_au101_charging"
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    @property
    def is_on(self) -> bool:
        return self._manager.state.charging
