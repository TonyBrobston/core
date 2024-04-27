"""Temperature sensor stub."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


class TemperatureSensor(SensorEntity):
    """Derp is a Sensor."""

    def __init__(self, name: str, temperature: int) -> None:
        """Derp is a Sensor init."""
        self._attr_unique_id = name
        self._attr_name = name
        self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_value = temperature


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Async setup entry."""
    async_add_entities(
        [
            TemperatureSensor("Main Floor Temperature", 71),
            TemperatureSensor("Basement Temperature", 69),
            TemperatureSensor("Office Temperature", 76),
            TemperatureSensor("Guest Bedroom Temperature", 72),
            TemperatureSensor("Master Bedroom Temperature", 75),
            TemperatureSensor("Upstairs Bathroom Temperature", 74),
        ]
    )
