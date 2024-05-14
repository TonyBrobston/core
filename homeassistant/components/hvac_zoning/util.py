"""File for utilities."""
from homeassistant.components.climate import HVACMode
from homeassistant.const import SERVICE_CLOSE_COVER, SERVICE_OPEN_COVER

from .const import SUPPORTED_HVAC_MODES


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


def get_thermostat_entity_ids(user_input):
    """Get thermostat enitty ids."""
    return [area["climate"] for area in user_input.values() if "climate" in area]


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


def determine_cover_services(rooms, hvac_mode):
    """Determine cover services."""
    return [
        determine_cover_service(
            room["target_temperature"], room["actual_temperature"], hvac_mode
        )
        for room in rooms.values()
    ]


# def adjust_covers(hass: HomeAssistant, config_entry: ConfigEntry):
#     """Adjust covers."""
#     # data = config_entry.as_dict()["data"]
#     # print(f"reformatted data: {reformat_and_filter_to_valid_areas(data)}")
#     state = hass.states.get("climate.living_room_thermostat")
#     if state:
#         return state.attributes.get("temperature")
def adjust_covers(hass, config_entry):
    """Adjust covers based on thermostat and temperature sensors."""
    user_input = config_entry.as_dict()["data"]
    # print(f"user_input: {user_input}")
    thermostat_entity_ids = get_thermostat_entity_ids(user_input)
    # print(f"thermostat_entity_ids: {thermostat_entity_ids}")
    thermostat_entity_id = thermostat_entity_ids[0]
    # print(f"thermostat_entity_id: {thermostat_entity_id}")
    areas = filter_to_valid_areas(user_input)
    # print(f"areas: {areas}")
    hvac_mode = hass.states.get(thermostat_entity_id).attributes["hvac_mode"]
    # print(f"hvac_mode: {hvac_mode}")
    for area, devices in areas.items():
        # print(f"area: {area}")
        # print(f"devices: {devices}")
        target_temperature = hass.states.get("climate." + area + "_thermostat").state
        # print(f"target_temperature: {target_temperature}")
        actual_temperature = hass.states.get(devices["temperature"]).state
        # print(f"actual_temperature: {actual_temperature}")
        service = determine_cover_service(
            target_temperature, actual_temperature, hvac_mode
        )
        for cover in devices["covers"]:
            hass.services.call("cover", service, service_data={"entity_id": cover})


def determine_thermostat_target_temperature(
    target_temperature: int,
    actual_temperature: int,
    hvac_mode: str,
    cover_services: list[str],
) -> int:
    """Determine the new thermostat target temperature based on the current state."""
    change_in_temperature = 2
    match hvac_mode:
        case HVACMode.HEAT:
            if SERVICE_OPEN_COVER in cover_services:
                if actual_temperature <= target_temperature:
                    heat_heating = actual_temperature + change_in_temperature
                    return heat_heating
            else:
                heat_idle = actual_temperature - change_in_temperature
                return heat_idle
        case HVACMode.COOL:
            if SERVICE_OPEN_COVER in cover_services:
                if actual_temperature >= target_temperature:
                    cool_cooling = actual_temperature - change_in_temperature
                    return cool_cooling
            else:
                cool_idle = actual_temperature + change_in_temperature
                return cool_idle

    return target_temperature
