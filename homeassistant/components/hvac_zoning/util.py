"""File for utilities."""
from homeassistant.components.climate import HVACMode
from homeassistant.components.climate.const import SERVICE_SET_TEMPERATURE
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    SERVICE_CLOSE_COVER,
    SERVICE_OPEN_COVER,
    Platform,
)

from .const import ACTIVE, IDLE, SUPPORTED_HVAC_MODES


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
        match hvac_mode:
            case HVACMode.HEAT:
                if actual_temperature >= target_temperature:
                    return IDLE
            case HVACMode.COOL:
                if actual_temperature <= target_temperature:
                    return IDLE

    return ACTIVE


def determine_cover_service_to_call(
    target_temperature: int, actual_temperature: int, hvac_mode: HVACMode
) -> str:
    """Determine cover service."""
    action_to_cover_service = {
        ACTIVE: SERVICE_OPEN_COVER,
        IDLE: SERVICE_CLOSE_COVER,
    }
    action = determine_action(target_temperature, actual_temperature, hvac_mode)

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


def adjust_house(hass, config_entry):
    """Adjust house."""
    user_input = config_entry.as_dict()["data"]
    central_thermostat_entity_id = get_all_thermostat_entity_ids(user_input)[0]
    central_thermostat = hass.states.get(central_thermostat_entity_id)
    central_thermostat_actual_temperature = central_thermostat.attributes[
        "current_temperature"
    ]
    central_hvac_mode = central_thermostat.state
    print(f"central_hvac_mode: {central_hvac_mode}")
    areas = filter_to_valid_areas(user_input)
    for area, devices in areas.items():
        area_target_temperature = hass.states.get(
            "climate." + area + "_thermostat"
        ).state
        area_actual_temperature = hass.states.get(devices["temperature"]).state
        service_to_call = determine_cover_service_to_call(
            area_target_temperature, area_actual_temperature, central_hvac_mode
        )
        for cover in devices["covers"]:
            hass.services.call(
                Platform.COVER, service_to_call, service_data={ATTR_ENTITY_ID: cover}
            )
    actions = [
        determine_action(
            hass.states.get("climate." + area + "_thermostat").state,
            hass.states.get(devices["temperature"]).state,
            central_hvac_mode,
        )
        for area, devices in areas.items()
    ]
    action = IDLE if all(action == IDLE for action in actions) else ACTIVE
    hass.services.call(
        Platform.CLIMATE,
        SERVICE_SET_TEMPERATURE,
        service_data={
            ATTR_ENTITY_ID: central_thermostat_entity_id,
            ATTR_TEMPERATURE: determine_change_in_temperature(
                central_thermostat_actual_temperature, central_hvac_mode, action
            ),
        },
    )
