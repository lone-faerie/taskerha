"""Support for refreshing Tasker data"""
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import (
    TaskerEntity,
    TaskerDataUpdateCoordinator,
)
from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TaskerRefreshButton(coordinator)])
    
class TaskerRefreshButton(TaskerEntity, ButtonEntity):
    
    def __init__(self,
        coordinator: TaskerDataUpdateCoordinator
    ) -> None:
        super().__init__(coordinator, "Refresh")
        
    @property
    def entity_registry_enabled_default(self):
        return True
        
    @property
    def icon(self) -> str:
        return "mdi:refresh"
        
    async def async_press(self) -> None:
        await self.coordinator.async_refresh()