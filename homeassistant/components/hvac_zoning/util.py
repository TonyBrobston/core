"""File for utilities."""
from homeassistant.components.climate import HVACMode
from homeassistant.const import SERVICE_CLOSE_COVER, SERVICE_OPEN_COVER


def filter_to_valid_areas(user_input):
    """Filter to valid areas."""
    return sorted(
        {
            area
            for areas in user_input.values()
            for area in areas
            if area in user_input["temperature"] and area in user_input["damper"]
        }
    )


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


def get_all_entities(areas):
    """Get all entities."""
    return sorted(
        [
            entity
            for area in areas.values()
            for key, value in area.items()
            for entity in (value if isinstance(value, list) else [value])
            if isinstance(entity, str)
        ]
    )


def get_thermostat_entities(user_input):
    """Get thermostat."""
    return list(user_input["climate"].values())


def determine_cover_service(
    target_temperature: int, actual_temperature: int, hvac_mode: HVACMode
) -> str:
    """Determine cover service."""
    if hvac_mode is None or target_temperature is None or actual_temperature is None:
        return SERVICE_OPEN_COVER

    if hvac_mode == HVACMode.HEAT:
        if actual_temperature >= target_temperature:
            return SERVICE_CLOSE_COVER
    elif hvac_mode == HVACMode.COOL:
        if actual_temperature <= target_temperature:
            return SERVICE_CLOSE_COVER

    return SERVICE_OPEN_COVER
