"""Climate stub."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .util import filter_to_valid_zones


class Thermostat(ClimateEntity):
    """Thermostat."""

    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_mode = None
    _attr_hvac_modes = []

    def __init__(self, name) -> None:
        """Thermostat init."""
        self._attr_unique_id = name
        self._attr_name = name
        self._attr_target_temperature = 70.0

    def set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        # print(f"temperature: {temperature}")
        self._attr_target_temperature = temperature


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Async setup entry."""

    user_input = config_entry.as_dict()["data"]

    async_add_entities(
        [
            Thermostat(zone_name + "_thermostat")
            for zone_name in filter_to_valid_zones(user_input)
        ]
    )
