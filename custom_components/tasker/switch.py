"""Support for Tasker profiles"""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_NAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .taskerapi.const import (
    ATTR_PROFILES,
    ATTR_ENABLED,
    ATTR_ACTIVE,
)
from .taskerapi.typing import TaskerProfile

from . import TaskerEntity
from .const import (
    DOMAIN,
)



async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities(
        TaskerProfileSwitch(coordinator, name)
        for name in coordinator.all_profiles
    )
    

class TaskerProfileSwitch(TaskerEntity, SwitchEntity):
    
    @callback
    def _handle_update(self, data) -> None:
        self._attr_is_on = data.enabled
        self._attr_extra_state_attributes = {
            ATTR_ACTIVE: data.active
        }
        self.async_write_ha_state()
    
    @callback
    def _handle_coordinator_update(self) -> None:
        if data := self.coordinator.data.profiles.get(self.name):
            """
            self._attr_is_on = data.get(ATTR_ENABLED, False)
            self._attr_extra_state_attributes = {
                ATTR_ACTIVE: data.get(ATTR_ACTIVE, False)
            }
            self.async_write_ha_state()
            """
            self._handle_update(data)
        """
        elif self.name not in self.coordinator.data.profiles_to_add:
            self.hass and self.hass.async_add_job(self.async_remove)
        """
        
    @property
    def icon(self) -> str:
        return "mdi:circle-opacity"
        
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.coordinator.enabled_profiles.add(self.name)
        if self.coordinator.data:
            self.coordinator.data.profiles_to_add.discard(self.name)
        
    async def async_will_remove_from_hass(self):
        await super().async_will_remove_from_hass()
        self.coordinator.enabled_profiles.discard(self.name)
        
    async def _async_set_enabled(self, enabled: bool | None = None):
        data = await self.coordinator.client.async_set_profile(
            self.name, enabled
        )
        self._handle_update(data)
        await self.coordinator.async_request_refresh()
        
    async def async_turn_on(self, **kwargs):
        await self._async_set_enabled(True)
    
    async def async_turn_off(self, **kwargs):
        await self._async_set_enabled(False)
    
    async def async_toggle(self, **kwargs):
        await self._async_set_enabled(None)