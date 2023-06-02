"""Support for Tasker tasks."""
from __future__ import annotations

from typing import Any
import logging

import voluptuous as vol

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_NAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import template
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    async_get_current_platform,
)
from homeassistant.helpers.json import json_dumps
from homeassistant.helpers.typing import TemplateVarsType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.util.json import JsonArrayType, JsonObjectType

from . import (
    TaskerEntity,
    TaskerDataUpdateCoordinator,
)
from .const import (
    DOMAIN,
    ATTR_TASKS,
    ATTR_RUNNING,
    ATTR_LAST_RETURN,
    ATTR_PAR1,
    ATTR_PAR2,
    ATTR_VARIABLES,
    ATTR_STRUCTURE_OUTPUT,
    SERVICE_PERFORM_TASK,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities(
        TaskerTaskBinarySensor(coordinator, name)
        for name in coordinator.all_tasks
    )
    
    platform = async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_PERFORM_TASK,
        {
            vol.Optional(ATTR_PAR1): cv.string,
            vol.Optional(ATTR_PAR2): cv.string,
            vol.Optional(
                ATTR_VARIABLES
            ): cv.schema_with_slug_keys(str),
            vol.Required(ATTR_STRUCTURE_OUTPUT, default=True): bool,
        },
        "async_perform"
    )

class TaskerTaskBinarySensor(TaskerEntity, BinarySensorEntity):
    """Representation of a Sensor."""
    
    def __init__(self,
        coordinator: TaskerDataUpdateCoordinator,
        name: str,
    ) -> None:
        super().__init__(coordinator, name)
        
        self._last_return = None
        self._last_return_is_json: bool = False
        
    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.RUNNING
        
    @property
    def icon(self) -> str:
        return "mdi:format-list-numbered"
        
    @callback
    def _handle_coordinator_update(self) -> None:
        if data := self.coordinator.data.tasks.get(self.name):
            self._attr_is_on = data.running
            self.async_write_ha_state()
        elif self.name not in self.coordinator.data.tasks_to_add:
            self.hass and self.hass.async_add_job(self.async_remove)
            
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.coordinator.enabled_tasks.add(self.name)
        if self.coordinator.data:
            self.coordinator.data.tasks_to_add.discard(self.name)
            
    async def async_will_remove_from_hass(self):
        await super().async_will_remove_from_hass()
        self.coordinator.enabled_tasks.discard(self.name)
            
    @property
    def last_return(self):
        return self._last_return
            
    @property
    def last_return_is_json(self) -> bool:
        return self._last_return_is_json
            
    @property
    def extra_state_attributes(self):
        return {
            ATTR_LAST_RETURN: self.last_return
        }
    
    async def async_perform(self,
        par1: str | None = None,
        par2: str | None = None,
        variables: dict[str, Any] = {},
        structure_output: bool = True,
    ) -> None:
        if par1:
            variables.setdefault(ATTR_PAR1, par1)
        if par2:
            variables.setdefault(ATTR_PAR2, par2)
        resp = await self.coordinator.client.async_perform_task(
            self.name,
            structure_output,
            variables,
        )
        if resp is not None:
            if structure_output and (
                type(resp) is JsonArrayType or
                type(resp) is JsonObjectType
            ):
                self._last_return = json_dumps(resp)
                self._last_return_is_json = True
            else:
                self._last_return = resp
                self._last_return_is_json = False
            self.async_write_ha_state()
        
        
        
        
        
        
        