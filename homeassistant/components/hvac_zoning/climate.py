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
        self._attr_hvac_modes = [HVACMode.HEAT]
        self._attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
        self._attr_current_temperature = 69
        self._attr_target_temperature = 75


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Async setup entry."""

    user_input = config_entry.as_dict()["data"]

    if (
        user_input != {}
        and user_input["should_build_virtual_thermostats"]["question"] == "Yes"
    ):
        async_add_entities(
            [
                Thermostat(key.title() + "_thermostat")
                for key in list(user_input["damper"].keys())
            ]
        )
