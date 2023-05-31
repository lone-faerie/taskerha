"""Provides device trigger for Tasker commands"""
import logging

import voluptuous as vol

from homeassistant.components.device_automation import (
    DEVICE_TRIGGER_BASE_SCHEMA,
)
from homeassistant.components.homeassistant.triggers import (
    event as event_trigger,
)
from homeassistant.const import (
    CONF_COMMAND,
    CONF_DOMAIN,
    CONF_DEVICE_ID,
    CONF_PLATFORM,
    CONF_TYPE,
)
from homeassistant.core import HomeAssistant, CALLBACK_TYPE
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, TASKER_COMMAND

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): TASKER_COMMAND,
        vol.Optional(CONF_COMMAND): str,
    }
)

async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, str]]:
    return [
        {
            CONF_PLATFORM: "device",
            CONF_DOMAIN: DOMAIN,
            CONF_DEVICE_ID: device_id,
            CONF_TYPE: TASKER_COMMAND,
        }
    ]
    
async def async_get_trigger_capabilities(
    hass: HomeAssistant, config: ConfigType
) -> dict[str, vol.Schema]:
    return {
        "extra_fields": vol.Schema(
            {
                vol.Optional(CONF_COMMAND): str,
            }
        )
    }
    
async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    event_config = {
        event_trigger.CONF_PLATFORM: "event",
        event_trigger.CONF_EVENT_TYPE: TASKER_COMMAND,
    }
    if command := config.get(CONF_COMMAND):
        event_config[event_trigger.CONF_EVENT_DATA] = {
            CONF_COMMAND: cv.matches_regex(command)
        }
    
    event_config = event_trigger.TRIGGER_SCHEMA(event_config)
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )