"""Test util."""
import pytest

from homeassistant.components.climate import HVACMode
from homeassistant.components.hvac_zoning.util import (
    determine_cover_service,
    determine_cover_services,
    determine_thermostat_target_temperature,
    filter_to_valid_areas,
    get_all_damper_and_temperature_entity_ids,
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
            "master_bedroom": ["cover.master_bedroom_vent"],
        },
        "temperature": {
            "main_floor": "sensor.main_floor_temperature",
            "master_bedroom": "sensor.master_bedroom_temperature",
        },
        "climate": {"main_floor": "climate.living_room_thermostat"},
    }

    areas = reformat_and_filter_to_valid_areas(user_input)

    assert areas == {
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
    }


@pytest.mark.parametrize(
    ("user_input", "expected_areas"),
    [
        (
            {
                "damper": {
                    "basement": [
                        "cover.basement_west_vent",
                    ],
                    "guest_bedroom": ["cover.guest_bedroom_vent"],
                    "upstairs_bathroom": ["cover.upstairs_bathroom_vent"],
                },
                "temperature": {
                    "basement": "sensor.basement_temperature",
                    "guest_bedroom": "sensor.guest_bedroom_temperature",
                },
            },
            ["basement", "guest_bedroom"],
        ),
        (
            {
                "damper": {
                    "guest_bedroom": ["cover.guest_bedroom_vent"],
                    "upstairs_bathroom": ["cover.upstairs_bathroom_vent"],
                },
                "temperature": {
                    "main_floor": "sensor.main_floor_temperature",
                    "guest_bedroom": "sensor.guest_bedroom_temperature",
                    "upstairs_bathroom": "sensor.upstairs_bathroom_temperature",
                },
            },
            ["guest_bedroom", "upstairs_bathroom"],
        ),
    ],
)
def test_filter_to_valid_areas(user_input, expected_areas) -> None:
    """Test filter to valid areas."""
    areas = filter_to_valid_areas(user_input)

    assert areas == expected_areas


def test_get_all_damper_and_temperature_entity_ids() -> None:
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

    entities = get_all_damper_and_temperature_entity_ids(areas)

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
        "climate": {"main_floor": "climate.living_room_thermostat"},
    }

    thermostat = get_thermostat_entities(user_input)

    assert thermostat == ["climate.living_room_thermostat"]


@pytest.mark.parametrize(
    ("target_temperature", "actual_temperature", "hvac_mode", "expected_service"),
    [
        (71, 70, HVACMode.HEAT, SERVICE_OPEN_COVER),
        (69, 70, HVACMode.HEAT, SERVICE_CLOSE_COVER),
        (70, 70, HVACMode.HEAT, SERVICE_CLOSE_COVER),
        (69, 70, HVACMode.COOL, SERVICE_OPEN_COVER),
        (71, 70, HVACMode.COOL, SERVICE_CLOSE_COVER),
        (70, 70, HVACMode.COOL, SERVICE_CLOSE_COVER),
        (71, 70, None, SERVICE_OPEN_COVER),
        (71, 70, HVACMode.HEAT_COOL, SERVICE_OPEN_COVER),
        (None, 70, HVACMode.HEAT, SERVICE_OPEN_COVER),
        (70, None, HVACMode.HEAT, SERVICE_OPEN_COVER),
        (None, 70, HVACMode.COOL, SERVICE_OPEN_COVER),
        (70, None, HVACMode.COOL, SERVICE_OPEN_COVER),
    ],
)
def test_determine_cover_service(
    target_temperature, actual_temperature, hvac_mode, expected_service
) -> None:
    """Test determine cover service."""
    service = determine_cover_service(target_temperature, actual_temperature, hvac_mode)

    assert service == expected_service


@pytest.mark.parametrize(
    ("hvac_mode", "rooms", "expected_services"),
    [
        (
            HVACMode.HEAT,
            {"basement": {"target_temperature": 72, "actual_temperature": 71}},
            [SERVICE_OPEN_COVER],
        ),
        (
            HVACMode.HEAT,
            {
                "basement": {"target_temperature": 72, "actual_temperature": 71},
                "office": {"target_temperature": 72, "actual_temperature": 71},
            },
            [SERVICE_OPEN_COVER, SERVICE_OPEN_COVER],
        ),
        (
            HVACMode.HEAT,
            {
                "basement": {"target_temperature": 72, "actual_temperature": 71},
                "office": {"target_temperature": 71, "actual_temperature": 72},
            },
            [SERVICE_OPEN_COVER, SERVICE_CLOSE_COVER],
        ),
        (
            HVACMode.HEAT,
            {
                "basement": {"target_temperature": 71, "actual_temperature": 72},
                "office": {"target_temperature": 71, "actual_temperature": 72},
            },
            [SERVICE_CLOSE_COVER, SERVICE_CLOSE_COVER],
        ),
        (
            HVACMode.HEAT,
            {"basement": {"target_temperature": 71, "actual_temperature": 71}},
            [SERVICE_CLOSE_COVER],
        ),
        (
            HVACMode.HEAT,
            {"basement": {"target_temperature": 71, "actual_temperature": 72}},
            [SERVICE_CLOSE_COVER],
        ),
        (
            HVACMode.COOL,
            {"basement": {"target_temperature": 71, "actual_temperature": 72}},
            [SERVICE_OPEN_COVER],
        ),
        (
            HVACMode.COOL,
            {"basement": {"target_temperature": 71, "actual_temperature": 71}},
            [SERVICE_CLOSE_COVER],
        ),
        (
            HVACMode.COOL,
            {"basement": {"target_temperature": 72, "actual_temperature": 71}},
            [SERVICE_CLOSE_COVER],
        ),
        (
            HVACMode.HEAT_COOL,
            {"basement": {"target_temperature": 72, "actual_temperature": 71}},
            [],
        ),
        (
            HVACMode.OFF,
            {"basement": {"target_temperature": 72, "actual_temperature": 71}},
            [],
        ),
    ],
)
def test_determine_cover_services(hvac_mode, rooms, expected_services) -> None:
    """Test determine cover services."""
    cover_services = determine_cover_services(rooms, hvac_mode)

    assert cover_services == expected_services


@pytest.mark.parametrize(
    (
        "target_temperature",
        "actual_temperature",
        "hvac_mode",
        "cover_services",
        "expected_new_target_temperature",
    ),
    [
        (70, 70, HVACMode.HEAT, [SERVICE_OPEN_COVER], 72),
        (72, 70, HVACMode.HEAT, [SERVICE_OPEN_COVER], 72),
        (72, 70, HVACMode.HEAT, [SERVICE_OPEN_COVER, SERVICE_CLOSE_COVER], 72),
        (71, 70, HVACMode.HEAT, [SERVICE_CLOSE_COVER], 68),
        (70, 70, HVACMode.COOL, [SERVICE_OPEN_COVER], 68),
        (70, 70, HVACMode.COOL, [SERVICE_OPEN_COVER, SERVICE_CLOSE_COVER], 68),
        (68, 70, HVACMode.COOL, [SERVICE_OPEN_COVER], 68),
        (69, 70, HVACMode.COOL, [SERVICE_CLOSE_COVER], 72),
        (68, 70, HVACMode.HEAT_COOL, [SERVICE_OPEN_COVER], 68),
        (68, 70, HVACMode.HEAT_COOL, [SERVICE_OPEN_COVER, SERVICE_CLOSE_COVER], 68),
    ],
)
def test_determine_thermostat_target_temperature(
    target_temperature,
    actual_temperature,
    hvac_mode,
    cover_services,
    expected_new_target_temperature,
) -> None:
    """Test determine thermostat target temperature."""
    new_thermostat_target_temperature = determine_thermostat_target_temperature(
        target_temperature, actual_temperature, hvac_mode, cover_services
    )

    assert new_thermostat_target_temperature == expected_new_target_temperature
