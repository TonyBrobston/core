"""Climate stub."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, EVENT_STATE_CHANGED, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SUPPORTED_HVAC_MODES
from .utils import filter_to_valid_areas, get_all_thermostat_entity_ids


class Thermostat(ClimateEntity):
    """Thermostat."""

    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_mode = None
    _attr_hvac_modes = SUPPORTED_HVAC_MODES

    def __init__(
        self, hass, name, temperature_sensor_entity_id, thermostat_entity_id
    ) -> None:
        """Thermostat init."""
        self._attr_unique_id = name
        self._attr_name = name
        self._attr_target_temperature = 73.0

        def handle_event(event):
            event_dict = event.as_dict()
            entity_id = event_dict["data"]["entity_id"]
            if entity_id == temperature_sensor_entity_id:
                current_temperature = float(event_dict["data"]["new_state"].state)
                self._attr_current_temperature = current_temperature
            if entity_id == thermostat_entity_id:
                hvac_mode = event_dict["data"]["new_state"].state
                self._attr_hvac_mode = hvac_mode

        hass.bus.async_listen(EVENT_STATE_CHANGED, handle_event)

    def set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        self._attr_target_temperature = temperature


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Async setup entry."""

    user_input = config_entry.as_dict()["data"]
    areas = filter_to_valid_areas(user_input)
    thermostat_entity_ids = get_all_thermostat_entity_ids(user_input)
    async_add_entities(
        [
            Thermostat(
                hass,
                key + "_thermostat",
                value["temperature"],
                thermostat_entity_ids[0],
            )
            for key, value in areas.items()
        ]
    )
