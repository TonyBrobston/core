"""Test the HVAC Zoning config flow."""


from homeassistant.components.hvac_zoning.config_flow import (
    filter_entities_to_device_class_and_map_to_entity_ids,
    filter_entities_to_device_class_and_map_to_value_and_label_array_of_dict,
)
from homeassistant.helpers.entity_registry import RegistryEntry

# async def test_form(hass: HomeAssistant, mock_setup_entry: AsyncMock) -> None:
#     """Test we get the form."""
#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )
#     assert result["type"] == FlowResultType.FORM
#     assert result["errors"] == {}

#     with patch(
#         "homeassistant.components.hvac_zoning.config_flow.PlaceholderHub.authenticate",
#         return_value=True,
#     ):
#         result = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {
#                 CONF_HOST: "1.1.1.1",
#                 CONF_USERNAME: "test-username",
#                 CONF_PASSWORD: "test-password",
#             },
#         )
#         await hass.async_block_till_done()

#     assert result["type"] == FlowResultType.CREATE_ENTRY
#     assert result["title"] == "Name of the device"
#     assert result["data"] == {
#         CONF_HOST: "1.1.1.1",
#         CONF_USERNAME: "test-username",
#         CONF_PASSWORD: "test-password",
#     }
#     assert len(mock_setup_entry.mock_calls) == 1


# async def test_form_invalid_auth(
#     hass: HomeAssistant, mock_setup_entry: AsyncMock
# ) -> None:
#     """Test we handle invalid auth."""
#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )

#     with patch(
#         "homeassistant.components.hvac_zoning.config_flow.PlaceholderHub.authenticate",
#         side_effect=InvalidAuth,
#     ):
#         result = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {
#                 CONF_HOST: "1.1.1.1",
#                 CONF_USERNAME: "test-username",
#                 CONF_PASSWORD: "test-password",
#             },
#         )

#     assert result["type"] == FlowResultType.FORM
#     assert result["errors"] == {"base": "invalid_auth"}

#     # Make sure the config flow tests finish with either an
#     # FlowResultType.CREATE_ENTRY or FlowResultType.ABORT so
#     # we can show the config flow is able to recover from an error.
#     with patch(
#         "homeassistant.components.hvac_zoning.config_flow.PlaceholderHub.authenticate",
#         return_value=True,
#     ):
#         result = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {
#                 CONF_HOST: "1.1.1.1",
#                 CONF_USERNAME: "test-username",
#                 CONF_PASSWORD: "test-password",
#             },
#         )
#         await hass.async_block_till_done()

#     assert result["type"] == FlowResultType.CREATE_ENTRY
#     assert result["title"] == "Name of the device"
#     assert result["data"] == {
#         CONF_HOST: "1.1.1.1",
#         CONF_USERNAME: "test-username",
#         CONF_PASSWORD: "test-password",
#     }
#     assert len(mock_setup_entry.mock_calls) == 1


# async def test_form_cannot_connect(
#     hass: HomeAssistant, mock_setup_entry: AsyncMock
# ) -> None:
#     """Test we handle cannot connect error."""
#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )

#     with patch(
#         "homeassistant.components.hvac_zoning.config_flow.PlaceholderHub.authenticate",
#         side_effect=CannotConnect,
#     ):
#         result = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {
#                 CONF_HOST: "1.1.1.1",
#                 CONF_USERNAME: "test-username",
#                 CONF_PASSWORD: "test-password",
#             },
#         )

#     assert result["type"] == FlowResultType.FORM
#     assert result["errors"] == {"base": "cannot_connect"}

#     # Make sure the config flow tests finish with either an
#     # FlowResultType.CREATE_ENTRY or FlowResultType.ABORT so
#     # we can show the config flow is able to recover from an error.

#     with patch(
#         "homeassistant.components.hvac_zoning.config_flow.PlaceholderHub.authenticate",
#         return_value=True,
#     ):
#         result = await hass.config_entries.flow.async_configure(
#             result["flow_id"],
#             {
#                 CONF_HOST: "1.1.1.1",
#                 CONF_USERNAME: "test-username",
#                 CONF_PASSWORD: "test-password",
#             },
#         )
#         await hass.async_block_till_done()

#     assert result["type"] == FlowResultType.CREATE_ENTRY
#     assert result["title"] == "Name of the device"
#     assert result["data"] == {
#         CONF_HOST: "1.1.1.1",
#         CONF_USERNAME: "test-username",
#         CONF_PASSWORD: "test-password",
#     }
#     assert len(mock_setup_entry.mock_calls) == 1


def test_filter_entities_to_device_class_and_map_to_value_and_label_array_of_dict() -> (
    None
):
    """Test map entities to entity names."""
    device_class = "damper"
    entities = [
        RegistryEntry(
            entity_id="sensor.basement_temperature",
            unique_id="Basement Temperature",
            platform="hvac_stubs",
            id="fcdf8c625327e2bd610ac6b4335ca438",
            original_name="Basement Temperature",
            original_device_class="temperature",
        ),
        RegistryEntry(
            entity_id="cover.basement_west_vent",
            unique_id="Basement West Vent",
            platform="hvac_stubs",
            id="800d6dcc0aef4b6a42476de9ff1403ad",
            original_name="Basement West Vent",
            original_device_class="damper",
        ),
        RegistryEntry(
            entity_id="cover.basement_northeast_vent",
            unique_id="Basement Northeast Vent",
            platform="hvac_stubs",
            id="0ae78e2e8f74045281a8ed154cd2b06d",
            original_name="Basement Northeast Vent",
            original_device_class="damper",
        ),
        RegistryEntry(
            entity_id="cover.basement_southeast_vent",
            unique_id="Basement Southeast Vent",
            platform="hvac_stubs",
            id="16d81f78e8b7917950f984277ba4feff",
            original_name="Basement Southeast Vent",
            original_device_class="damper",
        ),
    ]

    entity_names = (
        filter_entities_to_device_class_and_map_to_value_and_label_array_of_dict(
            entities, device_class
        )
    )

    expected_entity_names = [
        {"label": "Basement West Vent", "value": "cover.basement_west_vent"},
        {"label": "Basement Northeast Vent", "value": "cover.basement_northeast_vent"},
        {"label": "Basement Southeast Vent", "value": "cover.basement_southeast_vent"},
    ]
    assert entity_names == expected_entity_names


def test_filter_entities_to_device_class_and_map_to_value_and_label_array_of_dict_climate() -> (
    None
):
    """Test map entities to entity names."""
    device_class = "climate"
    entities = [
        RegistryEntry(
            entity_id="climate.living_room_thermostat",
            unique_id="Living Room Thermostat",
            platform="hvac_zoning_stubs",
            id="9ac9672ee6b6e117ad7dabd02e07c3ec",
            original_name="Living Room Thermostat",
            original_device_class=None,
        ),
        RegistryEntry(
            entity_id="sensor.basement_temperature",
            unique_id="Basement Temperature",
            platform="hvac_stubs",
            id="fcdf8c625327e2bd610ac6b4335ca438",
            original_name="Basement Temperature",
            original_device_class="temperature",
        ),
    ]

    entity_names = (
        filter_entities_to_device_class_and_map_to_value_and_label_array_of_dict(
            entities, device_class
        )
    )

    expected_entity_names = [
        {"value": "climate.living_room_thermostat", "label": "Living Room Thermostat"}
    ]
    assert entity_names == expected_entity_names


def test_filter_entities_to_device_class_and_map_to_entity_names() -> None:
    """Test map entities to entity names."""
    device_class = "damper"
    entities = [
        RegistryEntry(
            entity_id="sensor.basement_temperature",
            unique_id="Basement Temperature",
            platform="hvac_stubs",
            id="fcdf8c625327e2bd610ac6b4335ca438",
            original_name="Basement Temperature",
            original_device_class="temperature",
        ),
        RegistryEntry(
            entity_id="cover.basement_west_vent",
            unique_id="Basement West Vent",
            platform="hvac_stubs",
            id="800d6dcc0aef4b6a42476de9ff1403ad",
            original_name="Basement West Vent",
            original_device_class="damper",
        ),
        RegistryEntry(
            entity_id="cover.basement_northeast_vent",
            unique_id="Basement Northeast Vent",
            platform="hvac_stubs",
            id="0ae78e2e8f74045281a8ed154cd2b06d",
            original_name="Basement Northeast Vent",
            original_device_class="damper",
        ),
        RegistryEntry(
            entity_id="cover.basement_southeast_vent",
            unique_id="Basement Southeast Vent",
            platform="hvac_stubs",
            id="16d81f78e8b7917950f984277ba4feff",
            original_name="Basement Southeast Vent",
            original_device_class="damper",
        ),
    ]

    entity_names = filter_entities_to_device_class_and_map_to_entity_ids(
        entities, device_class
    )

    expected_entity_names = [
        "cover.basement_west_vent",
        "cover.basement_northeast_vent",
        "cover.basement_southeast_vent",
    ]
    assert entity_names == expected_entity_names
