"""Support for Tasker Android app"""
from typing import Any
import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_CONNECTIONS,
    ATTR_DEFAULT_NAME,
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_SW_VERSION,
    CONF_API_KEY,
    CONF_AUTHENTICATION,
    CONF_COMMAND,
    CONF_HOST,
    CONF_NAME,
    CONF_PARAMS,
    CONF_PORT,
    CONF_PREFIX,
    CONF_SCAN_INTERVAL,
    CONF_VARIABLES,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    format_mac,
)
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .taskerapi import TaskerClient, tasks
from .taskerapi.const import (
    ATTR_ANDROID_ID,
    ATTR_MAC_ADDRESS,
    ATTR_ACTIVE,
    ATTR_ENABLED,
    ATTR_PROFILES,
    ATTR_TASKS,
    ATTR_SCENES,
    ATTR_GLOBALS,
    TASK_DEVICE_INFO,
)
from .taskerapi.exceptions import TaskerAuthError
from .taskerapi.typing import (
    TaskerStats,
    TaskerProfile,
    TaskerTask,
    TaskerScene,
    TaskerGlobal,
)

from .const import (
    DOMAIN,
    ATTR_DEVICE_INFO,
    DEFAULT_NAME,
    SCAN_INTERVAL,
    TASKER_COMMAND,
)

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
]

_LOGGER = logging.getLogger(__name__)

"""
async def async_tasker_device(
    client: TaskerClient, *,
    name: str | None = None,
    import_task: bool | None = None
) -> tuple[DeviceInfo | None, str | None]:
    task = await client.async_get_task(TASK_DEVICE_INFO)
    # _LOGGER.warning(str(task))
    if import_task or (
        import_task is None and
        not task
    ):
        _LOGGER.warning("Importing Device Info Task")
        from .taskerapi.xml import XML_DEVICE_INFO
        await client.async_import_task(XML_DEVICE_INFO)
    unique_id = None
    info = None
    #_LOGGER.warning("Performing Device Info")
    resp = await client.async_perform_task(TASK_DEVICE_INFO)
    if resp:
        info = resp
    
    if info:
        if (cons := info.get(ATTR_CONNECTIONS)):
            #info[ATTR_CONNECTIONS] = {tuple(c) for c in cons}
            unique_id = format_mac(info[ATTR_CONNECTIONS][0][1])
            info[ATTR_CONNECTIONS] = {tuple(c) for c in cons}
        if (ids := info.get(ATTR_IDENTIFIERS)):
            #info[ATTR_IDENTIFIERS] = {(DOMAIN, i) for i in ids}
            unique_id = info[ATTR_IDENTIFIERS][0][1]
            info[ATTR_IDENTIFIERS] = {(DOMAIN, i) for i in ids}
        info[ATTR_DEFAULT_NAME] = DEFAULT_NAME
        if name:
            info[ATTR_NAME] = name
        
    return info, unique_id
"""

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Tasker platform."""
    try:
        hass.data.setdefault(DOMAIN, {})
    
        scan_interval = timedelta(
            seconds=entry.options.get(
                CONF_SCAN_INTERVAL,
                entry.data.get(
                    CONF_SCAN_INTERVAL,
                    SCAN_INTERVAL,
                )
            )
        )
        
        entry.async_on_unload(entry.add_update_listener(async_update_options))
        
        coordinator = TaskerDataUpdateCoordinator(hass, entry, scan_interval)
        await coordinator.async_config_entry_first_refresh()
        
        @callback
        def tasker_commands_listener():
            for cmd in coordinator.data.commands:
                cmd_split = cmd.split("=:=")
                hass.bus.async_fire(
                    TASKER_COMMAND,
                    {
                        CONF_COMMAND: cmd,
                        CONF_PREFIX: cmd_split[0],
                        CONF_PARAMS: cmd_split[1:]
                    }
                )
        if entry.options.get(CONF_COMMAND, True):
            entry.async_on_unload(
                coordinator.async_add_listener(tasker_commands_listener)
            )
        
        #_LOGGER.warning(coordinator.device_info)
    
        hass.data[DOMAIN][entry.entry_id] = coordinator
    
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        hass.data[DOMAIN][entry.entry_id].async_update_listeners()
    except Exception as e:
        _LOGGER.error("Error setting up entry: %s", e)
        raise e

    return True
    
async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Update a config entry's options."""
    await hass.config_entries.async_reload(entry.entry_id)
    
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    ):
        coordinator = hass.data[DOMAIN][entry.entry_id]
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

class TaskerEntity(CoordinatorEntity):
    """Base Tasker entity class"""
    def __init__(self,
        coordinator: 'TaskerDataUpdateCoordinator',
        name: str | None,
        init_data: Any = None,
    ) -> None:
        super().__init__(coordinator, context=name)
        
        self._attr_name = name or coordinator.entry.data[CONF_NAME]
        self._attr_unique_id = coordinator.entry.unique_id
        if name:
            self._attr_unique_id += "_" + cv.slugify(name)
        #self._attr_device_info = coordinator.device_info
        
        #if init_data:
        #    self._handle_update(init_data, False)
    
    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info
    
    @property
    def entity_registry_enabled_default(self) -> bool:
        return not self.has_entity_name
        
    @property
    def has_entity_name(self) -> bool:
        return True
        
def _validate_info(device_info) -> bool:
    return device_info and (
        ATTR_IDENTIFIERS in device_info or
        ATTR_CONNECTIONS in device_info
    )
    
class TaskerData:
    """Class representing data from update coordinator"""
    def __init__(self, stats: TaskerStats):
        self.stats: TaskerStats = stats
        
        self.commands: list[str] = []
        
        self.profiles: dict[str, TaskerProfile] = {}
        self.tasks: dict[str, TaskerTask] = {}
        self.scenes: dict[str, TaskerScene] = {}
        self.globals: dict[str, TaskerGlobal] = {}
        
        if False:
            self.profiles_to_add = prev.profiles_to_add
            self.tasks_to_add = prev.tasks_to_add
            self.scenes_to_add = prev.scenes_to_add
            self.globals_to_add = prev.globals_to_add
        else:
            self.profiles_to_add: set[str] = set()
            self.tasks_to_add: set[str] = set()
            self.scenes_to_add: set[str] = set()
            self.globals_to_add: set[str] = set()
        
    def __bool__(self) -> bool:
        return bool(
            self.profiles or self.profiles_to_add or
            self.tasks or self.tasks_to_add or
            self.scenes or self.scenes_to_add or
            self.globals or self.globals_to_add
        )
        
    def has_profile(self, name: str) -> bool:
        return name in self.profiles or name in self.profiles_to_add
        
    def has_task(self, name: str) -> bool:
        return name in self.tasks or name in self.tasks_to_add
        
    def has_scene(self, name: str) -> bool:
        return name in self.scenes or name in self.scenes_to_add
        
    def has_global(self, name: str) -> bool:
        return name in self.globals or name in self.globals_to_add

class TaskerDataUpdateCoordinator(DataUpdateCoordinator):
    """Tasker data update coordinator"""
    def __init__(self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        scan_interval: timedelta = SCAN_INTERVAL,
    ) -> None:
        self.entry = entry
        #self.builtins: set[str] = set(entry.options.get(CONF_VARIABLES, []))
        
        @callback
        def create_session(**kwargs):
            return async_create_clientsession(hass, False)
        self.client = TaskerClient(
            entry.data[CONF_HOST],
            entry.data[CONF_PORT],
            entry.data.get(CONF_API_KEY)
                if entry.data.get(CONF_AUTHENTICATION) else None,
            #session_fn=create_session
        )
        
        self.all_profiles: set[str] = set()
        self.all_tasks: set[str] = set()
        self.all_scenes: set[str] = set()
        self.all_globals: set[str] = set()
        
        self.enabled_profiles: set[str] = set()
        self.enabled_tasks: set[str] = set()
        self.enabled_scenes: set[str] = set()
        self.enabled_globals: set[str] = set()
        self.builtin_globals: set[str] = set(
            entry.options.get(CONF_VARIABLES, [])
        )
        
        self._fetch_all: bool = True
        self._device_info: DeviceInfo | None = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )
        
    @property
    def device_info(self) -> DeviceInfo | None:
        return self._device_info
        
    async def async_config_entry_first_refresh(self):
        try:
            await self.async_fetch_all()
            await self.async_device_info(self.entry.data.get(ATTR_NAME))
        except TaskerAuthError as e:
            _LOGGER.exception("Error authorizing Tasker API")
            self.last_update_success = False
            raise ConfigEntryAuthFailed(e) from e
        except Exception as e:
            _LOGGER.exception("Error on first refresh")
            self.last_update_success = False
            ex = ConfigEntryNotReady("Error on first refresh")
            ex.__cause__ = e
            raise ex
        await super().async_config_entry_first_refresh()
        
    async def _async_update_data(self):
        try:
            _LOGGER.info("Fetching Tasker stats")
            stats = await self.client.async_get_stats()
            data: TaskerData = TaskerData(stats)
            
            if self.entry.options.get(CONF_COMMAND):
                _LOGGER.info("Fetching Tasker commands")
                data.commands = await self.client.async_get_commands()
            
            if self.enabled_profiles:
                _LOGGER.info("Fetching Tasker profiles")
                profiles = await self.client.async_get_profiles(
                    list(self.enabled_profiles)
                )
                data.num_active_profiles = sum(
                    p.active for p in profiles
                )
                data.profiles = {
                    p.name: p for p in profiles
                    if p.name in self.enabled_profiles
                } if profiles is not None else (
                    self.data.profiles if self.data else {}
                )
                """
                data.profiles_to_add.update([
                    name for name in data.profiles if name not in self.data.profiles
                ] if self.data else data.profiles.keys())
                """
            
            if self.enabled_tasks:
                _LOGGER.info("Fetching Tasker tasks")
                tasks = await self.client.async_get_tasks(
                    list(self.enabled_tasks)
                )
                data.tasks = {
                    t.name: t for t in tasks
                } if tasks is not None else (
                    self.data.tasks if self.data else {}
                )
                """
                data.tasks_to_add.update([
                    name for name in data.tasks if name not in self.data.tasks
                ] if self.data else data.tasks.keys())
                """
            
            if self.enabled_scenes:
                _LOGGER.info("Fetching Tasker scenes")
                scenes = await self.client.async_get_scenes(
                    list(self.enabled_scenes)
                )
                data.scenes = {
                    s.name: s for s in scenes
                } if scenes is not None else (
                    self.data.scenes if self.data else {}
                )
                """
                data.scenes_to_add.update([
                    name for name in data.scenes if name not in self.data.scenes
                ] if self.data else data.scenes.keys())
                """
            if self.enabled_globals:
                _LOGGER.info("Fetching Tasker globals")
                global_vars = await self.client.async_get_globals(
                    list(self.enabled_globals)
                )
                data.globals = {
                    g.name: g for g in global_vars
                } if global_vars is not None else (
                    self.data.globals if self.data else {}
                )
                """
                data.globals_to_add.update([
                    name for name in data.globals if name not in self.data.globals
                ] if self.data else data.globals.keys())
                """
                
            return data
        except UpdateFailed as e:
            _LOGGER.exception("Update Failed: %s", e)
            raise e
        except Exception as e:
            _LOGGER.exception("Error fetching data: %s", e)
            raise UpdateFailed() from e
            
    async def async_fetch_all(self):
        self.all_profiles: set[str] = set(
            p.name for p in await self.client.async_get_profiles() or []
        )
        self.all_tasks: set[str] = set(
            t.name for t in await self.client.async_get_tasks() or []
        )
        self.all_scenes: set[str] = set(
            s.name for s in await self.client.async_get_scenes() or []
        )
        self.all_globals: set[str] = set(
            g.name for g in await self.client.async_get_globals() or []
        )
        
    async def async_device_info(self, name: str | None = None) -> DeviceInfo | None:
        _LOGGER.info("Fetching device info")
        device = await tasks.async_device_info(
            self.client,
            name=name or self.entry.data.get(CONF_NAME, name),
            import_task=TASK_DEVICE_INFO not in self.all_tasks,
        )
        #if not _validate_info(info) or not uid:
        #    raise ValueError("Could not get device info")
        self._device_info = DeviceInfo(
            identifiers={(DOMAIN, device[ATTR_ANDROID_ID])},
            manufacturer=device[ATTR_MANUFACTURER],
            model=device[ATTR_MODEL],
            sw_version=device[ATTR_SW_VERSION],
            default_name=DEFAULT_NAME,
        )
        if ATTR_MAC_ADDRESS in device:
            self._device_info[ATTR_CONNECTIONS] = {
                (CONNECTION_NETWORK_MAC, device[ATTR_MAC_ADDRESS])
            }
        if name:
            self._device_info[ATTR_NAME] = name