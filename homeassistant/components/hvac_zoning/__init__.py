"""The HVAC Zoning integration."""

from __future__ import annotations

from homeassistant.components.hvac_zoning.util import (
    adjust_house,
    filter_to_valid_areas,
    get_all_cover_entity_ids,
    get_all_temperature_entity_ids,
    get_all_thermostat_entity_ids,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# TO DO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.CLIMATE]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up HVAC Zoning from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    # TO DO 1. Create API instance
    # TO DO 2. Validate the API connection (and authentication)
    # TO DO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    def handle_event(event):
        event_dict = event.as_dict()
        event_type = event_dict["event_type"]
        entity_id = event_dict["data"]["entity_id"]
        user_input = config_entry.as_dict()["data"]
        areas = filter_to_valid_areas(user_input)
        cover_entity_ids = get_all_cover_entity_ids(areas)
        temperature_entity_ids = get_all_temperature_entity_ids(areas)
        thermostat_entity_ids = get_all_thermostat_entity_ids(user_input)
        virtual_thermostat_entity_ids = [
            "climate." + zone_name + "_thermostat"
            for zone_name in filter_to_valid_areas(user_input)
        ]
        entity_ids = (
            cover_entity_ids
            + temperature_entity_ids
            + thermostat_entity_ids
            + virtual_thermostat_entity_ids
        )
        if event_type == "state_changed" and entity_id in entity_ids:
            adjust_house(hass, config_entry)

    hass.bus.async_listen("state_changed", handle_event)
    return True
