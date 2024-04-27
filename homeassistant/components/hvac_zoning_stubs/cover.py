"""Cover stub."""

from __future__ import annotations

from homeassistant.components.cover import CoverDeviceClass, CoverEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_CLOSED, STATE_OPEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


class Cover(CoverEntity):
    "Derp is a Cover."

    def __init__(self, name: str, current_cover_position: str) -> None:
        "Derp is a Cover init."
        self._attr_unique_id = name
        self._attr_name = name
        self._attr_device_class = CoverDeviceClass.DAMPER
        self._attr_current_cover_position = 0
        self._attr_is_closed = current_cover_position == STATE_CLOSED


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Async setup entry."""
    async_add_entities(
        [
            Cover("Living Room Northeast Vent", STATE_CLOSED),
            Cover("Living Room Southeast Vent", STATE_OPEN),
            Cover("Kitchen South Vent", STATE_OPEN),
            Cover("Kitchen Northwest Vent", STATE_CLOSED),
            Cover("Basement West Vent", STATE_CLOSED),
            Cover("Basement Northeast Vent", STATE_CLOSED),
            Cover("Basement Southeast Vent", STATE_CLOSED),
            Cover("Office Vent", STATE_OPEN),
            Cover("Guest Bedroom Vent", STATE_CLOSED),
            Cover("Master Bedroom Vent", STATE_OPEN),
            Cover("Upstairs Bathroom Vent", STATE_OPEN),
        ]
    )
