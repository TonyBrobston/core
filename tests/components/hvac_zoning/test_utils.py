"""Test utils."""
import pytest

from homeassistant.components.hvac_zoning.utils import filter_to_valid_areas


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
