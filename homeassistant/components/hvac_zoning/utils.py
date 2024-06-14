"""Utils."""


def filter_to_valid_areas(config_entry_data):
    """Filter to valid areas."""
    return {
        "areas": {
            area: devices
            for area, devices in config_entry_data.get("areas", {}).items()
            if "temperature" in devices and "covers" in devices
        }
    }


def get_all_thermostat_entity_ids(config_entry_data):
    """Get thermostat enitty ids."""
    return [
        area["climate"]
        for area in config_entry_data.get("areas", {}).values()
        if "climate" in area
    ]
