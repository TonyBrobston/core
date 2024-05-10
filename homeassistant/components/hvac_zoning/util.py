"""File for utilities."""
from homeassistant.components.climate import HVACMode
from homeassistant.const import SERVICE_CLOSE_COVER, SERVICE_OPEN_COVER

from .const import SUPPORTED_HVAC_MODES


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
    if (
        hvac_mode not in SUPPORTED_HVAC_MODES
        or target_temperature is None
        or actual_temperature is None
    ):
        return SERVICE_OPEN_COVER

    match hvac_mode:
        case HVACMode.HEAT:
            if actual_temperature >= target_temperature:
                return SERVICE_CLOSE_COVER
        case HVACMode.COOL:
            if actual_temperature <= target_temperature:
                return SERVICE_CLOSE_COVER

    return SERVICE_OPEN_COVER


def determine_thermostat_target_temperature(
    target_temperature: int,
    actual_temperature: int,
    hvac_mode: str,
    cover_services: list[str],
) -> int:
    """Determine the new thermostat target temperature based on the current state."""
    match hvac_mode:
        case HVACMode.HEAT:
            if SERVICE_OPEN_COVER in cover_services:
                if actual_temperature <= target_temperature:
                    return actual_temperature + 1
            elif SERVICE_CLOSE_COVER in cover_services:
                return actual_temperature - 1
        case HVACMode.COOL:
            if SERVICE_OPEN_COVER in cover_services:
                if actual_temperature >= target_temperature:
                    return actual_temperature - 1
            elif SERVICE_CLOSE_COVER in cover_services:
                return actual_temperature + 1

    return target_temperature


def determine_cover_services(rooms, hvac_mode):
    """Determine cover services."""
    if hvac_mode not in SUPPORTED_HVAC_MODES:
        return []
    return [
        determine_cover_service(
            room["target_temperature"], room["actual_temperature"], hvac_mode
        )
        for room in rooms.values()
    ]
