"""Test util."""
from collections.abc import Callable
from unittest.mock import MagicMock, call

import pytest

from homeassistant.components.climate import SERVICE_SET_TEMPERATURE, HVACMode
from homeassistant.components.hvac_zoning import (
    adjust_house,
    determine_action,
    determine_change_in_temperature,
    determine_cover_service_to_call,
    filter_to_valid_areas,
    get_all_cover_entity_ids,
    get_all_temperature_entity_ids,
    get_all_thermostat_entity_ids,
)
from homeassistant.components.hvac_zoning.const import ACTIVE, DOMAIN, IDLE
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    SERVICE_CLOSE_COVER,
    SERVICE_OPEN_COVER,
    Platform,
)
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry
from tests.components.recorder.common import wait_recording_done


@pytest.mark.parametrize(
    ("user_input", "expected_areas"),
    [
        (
            {
                "basement": {
                    "covers": [
                        "cover.basement_west_vent",
                    ],
                    "temperature": "sensor.basement_temperature",
                },
                "guest_bedroom": {
                    "covers": ["cover.guest_bedroom_vent"],
                    "temperature": "sensor.guest_bedroom_temperature",
                },
                "upstairs_bathroom": {"covers": ["cover.upstairs_bathroom_vent"]},
            },
            {
                "basement": {
                    "covers": [
                        "cover.basement_west_vent",
                    ],
                    "temperature": "sensor.basement_temperature",
                },
                "guest_bedroom": {
                    "covers": ["cover.guest_bedroom_vent"],
                    "temperature": "sensor.guest_bedroom_temperature",
                },
            },
        ),
        (
            {
                "guest_bedroom": {
                    "covers": ["cover.guest_bedroom_vent"],
                    "temperature": "sensor.guest_bedroom_temperature",
                },
                "upstairs_bathroom": {
                    "covers": ["cover.upstairs_bathroom_vent"],
                    "temperature": "sensor.upstairs_bathroom_temperature",
                },
                "main_floor": {"temperature": "sensor.main_floor_temperature"},
            },
            {
                "guest_bedroom": {
                    "covers": ["cover.guest_bedroom_vent"],
                    "temperature": "sensor.guest_bedroom_temperature",
                },
                "upstairs_bathroom": {
                    "covers": ["cover.upstairs_bathroom_vent"],
                    "temperature": "sensor.upstairs_bathroom_temperature",
                },
            },
        ),
    ],
)
def test_filter_to_valid_areas(user_input, expected_areas) -> None:
    """Test filter to valid areas."""
    areas = filter_to_valid_areas(user_input)

    assert areas == expected_areas


def test_get_all_cover_entity_ids() -> None:
    """Test get all cover entities."""
    areas = {
        "basement": {
            "covers": [
                "cover.basement_west_vent",
                "cover.basement_northeast_vent",
                "cover.basement_southeast_vent",
            ],
            "temperature": "sensor.basement_temperature",
        },
        "upstairs_bathroom": {
            "covers": ["cover.upstairs_bathroom_vent"],
            "temperature": "sensor.upstairs_bathroom_temperature",
        },
    }

    entities = get_all_cover_entity_ids(areas)

    assert entities == [
        "cover.basement_west_vent",
        "cover.basement_northeast_vent",
        "cover.basement_southeast_vent",
        "cover.upstairs_bathroom_vent",
    ]


def test_get_all_temperature_entity_ids() -> None:
    """Test get all temperature entities."""
    areas = {
        "office": {
            "covers": ["cover.office_vent"],
            "temperature": "sensor.office_temperature",
        },
        "upstairs_bathroom": {
            "covers": ["cover.upstairs_bathroom_vent"],
            "temperature": "sensor.upstairs_bathroom_temperature",
        },
    }

    entities = get_all_temperature_entity_ids(areas)

    assert entities == [
        "sensor.office_temperature",
        "sensor.upstairs_bathroom_temperature",
    ]


@pytest.mark.parametrize(
    ("user_input", "expected_thermostats"),
    [
        (
            {"main_floor": {"climate": "climate.living_room_thermostat"}},
            ["climate.living_room_thermostat"],
        ),
        (
            {
                "main_floor": {
                    "climate": "climate.living_room_thermostat",
                },
                "garage": {
                    "climate": "climate.garage_thermostat",
                },
            },
            ["climate.living_room_thermostat", "climate.garage_thermostat"],
        ),
    ],
)
def test_get_all_thermostat_entity_ids(user_input, expected_thermostats) -> None:
    """Test get thermostat entity ids."""
    thermostats = get_all_thermostat_entity_ids(user_input)

    assert thermostats == expected_thermostats


@pytest.mark.parametrize(
    ("target_temperature", "actual_temperature", "hvac_mode", "expected_action"),
    [
        (73, 71, HVACMode.HEAT, ACTIVE),
        (70, 71, HVACMode.COOL, ACTIVE),
        (73, "71.52", HVACMode.HEAT, ACTIVE),
        (70, "71.52", HVACMode.COOL, ACTIVE),
        ("73.1", 71, HVACMode.HEAT, ACTIVE),
        ("70.1", 71, HVACMode.COOL, ACTIVE),
        (71, 73, HVACMode.HEAT, IDLE),
        (71, 70, HVACMode.COOL, IDLE),
        ("71.52", 73, HVACMode.HEAT, IDLE),
        ("71.52", 70, HVACMode.COOL, IDLE),
        (71, "73.1", HVACMode.HEAT, IDLE),
        (71, "70.1", HVACMode.COOL, IDLE),
        ("unknown", 71, HVACMode.COOL, ACTIVE),
        (71, "unknown", HVACMode.COOL, ACTIVE),
    ],
)
def test_determine_action(
    target_temperature, actual_temperature, hvac_mode, expected_action
) -> None:
    """Test determine action."""
    action = determine_action(target_temperature, actual_temperature, hvac_mode)
    assert action == expected_action


@pytest.mark.parametrize(
    ("target_temperature", "hvac_mode", "action", "expected_change_in_temperature"),
    [
        (68, HVACMode.HEAT, "active", 70),
        (68, HVACMode.COOL, "active", 66),
        (68, HVACMode.OFF, "active", 68),
        (68, HVACMode.HEAT, "idle", 68),
        (68, HVACMode.HEAT_COOL, "active", 68),
    ],
)
def test_determine_change_in_temperature(
    target_temperature, hvac_mode, action, expected_change_in_temperature
) -> None:
    """Test determine change in temperature."""
    change_in_temperature = determine_change_in_temperature(
        target_temperature, hvac_mode, action
    )
    assert change_in_temperature == expected_change_in_temperature


def test_adjust_house(hass_recorder: Callable[..., HomeAssistant]) -> None:
    """Test adjust house."""
    central_thermostat_entity_id = "climate.living_room_thermostat"
    cover_entity_id = "cover.master_bedroom_vent"
    area_target_temperature_entity_id = "climate.master_bedroom_thermostat"
    area_actual_temperature_entity_id = "sensor.master_bedroom_temperature"
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "master_bedroom": {
                "covers": [cover_entity_id],
                "temperature": area_actual_temperature_entity_id,
            },
            "main_floor": {
                "climate": central_thermostat_entity_id,
            },
        },
    )
    hass = hass_recorder()
    hass.states.set(
        entity_id=central_thermostat_entity_id,
        new_state="heat",
        attributes={
            "current_temperature": 68,
        },
    )
    hass.states.set(
        entity_id=cover_entity_id,
        new_state="open",
    )
    hass.states.set(
        entity_id=area_target_temperature_entity_id,
        new_state=71,
        attributes={
            "temperature": 71,
        },
    )
    hass.states.set(
        entity_id=area_actual_temperature_entity_id,
        new_state=70,
    )
    wait_recording_done(hass)
    hass.services = MagicMock()

    adjust_house(hass, config_entry)

    expected_central_target_temperature = 70
    hass.services.call.assert_has_calls(
        [
            call(
                Platform.COVER,
                SERVICE_OPEN_COVER,
                service_data={ATTR_ENTITY_ID: cover_entity_id},
            ),
            call(
                Platform.CLIMATE,
                SERVICE_SET_TEMPERATURE,
                service_data={
                    ATTR_ENTITY_ID: central_thermostat_entity_id,
                    ATTR_TEMPERATURE: expected_central_target_temperature,
                },
            ),
        ]
    )
