"""The HVAC Zoning integration."""

from __future__ import annotations
import datetime

from homeassistant.components.climate import SERVICE_SET_TEMPERATURE, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    EVENT_STATE_CHANGED,
    SERVICE_CLOSE_COVER,
    SERVICE_OPEN_COVER,
    Platform,
)
from homeassistant.core import HomeAssistant

from .const import ACTIVE, DOMAIN, IDLE, LOGGER, SUPPORTED_HVAC_MODES
from .utils import filter_to_valid_areas, get_all_thermostat_entity_ids

PLATFORMS: list[Platform] = [Platform.CLIMATE]


def get_all_cover_entity_ids(areas):
    """Get all cover entity ids."""
    return [cover for area in areas.values() for cover in area.get("covers", [])]


def get_all_temperature_entity_ids(areas):
    """Get all temperature entity ids."""
    return [area["temperature"] for area in areas.values() if "temperature" in area]


def determine_action(
    target_temperature: int, actual_temperature: int, hvac_mode: HVACMode
):
    """Determine action."""
    if (
        hvac_mode in SUPPORTED_HVAC_MODES
        and target_temperature is not None
        and actual_temperature is not None
    ):
        modified_actual_temperature = int(float(actual_temperature))
        modified_target_temperature = int(float(target_temperature))
        match hvac_mode:
            case HVACMode.HEAT:
                if modified_actual_temperature >= modified_target_temperature:
                    return IDLE
            case HVACMode.COOL:
                if modified_actual_temperature <= modified_target_temperature:
                    return IDLE

    return ACTIVE


def determine_is_night_time(bed_time, wake_time):
    """Determine is night time."""
    now = datetime.datetime.now()
    now_date = now.strftime("%Y-%m-%d")
    now_time = now.strftime("%H:%M:%S")

    if now_time > bed_time and now_time <= "23:59:59":
        bed_datetime = datetime.datetime.strptime(
            f"{now_date} {bed_time}", "%Y-%m-%d %H:%M:%S"
        )
        wake_date = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        wake_datetime = datetime.datetime.strptime(
            f"{wake_date} {wake_time}", "%Y-%m-%d %H:%M:%S"
        )
    elif now_time >= "00:00:00" and now_time < wake_time:
        bed_date = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        bed_datetime = datetime.datetime.strptime(
            f"{bed_date} {bed_time}", "%Y-%m-%d %H:%M:%S"
        )
        wake_datetime = datetime.datetime.strptime(
            f"{now_date} {wake_time}", "%Y-%m-%d %H:%M:%S"
        )
    else:
        return False

    return now > bed_datetime and now < wake_datetime


def determine_cover_service_to_call(
    target_temperature: int,
    actual_temperature: int,
    hvac_mode: HVACMode,
    thermostat_action: str,
) -> str:
    """Determine cover service."""
    action = (
        ACTIVE
        if thermostat_action == IDLE
        else determine_action(target_temperature, actual_temperature, hvac_mode)
    )

    return SERVICE_CLOSE_COVER if action is not ACTIVE else SERVICE_OPEN_COVER


def determine_change_in_temperature(target_temperature, hvac_mode, action):
    """Determine change in temperature."""
    if action == ACTIVE and hvac_mode in SUPPORTED_HVAC_MODES:
        match hvac_mode:
            case HVACMode.HEAT:
                return target_temperature + 2
            case HVACMode.COOL:
                return target_temperature - 2
    return target_temperature


def adjust_house(hass: HomeAssistant, config_entry: ConfigEntry):
    """Adjust house."""
    config_entry_data = config_entry.as_dict()["data"]
    central_thermostat_entity_id = get_all_thermostat_entity_ids(config_entry_data)[0]
    central_thermostat = hass.states.get(central_thermostat_entity_id)
    central_thermostat_actual_temperature = central_thermostat.attributes[
        "current_temperature"
    ]
    central_hvac_mode = central_thermostat.state
    config_entry_data_with_only_valid_areas = filter_to_valid_areas(config_entry_data)
    areas = config_entry_data_with_only_valid_areas.get("areas", {})
    actions = [
        determine_action(
            hass.states.get("climate." + area + "_thermostat").attributes[
                "temperature"
            ],
            hass.states.get(devices["temperature"]).state,
            central_hvac_mode,
        )
        for area, devices in areas.items()
    ]
    thermostat_action = ACTIVE if ACTIVE in actions else IDLE
    for area, devices in areas.items():
        area_thermostat = hass.states.get("climate." + area + "_thermostat")
        area_target_temperature = area_thermostat.attributes["temperature"]
        area_temperature_sensor = hass.states.get(devices["temperature"])
        area_actual_temperature = area_temperature_sensor.state
        service_to_call = determine_cover_service_to_call(
            area_target_temperature,
            area_actual_temperature,
            central_hvac_mode,
            thermostat_action,
        )
        for cover in devices["covers"]:
            hass.services.call(
                Platform.COVER, service_to_call, service_data={ATTR_ENTITY_ID: cover}
            )

    hass.services.call(
        Platform.CLIMATE,
        SERVICE_SET_TEMPERATURE,
        service_data={
            ATTR_ENTITY_ID: central_thermostat_entity_id,
            ATTR_TEMPERATURE: determine_change_in_temperature(
                central_thermostat_actual_temperature,
                central_hvac_mode,
                thermostat_action,
            ),
        },
    )


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up HVAC Zoning from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    def handle_event(event):
        event_dict = event.as_dict()
        event_type = event_dict["event_type"]
        data = event_dict["data"]
        entity_id = data["entity_id"]
        config_entry_data = config_entry.as_dict()["data"]
        config_entry_data_with_only_valid_areas = filter_to_valid_areas(
            config_entry_data
        )
        areas = config_entry_data_with_only_valid_areas.get("areas", {})
        cover_entity_ids = get_all_cover_entity_ids(areas)
        temperature_entity_ids = get_all_temperature_entity_ids(areas)
        thermostat_entity_ids = get_all_thermostat_entity_ids(config_entry_data)
        virtual_thermostat_entity_ids = [
            "climate." + area + "_thermostat" for area in areas
        ]
        entity_ids = (
            cover_entity_ids
            + temperature_entity_ids
            + thermostat_entity_ids
            + virtual_thermostat_entity_ids
        )
        if event_type == EVENT_STATE_CHANGED and entity_id in entity_ids:
            adjust_house(hass, config_entry)
            LOGGER.info(
                f"\nentity_id: {data['entity_id']}"
                + (f"\nold_state: {data['old_state']}" if "old_state" in data else "")
                + (f"\nnew_state: {data['new_state']}" if "new_state" in data else "")
                + "\n--------------------------------------------------------"
            )

    hass.bus.async_listen(EVENT_STATE_CHANGED, handle_event)
    return True
