"""Test util."""
from collections.abc import Callable

import pytest

from homeassistant.components.climate import HVACMode
from homeassistant.components.hvac_zoning.const import DOMAIN
from homeassistant.components.hvac_zoning.util import (
    adjust_covers,
    determine_cover_service,
    determine_cover_services,
    determine_thermostat_target_temperature,
    filter_to_valid_areas,
    get_all_damper_and_temperature_entity_ids,
    get_thermostat_entities,
)
from homeassistant.const import SERVICE_CLOSE_COVER, SERVICE_OPEN_COVER
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


@pytest.mark.parametrize(
    ("user_input", "expected_thermostats"),
    [
        (
            {"climate": {"main_floor": "climate.living_room_thermostat"}},
            ["climate.living_room_thermostat"],
        ),
        (
            {
                "climate": {
                    "main_floor": "climate.living_room_thermostat",
                    "garage": "climate.garage_thermostat",
                },
            },
            ["climate.living_room_thermostat", "climate.garage_thermostat"],
        ),
    ],
)
def test_get_thermostat_entities(user_input, expected_thermostats) -> None:
    """Test get thermostat entities."""
    thermostat = get_thermostat_entities(user_input)

    assert thermostat == expected_thermostats


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
            [SERVICE_OPEN_COVER],
        ),
        (
            HVACMode.OFF,
            {"basement": {"target_temperature": 72, "actual_temperature": 71}},
            [SERVICE_OPEN_COVER],
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
        (71, 70, HVACMode.HEAT, [], 68),
        (70, 70, HVACMode.COOL, [SERVICE_OPEN_COVER], 68),
        (70, 70, HVACMode.COOL, [SERVICE_OPEN_COVER, SERVICE_CLOSE_COVER], 68),
        (68, 70, HVACMode.COOL, [SERVICE_OPEN_COVER], 68),
        (69, 70, HVACMode.COOL, [SERVICE_CLOSE_COVER], 72),
        (69, 70, HVACMode.COOL, [], 72),
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


# def test_build_room_temperature_dict(
#     hass_recorder: Callable[..., HomeAssistant],
# ) -> None:
#     """Test build room temperature dict."""
#     area = "master_bedroom"
#     thermostat_entity_id = area + "thermostat"
#     temperature_entity_id = "sensor." + area + "_temperature"
#     formatted_user_input = {area: {"temperature": temperature_entity_id}}
#     hass = hass_recorder()
#     target_temperature = 69
#     hass.states.set(
#         entity_id=thermostat_entity_id,
#         new_state="unknown",
#         attributes={
#             "temperature": target_temperature,
#         },
#     )
#     actual_temperature = 70
#     hass.states.set(
#         entity_id=temperature_entity_id,
#         new_state=actual_temperature,
#     )
#     wait_recording_done(hass)

#     room_temperature_dict = build_room_temperature_dict(hass, formatted_user_input)

#     assert room_temperature_dict == {
#         "master_bedroom": {
#             "target_temperature": target_temperature,
#             "actual_temperature": actual_temperature,
#         }
#     }


def test_adjust_covers(hass_recorder: Callable[..., HomeAssistant]) -> None:
    """Test adjust covers."""
    # We need to write a test that drives into a hass.state.get on the climate entity id, then pull out the mode
    # then we need to do a hass.state.get for all cover entities and build them into a dict like the one below
    # then pass both of these things into determine_cover_services, then hass.services.call based on the output
    # of determine_cover_services
    # HVACMode.HEAT,
    # {"basement": {"target_temperature": 72, "actual_temperature": 71}},
    hass = hass_recorder()
    thermostat_entity_id = "climate.living_room_thermostat"
    cover_entity_id = "cover.master_bedroom_vent"
    temperature_entity_id = "sensor.master_bedroom_temperature"
    data = {
        "damper": {
            "master_bedroom": [cover_entity_id],
        },
        "temperature": {
            "master_bedroom": temperature_entity_id,
        },
        "climate": {"main_floor": thermostat_entity_id},
    }
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        # unique_id="123456",
        data=data,
    )
    hass.states.set(
        entity_id=thermostat_entity_id,
        new_state="unknown",
        attributes={
            "temperature": 69,
            "hvac_mode": "heat",
        },
    )
    hass.states.set(
        entity_id=cover_entity_id,
        new_state="open",
    )
    hass.states.set(
        entity_id=temperature_entity_id,
        new_state="70",
    )
    wait_recording_done(hass)
    derp = adjust_covers(hass, config_entry)
    assert derp == 69
