"""Climate stub."""

from __future__ import annotations

from homeassistant.components.climate import ClimateEntity, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


class Thermostat(ClimateEntity):
    """Derp is a Thermostat."""

    def __init__(self, name: str) -> None:
        """Derp is a Thermostat init."""
        self._attr_unique_id = name
        self._attr_name = name
        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.COOL, HVACMode.OFF]
        self._attr_temperature_unit = UnitOfTemperature.FAHRENHEIT


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Async setup entry."""
    async_add_entities([Thermostat("Living Room Thermostat")], True)
