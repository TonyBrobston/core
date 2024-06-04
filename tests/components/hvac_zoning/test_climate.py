"""Test Climate."""

from unittest.mock import MagicMock

from homeassistant.components.hvac_zoning.climate import Thermostat
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE, EVENT_STATE_CHANGED
from homeassistant.core import HomeAssistant


def test_thermostat_default_target_temperature(hass: HomeAssistant) -> None:
    """Test thermostat default target temperature."""
    name = "basement_thermostat"
    temperature_sensor_entity_id = "sensor.basement_temperature"
    thermostat_entity_id = "climate.living_room_thermostat"
    thermostat = Thermostat(
        hass, name, temperature_sensor_entity_id, thermostat_entity_id
    )

    assert thermostat._attr_target_temperature == 73.0


def test_set_temperature(hass: HomeAssistant) -> None:
    """Test set temperature."""
    name = "basement_thermostat"
    temperature_sensor_entity_id = "sensor.basement_temperature"
    thermostat_entity_id = "climate.living_room_thermostat"
    thermostat = Thermostat(
        hass, name, temperature_sensor_entity_id, thermostat_entity_id
    )

    target_temperature = 75.0
    kwargs = {ATTR_TEMPERATURE: target_temperature}
    thermostat.set_temperature(**kwargs)

    assert thermostat._attr_target_temperature == target_temperature


def test_set_current_temperature(hass: HomeAssistant) -> None:
    """Test set current temperature."""
    name = "basement_thermostat"
    temperature_sensor_entity_id = "sensor.basement_temperature"
    thermostat_entity_id = "climate.living_room_thermostat"
    thermostat = Thermostat(
        hass, name, temperature_sensor_entity_id, thermostat_entity_id
    )
    hass.bus.async_fire(
        EVENT_STATE_CHANGED,
        {
            ATTR_ENTITY_ID: temperature_sensor_entity_id,
            "new_state": MagicMock(state="69.0"),
        },
    )

    assert thermostat._attr_current_temperature == 69.0
