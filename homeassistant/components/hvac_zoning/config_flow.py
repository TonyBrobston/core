"""Config flow for HVAC Zoning integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.cover import CoverDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.area_registry import AreaRegistry
from homeassistant.helpers.entity_registry import EntityRegistry, async_entries_for_area
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def get_areas(self):
    """Load and list areas."""
    areaRegistry = AreaRegistry(self.hass)
    await areaRegistry.async_load()
    return list(areaRegistry.async_list_areas())


def filter_entities_to_device_class_and_map_to_entity_ids(entities, device_class):
    """Map entities to entity names."""
    return [
        entity.entity_id
        for entity in entities
        if device_class
        in (entity.original_device_class, entity.entity_id.split(".")[0])
    ]


async def get_entities_for_area(self, area_id):
    """Get entities for area."""
    entity_registry = EntityRegistry(self.hass)
    await entity_registry.async_load()
    return async_entries_for_area(entity_registry, area_id)


async def get_defaults(self, area, device_class, multiple):
    """Get defaults for form."""
    entities_for_area = await get_entities_for_area(self, area.id)
    entity_ids = filter_entities_to_device_class_and_map_to_entity_ids(
        entities_for_area,
        device_class,
    )
    if not multiple:
        return entity_ids[0] if entity_ids else []
    return entity_ids


def filter_entities_to_device_class_and_map_to_value_and_label_array_of_dict(
    entities, device_class
):
    """Map entities to entity names."""
    return [
        {"value": entity.entity_id, "label": entity.original_name}
        for entity in entities
        if device_class
        in (entity.original_device_class, entity.entity_id.split(".")[0])
    ]


async def get_options(self, area, device_class):
    """Get options for form."""
    entities_for_area = await get_entities_for_area(self, area.id)
    entity_ids = (
        filter_entities_to_device_class_and_map_to_value_and_label_array_of_dict(
            entities_for_area,
            device_class,
        )
    )
    return entity_ids


async def build_schema_for_device_class(self, device_class, multiple):
    """Build schema for device class."""
    areas = await get_areas(self)
    return vol.Schema(
        {
            vol.Optional(
                area.id,
                default=await get_defaults(self, area, device_class, multiple),
            ): SelectSelector(
                SelectSelectorConfig(
                    options=await get_options(self, area, device_class),
                    multiple=multiple,
                )
            )
            for area in areas
            if len(await get_options(self, area, device_class)) != 0
        },
    )


async def build_schema_for_areas(self):
    """Build schema for areas."""
    areas = await get_areas(self)
    return vol.Schema(
        {
            vol.Optional("bedrooms"): SelectSelector(
                SelectSelectorConfig(
                    options=[{"value": area.id, "label": area.name} for area in areas],
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                )
            )
        }
        if areas
        else {},
    )


def get_all_rooms(user_input1, user_input2):
    """Get all rooms."""
    return sorted(set(user_input1.keys()).union(user_input2.keys()))


def merge_user_input(config_entry, user_input, key):
    """Merge user input."""
    rooms = get_all_rooms(config_entry, user_input)
    return {
        room: {
            **config_entry.get(room, {}),
            **({key: user_input.get(room)} if room in user_input else {}),
        }
        for room in rooms
    }


def convert_bedroom_input_to_config_entry(config_entry, user_input):
    """Convert bedroom input to config entry."""
    bedrooms = user_input.get("bedrooms", [])
    bedroom_config_entry = {bedroom: True for bedroom in bedrooms}
    rooms = get_all_rooms(config_entry, bedroom_config_entry)
    return {room: room in bedrooms for room in rooms}


class HVACZoningConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HVAC Zoning."""

    VERSION = 1
    init_info: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle selecting vents."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self.init_info = merge_user_input(self.init_info, user_input, "covers")
            return await self.async_step_second()

        return self.async_show_form(
            step_id="user",
            data_schema=await build_schema_for_device_class(
                self, CoverDeviceClass.DAMPER, True
            ),
            errors=errors,
        )

    async def async_step_second(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle selecting temperature sensors."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self.init_info = merge_user_input(self.init_info, user_input, "temperature")
            return await self.async_step_third()

        return self.async_show_form(
            step_id="second",
            data_schema=await build_schema_for_device_class(
                self, SensorDeviceClass.TEMPERATURE, False
            ),
            errors=errors,
        )

    async def async_step_third(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle selecting the thermostat."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self.init_info = merge_user_input(self.init_info, user_input, "climate")
            return await self.async_step_fourth()

        return self.async_show_form(
            step_id="third",
            data_schema=await build_schema_for_device_class(self, "climate", False),
            errors=errors,
        )

    async def async_step_fourth(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle selecting the thermostat."""
        errors: dict[str, str] = {}
        if user_input is not None:
            bedrooms = convert_bedroom_input_to_config_entry(self.init_info, user_input)
            self.init_info = merge_user_input(self.init_info, bedrooms, "bedroom")
            return self.async_create_entry(
                title=DOMAIN,
                data=self.init_info,
            )

        return self.async_show_form(
            step_id="fourth",
            data_schema=await build_schema_for_areas(self),
            errors=errors,
        )
