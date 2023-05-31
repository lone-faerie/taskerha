"""Support for Tasker statistics."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    ATTR_NAME,
    ATTR_SW_VERSION,
    CONF_COMMAND,
    CONF_NAME,
    CONF_USERNAME,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    async_get_current_platform,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .taskerapi.const import (
    ATTR_PROFILES,
    ATTR_TASKS,
    ATTR_SCENES,
    ATTR_GLOBALS,
    ATTR_ACTIVE,
    ATTR_PAR1,
    TASK_BACKUP
)
from .taskerapi.tasks import (
    async_backup
)

from . import (
    TaskerEntity,
    TaskerDataUpdateCoordinator,
)
from .const import (
    DOMAIN,
 
    SERVICE_BACKUP,
    SERVICE_IMPORT_TASK,
    SERVICE_SEND_COMMAND,
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([TaskerSensor(coordinator)])
    
    platform = async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_IMPORT_TASK,
        {
            vol.Required("xml"): str,
            vol.Optional(CONF_NAME): str,
        },
        "async_import_task",
    )
    if TASK_BACKUP in coordinator.all_tasks:
        platform.async_register_entity_service(
            SERVICE_BACKUP,
            {vol.Optional(CONF_USERNAME): vol.Email()},
            "async_backup_tasker",
        )
    platform.async_register_entity_service(
        SERVICE_SEND_COMMAND,
        {vol.Required(CONF_COMMAND): cv.string},
        "async_send_command",
    )

class TaskerSensor(TaskerEntity, SensorEntity):
    
    #_attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self,
        coordinator: TaskerDataUpdateCoordinator,
    ) -> None:
        super().__init__(coordinator, None)
        
    @property
    def has_entity_name(self) -> bool:
        return False
        
    @property
    def icon(self) -> str:
        return "mdi:lightning-bolt"
        
    @property
    def native_unit_of_measurement(self) -> str:
        return "Active Profiles"
        
    @property
    def state_class(self) -> SensorStateClass:
        return SensorStateClass.MEASUREMENT
        
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        await self.coordinator.async_request_refresh()
        
    @callback
    def _handle_coordinator_update(self) -> None:
        stats = self.coordinator.data.stats
        self._attr_native_value = stats.active_profiles
        self._attr_extra_state_attributes = {
            ATTR_PROFILES: stats.total_profiles,
            ATTR_TASKS: stats.total_tasks,
            ATTR_SCENES: stats.total_scenes,
            ATTR_GLOBALS: stats.total_globals,
            ATTR_SW_VERSION: stats.version,
        }
        self.async_write_ha_state()
        
    async def async_import_task(self, xml: str, name: str | None = None):
        await self.coordinator.client.async_import_task(xml, name)
        
    async def async_backup_tasker(self, username: str | None = None):
        await async_backup(
            self.coordinator.client,
            username=username,
            import_task=TASK_BACKUP not in self.coordinator.all_tasks
        )
        """
        await self.coordinator.client.async_perform_task(
            TASK_BACKUP,
            {ATTR_PAR1: username} if username else {},
        )
        """
        
    async def async_send_command(self, command: str):
        await self.coordinator.client.async_send_commands(command)
        
        
        
        
        
        
        
        
        
        
        
        