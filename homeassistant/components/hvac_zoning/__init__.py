"""The HVAC Zoning integration."""

from __future__ import annotations

from homeassistant.components.climate import SERVICE_SET_TEMPERATURE, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    SERVICE_CLOSE_COVER,
    SERVICE_OPEN_COVER,
    Platform,
)
from homeassistant.core import HomeAssistant

from .const import ACTIVE, DOMAIN, IDLE, SUPPORTED_HVAC_MODES

# TO DO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.CLIMATE]


def filter_to_valid_areas(user_input):
    """Filter to valid areas."""
    return {
        area: devices
        for area, devices in user_input.items()
        if "temperature" in devices and "covers" in devices
    }


def reformat_and_filter_to_valid_areas(user_input):
    """Reformat and filter to valid areas."""
    valid_areas = filter_to_valid_areas(user_input)
    return {
        area: {
            "damper": user_input["damper"][area],
            "temperature": user_input["temperature"][area],
        }
        for area in valid_areas
    }


def get_all_cover_entity_ids(areas):
    """Get all cover entity ids."""
    return [cover for area in areas.values() for cover in area.get("covers", [])]


def get_all_temperature_entity_ids(areas):
    """Get all temperature entity ids."""
    return [area["temperature"] for area in areas.values() if "temperature" in area]


def get_all_thermostat_entity_ids(user_input):
    """Get thermostat enitty ids."""
    return [area["climate"] for area in user_input.values() if "climate" in area]


def determine_action(
    target_temperature: int, actual_temperature: int, hvac_mode: HVACMode
):
    """Determine action."""
    if (
        hvac_mode in SUPPORTED_HVAC_MODES
        and target_temperature is not None
        and actual_temperature is not None
    ):
        modified_actual_temperature = int(float(actual_temperature))
        modified_target_temperature = int(float(target_temperature))
        match hvac_mode:
            case HVACMode.HEAT:
                if modified_actual_temperature >= modified_target_temperature:
                    return IDLE
            case HVACMode.COOL:
                if modified_actual_temperature <= modified_target_temperature:
                    return IDLE

    return ACTIVE


def determine_cover_service_to_call(
    target_temperature: int,
    actual_temperature: int,
    hvac_mode: HVACMode,
    thermostat_action: str,
) -> str:
    """Determine cover service."""
    action_to_cover_service = {
        ACTIVE: SERVICE_OPEN_COVER,
        IDLE: SERVICE_CLOSE_COVER,
    }
    action = (
        ACTIVE
        if thermostat_action == IDLE
        else determine_action(target_temperature, actual_temperature, hvac_mode)
    )

    return action_to_cover_service.get(action)


def determine_change_in_temperature(target_temperature, hvac_mode, action):
    """Determine change in temperature."""
    if action == ACTIVE and hvac_mode in SUPPORTED_HVAC_MODES:
        match hvac_mode:
            case HVACMode.HEAT:
                return target_temperature + 2
            case HVACMode.COOL:
                return target_temperature - 2
    return target_temperature


def adjust_house(hass: HomeAssistant, config_entry: ConfigEntry):
    """Adjust house."""
    user_input = config_entry.as_dict()["data"]
    central_thermostat_entity_id = get_all_thermostat_entity_ids(user_input)[0]
    central_thermostat = hass.states.get(central_thermostat_entity_id)
    central_thermostat_actual_temperature = central_thermostat.attributes[
        "current_temperature"
    ]
    central_hvac_mode = central_thermostat.state
    areas = filter_to_valid_areas(user_input)
    actions = [
        determine_action(
            hass.states.get("climate." + area + "_thermostat").attributes[
                "temperature"
            ],
            hass.states.get(devices["temperature"]).state,
            central_hvac_mode,
        )
        for area, devices in areas.items()
    ]
    thermostat_action = ACTIVE if ACTIVE in actions else IDLE
    for area, devices in areas.items():
        area_thermostat = hass.states.get("climate." + area + "_thermostat")
        area_target_temperature = area_thermostat.attributes["temperature"]
        temperature_sensor = hass.states.get(devices["temperature"])
        area_actual_temperature = temperature_sensor.state
        service_to_call = determine_cover_service_to_call(
            area_target_temperature,
            area_actual_temperature,
            central_hvac_mode,
            thermostat_action,
        )
        for cover in devices["covers"]:
            hass.services.call(
                Platform.COVER, service_to_call, service_data={ATTR_ENTITY_ID: cover}
            )
    hass.services.call(
        Platform.CLIMATE,
        SERVICE_SET_TEMPERATURE,
        service_data={
            ATTR_ENTITY_ID: central_thermostat_entity_id,
            ATTR_TEMPERATURE: determine_change_in_temperature(
                central_thermostat_actual_temperature,
                central_hvac_mode,
                thermostat_action,
            ),
        },
    )


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
