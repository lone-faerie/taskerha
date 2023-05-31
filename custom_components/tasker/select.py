"""Support for Tasker scenes"""
from homeassistant.components.select import (
    SelectEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_NAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .taskerapi.const import (
    ATTR_SCENES,
    ATTR_STATUS,
    ATTR_DISPLAY_AS,
    ATTR_POSITION,
    ATTR_SIZE,
    TaskerSceneStatus,
    TaskerSceneAction,
)

from . import (
    TaskerEntity,
    TaskerDataUpdateCoordinator
)
from .const import (
    DOMAIN,
    TaskerSceneOption,
)

SCENE_OPTIONS_TO_STATUS = {
    TaskerSceneOption.DESTROYED: TaskerSceneStatus.UNCREATED,
    TaskerSceneOption.HIDDEN: TaskerSceneStatus.HIDDEN,
    TaskerSceneOption.VISIBLE: TaskerSceneStatus.VISIBLE,
}

SCENE_OPTIONS_TO_ACTIONS = {
    TaskerSceneOption.DESTROYED: TaskerSceneAction.DESTROY,
    TaskerSceneOption.HIDDEN: TaskerSceneAction.HIDE,
    TaskerSceneOption.VISIBLE: TaskerSceneAction.SHOW,
    TaskerSceneOption.OVERLAY: TaskerSceneAction.SHOW,
    TaskerSceneOption.OVERLAY_BLOCKING: TaskerSceneAction.SHOW,
    TaskerSceneOption.OVERLAY_BLOCKING_FULL: TaskerSceneAction.SHOW,
    TaskerSceneOption.DIALOG: TaskerSceneAction.SHOW,
    TaskerSceneOption.DIALOG_DIM_HEAVY: TaskerSceneAction.SHOW,
    TaskerSceneOption.DIALOG_DIM: TaskerSceneAction.SHOW,
    TaskerSceneOption.ACTIVITY: TaskerSceneAction.SHOW,
    TaskerSceneOption.ACTIVITY_NO_BAR: TaskerSceneAction.SHOW,
    TaskerSceneOption.ACTIVITY_NO_BAR_STATUS: TaskerSceneAction.SHOW,
    TaskerSceneOption.ACTIVITY_NO_BAR_STATUS_NAV: TaskerSceneAction.SHOW,
}

#SCENE_OPTIONS = list(SCENE_OPTIONS_TO_STATUS.keys())
SCENE_OPTIONS = [o.value for o in TaskerSceneOption]

SCENE_STATUS_TO_OPTIONS = {
    TaskerSceneStatus.UNCREATED: TaskerSceneOption.DESTROYED,
    TaskerSceneStatus.HIDDEN: TaskerSceneOption.HIDDEN,
    TaskerSceneStatus.VISIBLE: TaskerSceneOption.VISIBLE,
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities(
        TaskerSceneSelect(coordinator, name)
        for name in coordinator.all_scenes
    )
    

class TaskerSceneSelect(TaskerEntity, SelectEntity):
    
    def __init__(self,
        coordinator: TaskerDataUpdateCoordinator,
        name: str,
    ) -> None:
        super().__init__(coordinator, name)
        self._attr_current_option = TaskerSceneOption.DESTROYED
    
    @callback
    def _handle_update(self, data, write_state=True):
        if data.status == TaskerSceneStatus.VISIBLE:
            opt = data.display_as or (
                self.current_option if self.current_option not in [
                    TaskerSceneOption.DESTROYED, TaskerSceneOption.HIDDEN,
                ] else TaskerSceneOption.VISIBLE
            )
        else:
            opt = SCENE_STATUS_TO_OPTIONS.get(
                data.status, TaskerSceneOption.DESTROYED
            )
        if opt in SCENE_OPTIONS:
            self._attr_current_option = opt
        self._attr_extra_state_attributes = {
            ATTR_POSITION: data.position or (
                (self.extra_state_attributes or {}).get(ATTR_POSITION)
            ),
            ATTR_SIZE: data.size or (
                ATTR_SIZE,
                (self.extra_state_attributes or {}).get(ATTR_SIZE)
            )
        }
        if data and write_state:
            self.async_write_ha_state()
    
    @callback
    def _handle_coordinator_update(self) -> None:
        if data := self.coordinator.data.scenes.get(self.name):
            self._handle_update(data)
            #self._attr_current_option = SCENE_STATUS_TO_OPTIONS.get(
            #    data.get(ATTR_STATUS), "Uncreated"
            #)
            #self._attr_extra_state_attributes = {
            #    ATTR_POSITION: data.get(ATTR_POSITION),
            #    ATTR_SIZE: data.get(ATTR_SIZE),
            #}
            #self.async_write_ha_state()
        elif self.name not in self.coordinator.data.scenes_to_add:
            self.hass and self.hass.async_add_job(self.async_remove)
            
    @property
    def icon(self) -> str:
        return "mdi:image"
            
    @property
    def options(self) -> list[str]:
        return SCENE_OPTIONS
        
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.coordinator.enabled_scenes.add(self.name)
        if self.coordinator.data:
            self.coordinator.data.scenes_to_add.discard(self.name)
        
    async def async_will_remove_from_hass(self):
        await super().async_will_remove_from_hass()
        self.coordinator.enabled_scenes.discard(self.name)
        
    async def async_select_option(self, option: str) -> None:
        action = SCENE_OPTIONS_TO_ACTIONS.get(option)
        if action is None or option == self.current_option:
            return
        if option == TaskerSceneOption.VISIBLE:
            option = TaskerSceneOption.OVERLAY
        display_as = option if action == TaskerSceneAction.SHOW else None
            
        data = await self.coordinator.client.async_set_scene(
            self.name,
            action,
            display_as
        )
        self._handle_update(data)
        await self.coordinator.async_request_refresh()
        
        
        
        
        
        
        
        
        
