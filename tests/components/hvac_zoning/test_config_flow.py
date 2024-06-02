"""Test the HVAC Zoning config flow."""
from unittest.mock import MagicMock, patch

import pytest

from homeassistant import data_entry_flow
from homeassistant.components.hvac_zoning import config_flow
from homeassistant.components.hvac_zoning.config_flow import (
    filter_entities_to_device_class_and_map_to_entity_ids,
    filter_entities_to_device_class_and_map_to_value_and_label_array_of_dict,
    get_all_rooms,
    get_defaults,
    get_entities_for_area,
    get_options,
    merge_user_input,
)
from homeassistant.components.hvac_zoning.const import DOMAIN
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.area_registry import AreaEntry
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
    EntityRegistryItems,
    RegistryEntry,
)

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


# async def test_get_entities_for_area(hass: HomeAssistant) -> None:
#     """Test get entities for area."""
#     mock_self = MagicMock()
#     mock_self.hass = hass
#     entity_id = "hvac_zoning.foo_cover"
#     registry_id = "47ad524676f7deec03f2ef84f18ed00"
#     registry_entry = RegistryEntry(entity_id, "bar", Platform.COVER, id=registry_id)
#     entity_registry_items = EntityRegistryItems()
#     entity_registry_items.__setitem__(entity_id, registry_entry)
#     entity_registry = EntityRegistry(hass)
#     entity_registry.entities = entity_registry_items
#     entity_registry.deleted_entities = {}
#     area_id = "living_room"
#     entity_registry.async_update_entity(entity_id, area_id=area_id)
#     await hass.async_block_till_done()

#     with mock_async_load(entity_registry):
#         print("foo")

#     with patch(
#         "homeassistant.components.hvac_zoning.config_flow.EntityRegistry",
#         return_value=entity_registry,
#     ):
#         entities = await get_entities_for_area(mock_self, area_id)

#         assert entities == [
#             RegistryEntry(
#                 entity_id=entity_id,
#                 unique_id="bar",
#                 platform=Platform.COVER,
#                 previous_unique_id=None,
#                 aliases=set(),
#                 area_id=area_id,
#                 categories={},
#                 capabilities=None,
#                 config_entry_id=None,
#                 device_class=None,
#                 device_id=None,
#                 disabled_by=None,
#                 entity_category=None,
#                 hidden_by=None,
#                 icon=None,
#                 id=registry_id,
#                 has_entity_name=False,
#                 labels=set(),
#                 name=None,
#                 options={},
#                 original_device_class=None,
#                 original_icon=None,
#                 original_name=None,
#                 supported_features=0,
#                 translation_key=None,
#                 unit_of_measurement=None,
#             )
#         ]


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

    assert entity_names == [
        {"label": "Basement West Vent", "value": "cover.basement_west_vent"},
        {"label": "Basement Northeast Vent", "value": "cover.basement_northeast_vent"},
        {"label": "Basement Southeast Vent", "value": "cover.basement_southeast_vent"},
    ]


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

    assert entity_names == [
        {"value": "climate.living_room_thermostat", "label": "Living Room Thermostat"}
    ]


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
    ]

    entity_names = filter_entities_to_device_class_and_map_to_entity_ids(
        entities, device_class
    )

    assert entity_names == [
        "cover.basement_west_vent",
        "cover.basement_northeast_vent",
    ]


@pytest.mark.parametrize(
    ("device_class", "area_name", "multiple", "expected_defaults"),
    [
        (
            "damper",
            "basement",
            True,
            ["cover.basement_west_vent", "cover.basement_northeast_vent"],
        ),
        (
            "damper",
            "basement",
            False,
            "cover.basement_west_vent",
        ),
    ],
)
async def test_get_defaults(
    hass: HomeAssistant, device_class, area_name, multiple, expected_defaults
) -> None:
    """Test get defaults."""
    mock_self = MagicMock()
    mock_self.hass = hass
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
    ]
    area_entry = AreaEntry(
        id=area_name,
        name=area_name,
        normalized_name=area_name,
        aliases=[],
        floor_id=1,
        icon=None,
        picture=None,
    )

    with patch(
        "homeassistant.components.hvac_zoning.config_flow.get_entities_for_area",
        return_value=entities,
    ):
        defaults = await get_defaults(mock_self, area_entry, device_class, multiple)

        assert defaults == expected_defaults


async def test_get_options(hass: HomeAssistant) -> None:
    """Test get options."""
    mock_self = MagicMock()
    mock_self.hass = hass
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
    ]
    area_entry = AreaEntry(
        id="basement",
        name="basement",
        normalized_name="basement",
        aliases=[],
        floor_id=1,
        icon=None,
        picture=None,
    )

    with patch(
        "homeassistant.components.hvac_zoning.config_flow.get_entities_for_area",
        return_value=entities,
    ):
        options = await get_options(mock_self, area_entry, "damper")

        assert options == [
            {"value": "cover.basement_west_vent", "label": "Basement West Vent"},
            {
                "label": "Basement Northeast Vent",
                "value": "cover.basement_northeast_vent",
            },
        ]


@pytest.mark.parametrize(
    ("user_input1", "user_input2", "expected_output"),
    [
        (
            {
                "main_floor": {
                    "covers": [
                        "cover.living_room_northeast_vent",
                    ],
                    "temperature": "sensor.main_floor_temperature",
                },
                "upstairs_bathroom": {
                    "covers": ["cover.upstairs_bathroom_vent"],
                    "temperature": "sensor.upstairs_bathroom_temperature",
                },
            },
            {"main_floor": "climate.living_room_thermostat"},
            ["main_floor", "upstairs_bathroom"],
        ),
        (
            {"main_floor": {"climate": "climate.living_room_thermostat"}},
            {
                "main_floor": {
                    "covers": [
                        "cover.living_room_northeast_vent",
                    ],
                    "temperature": "sensor.main_floor_temperature",
                },
                "upstairs_bathroom": {
                    "covers": ["cover.upstairs_bathroom_vent"],
                    "temperature": "sensor.upstairs_bathroom_temperature",
                },
            },
            ["main_floor", "upstairs_bathroom"],
        ),
    ],
)
def test_get_all_rooms(user_input1, user_input2, expected_output) -> None:
    """Test get all rooms."""
    rooms = get_all_rooms(user_input1, user_input2)
    assert rooms == expected_output


@pytest.mark.parametrize(
    ("config_entry", "user_input", "key", "expected_output"),
    [
        (
            {},
            {
                "office": ["cover.office_vent"],
                "upstairs_bathroom": ["cover.upstairs_bathroom_vent"],
            },
            "covers",
            {
                "office": {"covers": ["cover.office_vent"]},
                "upstairs_bathroom": {"covers": ["cover.upstairs_bathroom_vent"]},
            },
        ),
        (
            {
                "office": {"covers": ["cover.office_vent"]},
                "upstairs_bathroom": {"covers": ["cover.upstairs_bathroom_vent"]},
            },
            {
                "office": "sensor.office_temperature",
                "upstairs_bathroom": "sensor.upstairs_bathroom_temperature",
            },
            "temperature",
            {
                "office": {
                    "covers": ["cover.office_vent"],
                    "temperature": "sensor.office_temperature",
                },
                "upstairs_bathroom": {
                    "covers": ["cover.upstairs_bathroom_vent"],
                    "temperature": "sensor.upstairs_bathroom_temperature",
                },
            },
        ),
        (
            {
                "main_floor": {
                    "covers": [
                        "cover.living_room_northeast_vent",
                    ],
                    "temperature": "sensor.main_floor_temperature",
                },
                "upstairs_bathroom": {
                    "covers": ["cover.upstairs_bathroom_vent"],
                    "temperature": "sensor.upstairs_bathroom_temperature",
                },
            },
            {
                "main_floor": "climate.living_room_thermostat",
            },
            "climate",
            {
                "main_floor": {
                    "climate": "climate.living_room_thermostat",
                    "covers": [
                        "cover.living_room_northeast_vent",
                    ],
                    "temperature": "sensor.main_floor_temperature",
                },
                "upstairs_bathroom": {
                    "covers": ["cover.upstairs_bathroom_vent"],
                    "temperature": "sensor.upstairs_bathroom_temperature",
                },
            },
        ),
    ],
)
def test_merge_user_input(config_entry, user_input, key, expected_output) -> None:
    """Test merge user inputs."""
    assert merge_user_input(config_entry, user_input, key) == expected_output


async def test_step_user_without_user_input(hass: HomeAssistant) -> None:
    """Test step user without user input."""
    flow = config_flow.HVACZoningConfigFlow()
    flow.hass = hass

    result = await flow.async_step_user()

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["data_schema"].schema == {}


async def test_step_user_with_user_input(hass: HomeAssistant) -> None:
    """Test step user with user input."""
    flow = config_flow.HVACZoningConfigFlow()
    flow.hass = hass
    user_input = {
        "office": ["cover.office_vent"],
        "upstairs_bathroom": ["cover.upstairs_bathroom_vent"],
    }

    result = await flow.async_step_user(user_input)

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "second"
    assert flow.init_info == {
        "office": {"covers": ["cover.office_vent"]},
        "upstairs_bathroom": {"covers": ["cover.upstairs_bathroom_vent"]},
    }


async def test_step_second_without_user_input(hass: HomeAssistant) -> None:
    """Test step second without user input."""
    flow = config_flow.HVACZoningConfigFlow()
    flow.hass = hass

    result = await flow.async_step_second()

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "second"
    assert result["data_schema"].schema == {}


async def test_step_second_with_user_input(hass: HomeAssistant) -> None:
    """Test step second with user input."""
    flow = config_flow.HVACZoningConfigFlow()
    flow.hass = hass
    user_input = {
        "office": "sensor.office_temperature",
        "upstairs_bathroom": "sensor.upstairs_bathroom_temperature",
    }

    result = await flow.async_step_second(user_input)

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "third"
    assert flow.init_info == {
        "office": {
            "temperature": "sensor.office_temperature",
        },
        "upstairs_bathroom": {
            "temperature": "sensor.upstairs_bathroom_temperature",
        },
    }


async def test_step_third_without_user_input(hass: HomeAssistant) -> None:
    """Test step third without user input."""
    flow = config_flow.HVACZoningConfigFlow()
    flow.hass = hass

    result = await flow.async_step_third()

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "third"
    assert result["data_schema"].schema == {}


async def test_step_third_with_user_input(hass: HomeAssistant) -> None:
    """Test step third with user input."""
    flow = config_flow.HVACZoningConfigFlow()
    flow.hass = hass
    user_input = {
        "main_floor": "climate.living_room_thermostat",
    }

    result = await flow.async_step_third(user_input)

    assert result["title"] == DOMAIN
    assert result["data"] == {
        "main_floor": {
            "climate": "climate.living_room_thermostat",
        },
    }
