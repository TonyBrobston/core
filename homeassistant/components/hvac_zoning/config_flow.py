"""Config flow for HVAC Zoning integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.area_registry import AreaRegistry
from homeassistant.helpers.entity_registry import EntityRegistry, async_entries_for_area

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TO DO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )

    hub = PlaceholderHub(data[CONF_HOST])

    if not await hub.authenticate(data[CONF_USERNAME], data[CONF_PASSWORD]):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Name of the device"}


async def get_entities_for_area(self, area_id):
    """Get entities for area."""
    entityRegistry = EntityRegistry(self.hass)
    await entityRegistry.async_load()
    return async_entries_for_area(entityRegistry, area_id)


async def get_entities_original_name_for_area(self, area_id):
    """Get entities original name for area."""
    entities = await get_entities_original_name_for_area(self, area_id)
    return [entity.original_name for entity in entities]


class HVACZoningConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HVAC Zoning."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        areaRegistry = AreaRegistry(self.hass)
        await areaRegistry.async_load()
        area_entries = list(areaRegistry.async_list_areas())

        # print(f"area_entries: {area_entries}")

        # entityRegistry = EntityRegistry(self.hass)
        # await entityRegistry.async_load()
        # bedroom_entities = async_entries_for_area(entityRegistry, "bedroom")
        # bedroom_entities = await get_entities_for_area(self, "bedroom")
        # print(f"bedroom_entities: {bedroom_entities}")

        # print([async get_entities_for_area(self, entry.id) for entry in area_entries])

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(entry.id): vol.In(
                        filter_entities_to_device_class_and_map_to_entity_names(
                            await get_entities_for_area(self, entry.id), "temperature"
                        )
                    )
                    for entry in area_entries
                    # vol.Required("foo"): vol.In(["foo", "bar"]),
                    # vol.Optional("derp"): SelectSelector(
                    #     SelectSelectorConfig(
                    #         options=["text", "headers"],
                    #         multiple=True,
                    #     )
                    # ),
                }
            ),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


def filter_entities_to_device_class_and_map_to_entity_names(entities, device_class):
    """Map entities to entity names."""
    return [
        entity.original_name
        for entity in entities
        if entity.original_device_class == device_class
    ]
