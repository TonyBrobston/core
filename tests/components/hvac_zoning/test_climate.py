"""Test Climate."""

from homeassistant.components.hvac_zoning.climate import Thermostat
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant


def test_thermostat_default_target_temperature() -> None:
    """Test thermostat default target temperature."""
    thermostat = Thermostat("basement_thermostat")

    assert thermostat._attr_target_temperature == 70.0


def test_set_temperature(hass: HomeAssistant) -> None:
    """Test set temperature."""
    thermostat = Thermostat("basement_thermostat")

    target_temperature = 75.0
    kwargs = {ATTR_TEMPERATURE: target_temperature}
    thermostat.set_temperature(**kwargs)

    assert thermostat._attr_target_temperature == target_temperature
