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
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def get_entities_for_area(self, area_id):
    """Get entities for area."""
    entityRegistry = EntityRegistry(self.hass)
    await entityRegistry.async_load()
    return async_entries_for_area(entityRegistry, area_id)


async def get_entities_original_name_for_area(self, area_id):
    """Get entities original name for area."""
    entities = await get_entities_original_name_for_area(self, area_id)
    return [entity.original_name for entity in entities]


def filter_entities_to_device_class_and_map_to_entity_names(entities, device_class):
    """Map entities to entity names."""
    return [
        {"value": entity.entity_id, "label": entity.original_name}
        for entity in entities
        if device_class
        in (entity.original_device_class, entity.entity_id.split(".")[0])
    ]


async def build_schema(self, device_class, multiple):
    """Build schema."""
    return vol.Schema(
        {
            vol.Optional(area.id): SelectSelector(
                SelectSelectorConfig(
                    options=filter_entities_to_device_class_and_map_to_entity_names(
                        await get_entities_for_area(self, area.id),
                        device_class,
                    ),
                    multiple=multiple,
                )
            )
            for area in await get_areas(self)
        },
    )


async def get_areas(self):
    """Load and list areas."""
    areaRegistry = AreaRegistry(self.hass)
    await areaRegistry.async_load()
    return list(areaRegistry.async_list_areas())


class HVACZoningConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HVAC Zoning."""

    VERSION = 1
    init_info: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        # print(f"user_input1: {user_input}")
        # print(f"init_info1: {self.init_info}")
        if user_input is not None:
            self.init_info = {"damper": user_input}
            return await self.async_step_second()

        return self.async_show_form(
            step_id="user",
            data_schema=await build_schema(self, CoverDeviceClass.DAMPER, True),
            errors=errors,
        )

    async def async_step_second(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        # print(f"user_input2: {user_input}")
        # print(f"init_info2: {self.init_info}")
        if user_input is not None:
            self.init_info = {
                **self.init_info,
                "temperature": user_input,
            }
            return await self.async_step_third()

        return self.async_show_form(
            step_id="second",
            data_schema=await build_schema(self, SensorDeviceClass.TEMPERATURE, False),
            errors=errors,
        )

    async def async_step_third(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        # print(f"user_input3: {user_input}")
        # print(f"init_info3: {self.init_info}")
        if user_input is not None:
            self.init_info = user_input
            return self.async_create_entry(
                title="HVAC Zoning",
                data={
                    **self.init_info,
                    "climate": user_input,
                },
            )

        return self.async_show_form(
            step_id="third",
            data_schema=await build_schema(self, "climate", False),
            errors=errors,
        )
