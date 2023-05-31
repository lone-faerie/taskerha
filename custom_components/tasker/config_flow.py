"""Config Flow to configure the Tasker integration."""
import logging
from typing import Any, Mapping
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlowWithConfigEntry,
)
from homeassistant.const import (
    CONF_API_KEY,
    CONF_AUTHENTICATION,
    CONF_COMMAND,
    CONF_DEVICE,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_VARIABLES,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import (
    BooleanSelector,
    TemplateSelector,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import format_mac

from .taskerapi import TaskerClient, tasks
from .taskerapi.const import (
    ATTR_ANDROID_ID,
    BUILTIN_GLOBALS,
    TASK_DEVICE_INFO,
)
from .taskerapi.exceptions import TaskerAuthError

#from . import async_tasker_device
from .const import (
    DOMAIN,
    CONF_STRUCTURE_GLOBALS,
    DEFAULT_NAME,
    DEFAULT_PORT,
    SCAN_INTERVAL,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Required(CONF_AUTHENTICATION, default=True): bool,
        vol.Optional(
            CONF_SCAN_INTERVAL, default=SCAN_INTERVAL,
        ): int,
    }
)

_LOGGER = logging.getLogger(__name__)

class ConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    
    VERSION = 1
    
    entry: ConfigEntry | None = None
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}
        
        if user_input is not None:
            try:
                client = TaskerClient(
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                )
                if user_input[CONF_AUTHENTICATION]:
                    await client.async_auth()
                tasker_device = await tasks.async_device_info(client)
            except TaskerAuthError as e:
                _LOGGER.error("Auth error: %s", e)
                self.async_abort(reason="auth_error")
                raise
            except Exception as e:
                _LOGGER.error("Connection error: %s", e)
                errors ["base"] = "connection_error"
                raise
            else:
                if ATTR_ANDROID_ID not in tasker_device:
                    _LOGGER.error("Could not fetch android id")
                    self.async_abort(reason="uid_error")
            
            if not errors:
                await self.async_set_unique_id(tasker_device[ATTR_ANDROID_ID])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_API_KEY: client.api_key,
                        **user_input,
                    },
                )
                
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
        
    async def async_step_reauth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        self.entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()
    
    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        assert self.entry is not None
        
        if user_input is not None:
            try:
                data = self.entry.data.copy()
                client = TaskerClient(
                    data[CONF_HOST],
                    data[CONF_PORT]
                )
                await client.async_auth()
            except TaskerAuthError as e:
                _LOGGER.error("Auth error: %s", e)
                return self.async_abort(reason="auth_error")
            except Exception as e:
                _LOGGER.error("Connection error: %s", e)
                return self.async_abort(reason="reauth_unsuccessful")
                
            if client.api_key != data[CONF_API_KEY]:
                data[CONF_API_KEY] = client.api_key
                self.hass.config_entries.async_update_entry(
                    self.entry, data=data
                )
                await self.hass.config_entries.async_reload(self.entry.entry_id)
            return self.async_abort(reason="reauth_successful")
        
        return self.async_show_form(step_id="reauth_confirm")
        
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return OptionsFlowHandler(config_entry)
        
class OptionsFlowHandler(OptionsFlowWithConfigEntry):
    
    async def async_step_init(self,
        user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        
        options_schema = vol.Schema({
            vol.Required(
                CONF_VARIABLES,
                default=self.options.get(CONF_VARIABLES, []),
            ): cv.multi_select(BUILTIN_GLOBALS),
            vol.Required(
                CONF_STRUCTURE_GLOBALS,
                default=self.options.get(
                    CONF_STRUCTURE_GLOBALS, True
                ),
            ): BooleanSelector(),
            vol.Required(
                CONF_COMMAND,
                default=self.options.get(
                    CONF_COMMAND, True
                ),
            ): BooleanSelector(),
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.data.get(
                    CONF_SCAN_INTERVAL, SCAN_INTERVAL
                )
            ): int, 
        })
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )