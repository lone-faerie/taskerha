"""Support for Tasker globals"""
import logging
from xmltodict import parse as xml_parse

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_VARIABLES,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.json import json_dumps
from homeassistant.util.json import JsonArrayType, JsonObjectType

from .taskerapi.const import (
    ATTR_GLOBALS,
    ATTR_VALUE,
    BUILTIN_GLOBALS,
)

from . import (
    TaskerEntity,
    TaskerDataUpdateCoordinator
)
from .const import (
    DOMAIN,
    CONF_STRUCTURE_GLOBALS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities(
        [
            TaskerGlobalText(coordinator, name)
            for name in coordinator.all_globals
        ] + [
            TaskerBuiltinText(coordinator, name)
            for name in coordinator.builtin_globals
        ]
    )
    """
    async_add_entities(
        TaskerGlobalText(coordinator, name)
        for name in [
            *coordinator.all_globals,
            *entry.options.get(CONF_VARIABLES, [])
        ]
    )
    """

class TaskerGlobalText(TaskerEntity, TextEntity):
    
    def __init__(self,
        coordinator: TaskerDataUpdateCoordinator,
        name: str,
    ) -> None:
        super().__init__(coordinator, name)
        self._attr_native_value = ""
    
    @callback
    def _handle_update(self, data, write_state = True) -> None:
        """
        if (value := data.get(ATTR_VALUE)) is None:
            self._attr_native_value = ""
        elif type(value) is JsonArrayType or type(value) is JsonObjectType:
            self._attr_native_value = json_dumps(value)
        elif type(value) is bool:
            self._attr_native_value = str(value).lower()
        else:
            try:
                self._attr_native_value = json_dumps(xml_parse(str(value)))
            except:
                self._attr_native_value = str(value)
        """
        self._attr_native_value = str(data.value or "")
        if self.do_structure:
            self._attr_extra_state_attributes = {
                "value_json": data.value_json
            }
        if write_state:
            self.async_write_ha_state()
            
    @callback
    def _handle_coordinator_update(self) -> None:
        if data := self.coordinator.data.globals.get(self.var_name):
            self._handle_update(data)
        """
        elif self.var_name not in self.coordinator.all_globals:
            self.hass and self.hass.async_add_job(self.async_remove)
        """
    @property
    def do_structure(self) -> bool:
        return self.coordinator.entry.options.get(CONF_STRUCTURE_GLOBALS, True)
            
    @property
    def icon(self) -> str:
        return "mdi:label-outline"
        
    @property
    def native_max(self) -> str:
        return 1023
            
    @property
    def var_name(self) -> str:
        return self.name
    
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        _LOGGER.warning(f"{self.var_name} added to hass")
        self.coordinator.enabled_globals.add(self.var_name)
        if self.coordinator.data:
            self.coordinator.data.globals_to_add.discard(self.var_name)
        
    async def async_will_remove_from_hass(self):
        await super().async_will_remove_from_hass()
        self.coordinator.enabled_globals.discard(self.var_name)
        
    async def async_set_value(self, value):
        await self.coordinator.client.async_set_global(self.var_name, value)
        await self.coordinator.async_request_refresh()
        
class TaskerBuiltinText(TaskerGlobalText):
    
    def __init__(self,
        coordinator: TaskerDataUpdateCoordinator,
        name: str,
    ) -> None:
        super().__init__(coordinator, BUILTIN_GLOBALS[name])
        self._var_name: str = name
        
    @property
    def do_structure(self) -> bool:
        return False
        
    @property
    def entity_registry_enabled_default(self) -> bool:
        return True
        
    @property
    def var_name(self) -> str:
        return self._var_name
    
    async def async_set_value(self, value):
        _LOGGER.warning("Cannot set builtin Tasker globals")
        
    