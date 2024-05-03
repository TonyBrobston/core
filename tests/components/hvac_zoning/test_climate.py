"""Test climate."""

from homeassistant.components.hvac_zoning.climate import map_user_input_format


def test_map_user_input_format() -> None:
    """Test remap user_input to merge areas."""
    user_input = {
        "damper": {
            "main_floor": [
                "cover.living_room_northeast_vent",
                "cover.living_room_southeast_vent",
                "cover.kitchen_south_vent",
                "cover.kitchen_northwest_vent",
            ],
            "basement": [
                "cover.basement_west_vent",
                "cover.basement_northeast_vent",
                "cover.basement_southeast_vent",
            ],
            "master_bedroom": ["cover.master_bedroom_vent"],
            "guest_bedroom": ["cover.guest_bedroom_vent"],
            "office": ["cover.office_vent"],
            "upstairs_bathroom": ["cover.upstairs_bathroom_vent"],
        },
        "temperature": {
            "main_floor": "sensor.main_floor_temperature",
            "basement": "sensor.basement_temperature",
            "master_bedroom": "sensor.master_bedroom_temperature",
            "guest_bedroom": "sensor.guest_bedroom_temperature",
            "office": "sensor.office_temperature",
            "upstairs_bathroom": "sensor.upstairs_bathroom_temperature",
        },
        "climate": {"main_floor": "climate.living_room_thermostat"},
        "should_build_virtual_thermostats": {"question": "Yes"},
    }

    mapped_user_input = map_user_input_format(user_input)

    assert mapped_user_input == [
        "basement",
        "guest_bedroom",
        "main_floor",
        "master_bedroom",
        "office",
        "upstairs_bathroom",
    ]
