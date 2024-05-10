"""Test util."""


from homeassistant.components.climate import HVACMode
from homeassistant.components.hvac_zoning.util import (
    determine_cover_service,
    determine_cover_services,
    determine_thermostat_target_temperature,
    filter_to_valid_areas,
    get_all_entities,
    get_thermostat_entities,
    reformat_and_filter_to_valid_areas,
)
from homeassistant.const import SERVICE_CLOSE_COVER, SERVICE_OPEN_COVER


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


def test_determine_cover_service_heat_open_greater_than() -> None:
    """Test determine cover service heat open greater than."""
    target_temperature = 71
    actual_temperature = 70
    hvac_mode = HVACMode.HEAT
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_OPEN_COVER


def test_determine_cover_service_heat_close_less_than() -> None:
    """Test determine cover service heat close less than."""
    target_temperature = 69
    actual_temperature = 70
    hvac_mode = HVACMode.HEAT
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_CLOSE_COVER


def test_determine_cover_service_heat_close_equal_to() -> None:
    """Test determine cover service heat close equal to."""
    target_temperature = 70
    actual_temperature = 70
    hvac_mode = HVACMode.HEAT
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_CLOSE_COVER


def test_determine_cover_service_cool_open_less_than() -> None:
    """Test determine cover service cool open less than."""
    target_temperature = 69
    actual_temperature = 70
    hvac_mode = HVACMode.COOL
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_OPEN_COVER


def test_determine_cover_service_cool_close_greater_than() -> None:
    """Test determine cover service cool close greater than."""
    target_temperature = 71
    actual_temperature = 70
    hvac_mode = HVACMode.COOL
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_CLOSE_COVER


def test_determine_cover_service_cool_close_equal_to() -> None:
    """Test determine cover service cool close equal to."""
    target_temperature = 70
    actual_temperature = 70
    hvac_mode = HVACMode.COOL
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_CLOSE_COVER


def test_determine_cover_service_none_open_none_hvac_mode() -> None:
    """Test determine cover service none open invalid hvac mode."""
    target_temperature = 71
    actual_temperature = 70
    hvac_mode = None
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_OPEN_COVER


def test_determine_cover_service_none_open_heat_cool_hvac_mode() -> None:
    """Test determine cover service none open invalid hvac mode."""
    target_temperature = 71
    actual_temperature = 70
    hvac_mode = HVACMode.HEAT_COOL
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_OPEN_COVER


def test_determine_cover_service_heat_open_invalid_target_temperature() -> None:
    """Test determine cover service heat open invalid target temperature."""
    target_temperature = None
    actual_temperature = 70
    hvac_mode = HVACMode.HEAT
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_OPEN_COVER


def test_determine_cover_service_heat_open_invalid_actual_temperature() -> None:
    """Test determine cover service heat open invalid actual temperature."""
    target_temperature = 70
    actual_temperature = None
    hvac_mode = HVACMode.HEAT
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_OPEN_COVER


def test_determine_cover_service_cool_open_invalid_target_temperature() -> None:
    """Test determine cover service cool open invalid target temperature."""
    target_temperature = None
    actual_temperature = 70
    hvac_mode = HVACMode.COOL
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_OPEN_COVER


def test_determine_cover_service_cool_open_invalid_actual_temperature() -> None:
    """Test determine cover service cool open invalid actual temperature."""
    target_temperature = 70
    actual_temperature = None
    hvac_mode = HVACMode.COOL
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == SERVICE_OPEN_COVER


def test_determine_thermostat_target_temperature_move_to_heating() -> None:
    """Determine thermostat target temperature move to heating."""
    target_temperature = 70
    actual_temperature = 70
    hvac_mode = HVACMode.HEAT
    cover_services = [SERVICE_OPEN_COVER]

    new_thermostat_target_temperature = determine_thermostat_target_temperature(
        target_temperature, actual_temperature, hvac_mode, cover_services
    )

    assert new_thermostat_target_temperature == 71


def test_determine_thermostat_target_temperature_continue_heating() -> None:
    """Determine thermostat target temperature continue heating."""
    target_temperature = 71
    actual_temperature = 70
    hvac_mode = HVACMode.HEAT
    cover_services = [SERVICE_OPEN_COVER]

    new_thermostat_target_temperature = determine_thermostat_target_temperature(
        target_temperature, actual_temperature, hvac_mode, cover_services
    )

    assert new_thermostat_target_temperature == 71


def test_determine_thermostat_target_temperature_stop_heating() -> None:
    """Determine thermostat target temperature stop heating."""
    target_temperature = 71
    actual_temperature = 70
    hvac_mode = HVACMode.HEAT
    cover_services = [SERVICE_CLOSE_COVER]

    new_thermostat_target_temperature = determine_thermostat_target_temperature(
        target_temperature, actual_temperature, hvac_mode, cover_services
    )

    assert new_thermostat_target_temperature == 69


def test_determine_thermostat_target_temperature_move_to_cooling() -> None:
    """Test determine thermostat target temperature move to cooling."""
    target_temperature = 70
    actual_temperature = 70
    hvac_mode = HVACMode.COOL
    cover_services = [SERVICE_OPEN_COVER]

    new_thermostat_target_temperature = determine_thermostat_target_temperature(
        target_temperature, actual_temperature, hvac_mode, cover_services
    )

    assert new_thermostat_target_temperature == 69


def test_determine_thermostat_target_temperature_continue_cooling() -> None:
    """Test determine thermostat target temperature continue cooling."""
    target_temperature = 69
    actual_temperature = 70
    hvac_mode = HVACMode.COOL
    cover_services = [SERVICE_OPEN_COVER]

    new_thermostat_target_temperature = determine_thermostat_target_temperature(
        target_temperature, actual_temperature, hvac_mode, cover_services
    )

    assert new_thermostat_target_temperature == 69


def test_determine_thermostat_target_temperature_stop_cooling() -> None:
    """Test determine thermostat target temperature stop cooling."""
    target_temperature = 69
    actual_temperature = 70
    hvac_mode = HVACMode.COOL
    cover_services = [SERVICE_CLOSE_COVER]

    new_thermostat_target_temperature = determine_thermostat_target_temperature(
        target_temperature, actual_temperature, hvac_mode, cover_services
    )

    assert new_thermostat_target_temperature == 71


def test_determine_thermostat_target_temperature_continue_heat_cool() -> None:
    """Test determine thermostat target temperature continue cooling."""
    target_temperature = 69
    actual_temperature = 70
    hvac_mode = HVACMode.HEAT_COOL
    cover_services = [SERVICE_OPEN_COVER]

    new_thermostat_target_temperature = determine_thermostat_target_temperature(
        target_temperature, actual_temperature, hvac_mode, cover_services
    )

    assert new_thermostat_target_temperature == target_temperature


def test_determine_cover_services_move_to_heating_open_greater_than() -> None:
    """Determine cover services move to heating open greater than."""
    hvac_mode = HVACMode.HEAT
    rooms = {
        "basement": {
            "target_temperature": 72,
            "actual_temperature": 71,
        }
    }

    cover_services = determine_cover_services(rooms, hvac_mode)

    assert cover_services == [SERVICE_OPEN_COVER]


# def test_determine_cover_services_move_to_heating_open_greater_than_multiple_rooms_same() -> None:
#     """Determine cover services move to heating open greater than multiple rooms."""
#     hvac_mode = HVACMode.HEAT
#     rooms = {
#         "basement": {
#             "target_temperature": 72,
#             "actual_temperature": 71,
#         },
#         "office": {
#             "target_temperature": 72,
#             "actual_temperature": 71,
#         }
#     }

#     cover_services = determine_cover_services(rooms, hvac_mode)

#     assert cover_services == [SERVICE_OPEN_COVER, SERVICE_OPEN_COVER]

# def test_determine_cover_services_move_to_heating_open_greater_than_multiple_rooms_different() -> None:
#     """Determine cover services move to heating open greater than multiple rooms."""
#     hvac_mode = HVACMode.HEAT
#     rooms = {
#         "basement": {
#             "target_temperature": 72,
#             "actual_temperature": 71,
#         },
#         "office": {
#             "target_temperature": 71,
#             "actual_temperature": 72,
#         }
#     }

#     cover_services = determine_cover_services(rooms, hvac_mode)

#     assert cover_services == [SERVICE_OPEN_COVER, SERVICE_CLOSE_COVER]


def test_determine_cover_services_continue_heating_close_equal_to() -> None:
    """Determine cover services continue heating close equal to."""
    hvac_mode = HVACMode.HEAT
    rooms = {
        "basement": {
            "target_temperature": 71,
            "actual_temperature": 71,
        }
    }

    cover_services = determine_cover_services(rooms, hvac_mode)

    assert cover_services == [SERVICE_CLOSE_COVER]


def test_determine_cover_services_stop_heating_close_less_than() -> None:
    """Determine cover services stop heating close less than."""
    hvac_mode = HVACMode.HEAT
    rooms = {"basement": {"target_temperature": 71, "actual_temperature": 72}}

    cover_services = determine_cover_services(rooms, hvac_mode)

    assert cover_services == [SERVICE_CLOSE_COVER]


def test_determine_cover_services_move_to_cooling_open_less_than() -> None:
    """Determine cover services move to cooling open less than."""
    hvac_mode = HVACMode.COOL
    rooms = {
        "basement": {
            "target_temperature": 71,
            "actual_temperature": 72,
        }
    }

    cover_services = determine_cover_services(rooms, hvac_mode)

    assert cover_services == [SERVICE_OPEN_COVER]


def test_determine_cover_services_continue_cooling_close_equal_to() -> None:
    """Determine cover services continue cooling close equal to."""
    hvac_mode = HVACMode.COOL
    rooms = {
        "basement": {
            "target_temperature": 71,
            "actual_temperature": 71,
        }
    }

    cover_services = determine_cover_services(rooms, hvac_mode)

    assert cover_services == [SERVICE_CLOSE_COVER]


def test_determine_cover_services_move_to_cooling_close_greater_than() -> None:
    """Determine cover services move to cooling close greater than."""
    hvac_mode = HVACMode.COOL
    rooms = {
        "basement": {
            "target_temperature": 72,
            "actual_temperature": 71,
        }
    }

    cover_services = determine_cover_services(rooms, hvac_mode)

    assert cover_services == [SERVICE_CLOSE_COVER]


def test_determine_cover_services_do_nothing_heat_cool() -> None:
    """Determine cover services do nothing heat cool."""
    hvac_mode = HVACMode.HEAT_COOL
    rooms = {
        "basement": {
            "target_temperature": 72,
            "actual_temperature": 71,
        }
    }

    cover_services = determine_cover_services(rooms, hvac_mode)

    assert not cover_services
