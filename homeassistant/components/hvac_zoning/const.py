"""Constants for the HVAC Zoning integration."""
from homeassistant.components.climate import HVACMode

DOMAIN = "hvac_zoning"

SUPPORTED_HVAC_MODES = [HVACMode.HEAT, HVACMode.COOL]

ACTIVE = "active"
IDLE = "idle"
