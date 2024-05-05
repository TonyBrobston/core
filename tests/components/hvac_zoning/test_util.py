"""Test util."""


from homeassistant.components.hvac_zoning.util import (
    filter_to_valid_areas,
    get_all_entities,
    get_thermostat_entities,
    reformat_and_filter_to_valid_areas,
)


def test_reformat_and_filter_to_valid_areas() -> None:
    """Test reformat and filter to valid areas."""
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

    areas = reformat_and_filter_to_valid_areas(user_input)

    assert areas == {
        "basement": {
            "damper": [
                "cover.basement_west_vent",
                "cover.basement_northeast_vent",
                "cover.basement_southeast_vent",
            ],
            "temperature": "sensor.basement_temperature",
        },
        "guest_bedroom": {
            "damper": ["cover.guest_bedroom_vent"],
            "temperature": "sensor.guest_bedroom_temperature",
        },
        "main_floor": {
            "damper": [
                "cover.living_room_northeast_vent",
                "cover.living_room_southeast_vent",
                "cover.kitchen_south_vent",
                "cover.kitchen_northwest_vent",
            ],
            "temperature": "sensor.main_floor_temperature",
        },
        "master_bedroom": {
            "damper": ["cover.master_bedroom_vent"],
            "temperature": "sensor.master_bedroom_temperature",
        },
        "office": {
            "damper": ["cover.office_vent"],
            "temperature": "sensor.office_temperature",
        },
        "upstairs_bathroom": {
            "damper": ["cover.upstairs_bathroom_vent"],
            "temperature": "sensor.upstairs_bathroom_temperature",
        },
    }


def test_filter_to_valid_areas() -> None:
    """Test filter to valid areas."""
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

    areas = filter_to_valid_areas(user_input)

    assert areas == [
        "basement",
        "guest_bedroom",
        "main_floor",
        "master_bedroom",
        "office",
        "upstairs_bathroom",
    ]


def test_filter_to_valid_areas_missing_temperature() -> None:
    """Test filter to valid areas missing temperature."""
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

    areas = filter_to_valid_areas(user_input)

    assert areas == [
        "basement",
        "guest_bedroom",
        "main_floor",
        "master_bedroom",
        "office",
    ]


def test_filter_to_valid_areas_missing_damper() -> None:
    """Test filter to valid areas missing damper."""
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

    areas = filter_to_valid_areas(user_input)

    assert areas == [
        "basement",
        "guest_bedroom",
        "master_bedroom",
        "office",
        "upstairs_bathroom",
    ]


def test_get_all_entities() -> None:
    """Test get all entities."""
    areas = {
        "basement": {
            "damper": [
                "cover.basement_west_vent",
                "cover.basement_northeast_vent",
                "cover.basement_southeast_vent",
            ],
            "temperature": "sensor.basement_temperature",
        },
        "guest_bedroom": {
            "damper": ["cover.guest_bedroom_vent"],
            "temperature": "sensor.guest_bedroom_temperature",
        },
        "main_floor": {
            "damper": [
                "cover.living_room_northeast_vent",
                "cover.living_room_southeast_vent",
                "cover.kitchen_south_vent",
                "cover.kitchen_northwest_vent",
            ],
            "temperature": "sensor.main_floor_temperature",
        },
        "master_bedroom": {
            "damper": ["cover.master_bedroom_vent"],
            "temperature": "sensor.master_bedroom_temperature",
        },
        "office": {
            "damper": ["cover.office_vent"],
            "temperature": "sensor.office_temperature",
        },
        "upstairs_bathroom": {
            "damper": ["cover.upstairs_bathroom_vent"],
            "temperature": "sensor.upstairs_bathroom_temperature",
        },
    }

    entities = get_all_entities(areas)

    assert entities == [
        "cover.basement_northeast_vent",
        "cover.basement_southeast_vent",
        "cover.basement_west_vent",
        "cover.guest_bedroom_vent",
        "cover.kitchen_northwest_vent",
        "cover.kitchen_south_vent",
        "cover.living_room_northeast_vent",
        "cover.living_room_southeast_vent",
        "cover.master_bedroom_vent",
        "cover.office_vent",
        "cover.upstairs_bathroom_vent",
        "sensor.basement_temperature",
        "sensor.guest_bedroom_temperature",
        "sensor.main_floor_temperature",
        "sensor.master_bedroom_temperature",
        "sensor.office_temperature",
        "sensor.upstairs_bathroom_temperature",
    ]


def test_get_thermostat_entities() -> None:
    """Test get thermostat entities."""
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

    thermostat = get_thermostat_entities(user_input)

    assert thermostat == ["climate.living_room_thermostat"]
