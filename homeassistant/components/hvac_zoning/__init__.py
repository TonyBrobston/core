"""The HVAC Zoning integration."""

from __future__ import annotations

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

    # def handle_event(event):
    #     event_dict = event.as_dict()
    #     user_input = config_entry.as_dict()["data"]
    #     print(f"user_input: {user_input}")
    #     event_type = event_dict["event_type"]
    #     entity_id = event_dict["data"]["entity_id"]
    #     thermostat_entity_ids = [
    #         "climate." + zone_name + "_thermostat"
    #         for zone_name in filter_to_valid_areas(user_input)
    #     ]
    #     damper_and_temperature_entity_ids = get_all_entities(
    #         reformat_and_filter_to_valid_areas(user_input)
    #     )
    #     thermostat_entity = get_thermostat_entity(user_input)
    #     entity_ids = (
    #         thermostat_entity_ids
    #         + damper_and_temperature_entity_ids
    #         + thermostat_entity
    #     )
    #     # TO DO: Include main climate
    #     if event_type == "state_changed" and entity_id in entity_ids:
    #         print(f"event: {event_dict}")

    #     # if (
    #     #     event_dict["event_type"] == "call_service"
    #     #     and event_dict["data"]["service_data"]["temperature"] == 71
    #     # ):
    #     #     hass.services.call(
    #     #         "climate",
    #     #         "set_temperature",
    #     #         service_data={
    #     #             "entity_id": "climate.basement_thermostat",
    #     #             "temperature": 65,
    #     #         },
    #     #     )

    # hass.bus.async_listen("state_changed", handle_event)
    # hass.bus.async_listen("call_service", handle_event)
    return True
