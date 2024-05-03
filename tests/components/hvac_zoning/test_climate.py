"""Test climate."""

from homeassistant.components.hvac_zoning.climate import filter_to_valid_zones


def test_filter_to_valid_zones() -> None:
    """Test filter to valid zones."""
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
    }

    valid_zones = filter_to_valid_zones(user_input)

    assert valid_zones == [
        "basement",
        "guest_bedroom",
        "main_floor",
        "master_bedroom",
        "office",
        "upstairs_bathroom",
    ]


def test_filter_to_valid_zones_missing_temperature() -> None:
    """Test filter to valid zones missing temperature."""
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
        },
        "climate": {"main_floor": "climate.living_room_thermostat"},
    }

    valid_zones = filter_to_valid_zones(user_input)

    assert valid_zones == [
        "basement",
        "guest_bedroom",
        "main_floor",
        "master_bedroom",
        "office",
    ]


def test_filter_to_valid_zones_missing_damper() -> None:
    """Test filter to valid zones missing damper."""
    user_input = {
        "damper": {
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
    }

    valid_zones = filter_to_valid_zones(user_input)

    assert valid_zones == [
        "basement",
        "guest_bedroom",
        "master_bedroom",
        "office",
        "upstairs_bathroom",
    ]
