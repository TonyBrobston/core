"""Utils."""


def filter_to_valid_areas(user_input):
    """Filter to valid areas."""
    return {
        area: devices
        for area, devices in user_input.items()
        if "temperature" in devices and "covers" in devices
    }

def get_all_thermostat_entity_ids(user_input):
    """Get thermostat enitty ids."""
    return [area["climate"] for area in user_input.values() if "climate" in area]