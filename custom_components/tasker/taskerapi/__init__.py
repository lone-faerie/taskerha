"""Provide a package for controlling Tasker Android app"""
from dataclasses import asdict
from typing import Any, Callable, Mapping
from typing_extensions import NotRequired, Required, TypedDict
import logging
import base64

import aiohttp
from aiohttp.hdrs import METH_GET, METH_POST, METH_DELETE
import async_timeout
import orjson
import xmltodict

from .const import (
    ATTR_DISPLAY_AS,
    ATTR_VALUE,
    DEFAULT_PORT,
    AUTH_PATH,
    AUTH_REFRESH_PATH,
    STATS_PATH,
    PROFILES_PATH,
    TASKS_PATH,
    SCENES_PATH,
    GLOBALS_PATH,
    COMMANDS_PATH,
    IMPORT_PATH,
    FILE_PATH,
    TIMEOUT,
    #TaskerStructure,
    #TaskerStats,
    #TaskerProfile,
    #TaskerTask,
    #TaskerScene,
    #TaskerGlobal,
)
from .exceptions import (
    TaskerError,
    TaskerAuthError,
)
from .helpers import (
    csv_to_dict,
    maybe_cast,
    parse_tasker_output,
    rename_tasker_xml,
)
from .typing import (
    TaskerStructure,
    TaskerStats,
    TaskerProfile,
    TaskerTask,
    TaskerScene,
    TaskerGlobal,
    TaskerGlobalDecoded,
    TaskerGlobalEncoded,
)

ATTR_CONNECTIONS = "connections"
ATTR_IDENTIFIERS = "identifiers"

_LOGGER = logging.getLogger(__name__)

NewSessionCallback = Callable[..., aiohttp.ClientSession]

class TaskerClient:
    """Tasker client class"""
    def __init__(self,
        host: str,
        port: int = DEFAULT_PORT,
        api_key: str | None = None, *,
        session_fn: NewSessionCallback = aiohttp.ClientSession,
        **kwargs
    ):
        """Initialize the client"""
        self._host: str = host
        self._port: int = port
        self._api_key: str | None = api_key
        
        self.session_fn: NewSessionCallback = session_fn
        self.session_kwargs = kwargs
        
    @property
    def host(self):
        """Return client host"""
        return self._host
        
    @property
    def port(self):
        """Return client port"""
        return self._port
        
    @property
    def api_key(self):
        """Return client api key"""
        return self._api_key or None
        
    async def _async_request(self,
        session: aiohttp.ClientSession,
        method: str,
        path: str,
        timeout: int = TIMEOUT,
        **kwargs,
    ) -> aiohttp.ClientResponse:
        """Make an api request"""
        async with async_timeout.timeout(timeout):
            url = f"http://{self._host}:{self._port}{path}"
            headers = {"Connection": "keep-alive"}
            if self.api_key:
                headers.update({"Authorization": self.api_key})
            if "headers" in kwargs:
                headers.update(kwargs.pop("headers"))
            
            if method == METH_GET:
                resp = await session.get(url, headers=headers, **kwargs)
            elif method == METH_POST:
                resp = await session.post(url, headers=headers, **kwargs)
            elif method == METH_DELETE:
                resp = await session.delete(url, headers=headers, **kwargs)
            else:
                # resp = await session.request(method, url, **kwargs)
                raise TaskerError(f"Unsupported HTTP method {method}")
        try:
            resp.raise_for_status()
        except aiohttp.ClientResponseError as e:
            if e.status == 401:
                raise TaskerAuthError("Unauthorized") from e
            else:
                raise
        # _LOGGER.warning(f"{resp.status} {str(resp.headers)}")
        return resp
        
    async def _async_request_json(self,
        method: str,
        path: str,
        timeout: int = TIMEOUT,
        **kwargs,
    ) -> Any:
        """Make an api request and return json"""
        async with self.session_fn(**self.session_kwargs) as session:
            resp = await self._async_request(
                session,
                method,
                path,
                timeout,
                **kwargs
            )
            return await resp.json(content_type=None)
            
    async def _async_request_structured(self,
        method: str,
        path: str,
        timeout: int = TIMEOUT,
        **kwargs
    ) -> Any | str:
        """Make api request and return Tasker structure"""
        async with self.session_fn(**self.session_kwargs) as session:
            resp = await self._async_request(
                session,
                method,
                path,
                timeout,
                **kwargs
            )
            try:
                return await resp.json(content_type=None)
            except:
                text = await resp.text()
                try:
                    return xmltodict.parse(text)
                except:
                    try:
                        return csv_to_dict(text)
                    except:
                        return text
            
    async def _async_request_bytes(self,
        method: str,
        path: str,
        timeout: int = TIMEOUT,
        **kwargs
    ) -> tuple[bytes, str]:
        """Make an api request and return bytes and encoding"""
        async with self.session_fn(**self.session_kwargs) as session:
            resp = await self._async_request(
                session,
                method,
                path,
                timeout,
                **kwargs
            )
            return await resp.read(), resp.get_encoding()
    
    @staticmethod
    def _named_body(name, **kwargs) -> dict[str, Any]:
        """Return a body with 'name' attribute"""
        return {
            "name": name,
        } if None in kwargs.values() else {
            "name": name,
            **kwargs,
        }
    
    async def async_auth(self, refresh: bool = False) -> bool:
        """Authorize the client connection"""
        try:
            url = f"http://{self.host}:{self.port}{AUTH_PATH}"
            params = None
            headers = {"Connection": "keep-alive"}
            if refresh and self.api_key:
                url += f"/refresh"
                params = {"token": self.api_key}
                headers["Authorization"] = self.api_key
                
            async with self.session_fn(**self.session_kwargs) as session:
                async with async_timeout.timeout(TIMEOUT):
                    resp = await session.get(
                        url, params=params, headers=headers
                    )
                resp.raise_for_status()
                data = await resp.json(content_type=None)
                self._api_key = data.get("key", self.api_key)
            #resp = await self._async_request_json(**kwargs)
        except Exception as e:
            raise TaskerAuthError("Failed to authorize") from e
        #self._api_key = resp.get("key") if resp else None
        if self.api_key is None:
            raise TaskerAuthError("api_key is None")
        return True
    
    async def async_get_stats(self) -> TaskerStats:
        """Get Tasker statistics"""
        return TaskerStats(
            **await self._async_request_json(
                METH_GET,
                STATS_PATH
            )
        )
    
    async def async_get_profiles(
        self, names: list[str] | None = None
    ) -> list[TaskerProfile]:
        """Get a list of Tasker profiles"""
        return [
            TaskerProfile(**p) for p in
            await self._async_request_json(
                METH_GET,
                PROFILES_PATH,
                params={"name": names} if names else None,
            )
        ]
    
    async def async_get_profile(
        self, name: str
    ) -> TaskerProfile | None:
        """Get a Tasker profile"""
        ret = await self.async_get_profiles([name])
        return ret[0] if ret else None
        
    async def async_set_profiles(
        self, names: list[str], states: list[bool | None]
    ) -> list[dict[str, Any]] | None:
        return await self._async_request_json(
            METH_POST,
            PROFILES_PATH,
            json=[
                asdict(TaskerProfile(name=n, enabled=s))
                for (n, s) in zip(names, states)
            ],
        )
    
    async def async_set_profile(
        self, name: str, state: bool | None = None
    ) -> dict[str, Any] | None:
        """Set a Tasker profile"""
        return TaskerProfile(
            **await self._async_request_json(
                METH_POST,
                PROFILES_PATH,
                json=asdict(TaskerProfile(name, enabled=state)),
            )
        )
        
    async def async_get_tasks(
        self, names: list[str] | None = None
    ) -> list[TaskerTask] | None:
        """Get a list of Tasker tasks"""
        return [
            TaskerTask(**t) for t in
            await self._async_request_json(
                METH_GET,
                TASKS_PATH,
                params={"name": names} if names else None,
            )
        ]
    
    async def async_get_task(
        self, name:str
    ) -> TaskerTask | None:
        """Get a Tasker task"""
        ret = await self.async_get_tasks([name])
        return ret[0] if ret else None
        
    #async def async_perform_tasks(
    #    self, names: list[str], *args: dict[str, Any]
    #) -> list[dict[str, Any] | None] | None:
    #    return await self._async_request_json(
    #        METH_POST,
    #        TASKS_PATH,
    #        json=[
    #            self._named_body(n, variables=kwa)
    #            for (n, kwa) in zip(names, args)
    #        ],
    #    )
        
    async def async_perform_task(
        self,
        name: str,
        structure_output: bool = True,
        kwargs={},
        timeout: int = TIMEOUT,
    ) -> TaskerStructure:
        """Perform a Tasker task"""
        data, encoding = await self._async_request_bytes(
            METH_POST,
            TASKS_PATH,
            timeout=max(timeout, TIMEOUT),
            json=self._named_body(
                name,
                structure_output=structure_output,
                variables=kwargs,
            ),
        )
        return parse_tasker_output(data, encoding, structure_output)
        
    async def _async_perform_task(
        self, name: str, structure_output: bool = True, **kwargs
    ) -> TaskerStructure:
        request_fn = (
            self._async_request_structured
            if structure_output else
            self._async_request_bytes
        )
        ret = await request_fn(
            METH_POST,
            TASKS_PATH,
            json=self._named_body(
                name,
                structure_output=structure_output,
                variables=kwargs
            )
        )
        return ret if structure_output else ret[0].decode(ret[1])
        """
        if structure_output:
            return await self._async_request_structured(
                METH_POST,
                TASKS_PATH,
                json=self._named_body(
                    name,
                    structure_output=True,
                    variables=kwargs
                ),
            )
        else:
            ret = await self._async_request_bytes(
                METH_POST,
                TASKS_PATH,
                json=self._named_body(
                    name,
                    structure_output=False,
                    variables=kwargs
                )
            )
            return ret[0].decode(ret[1])
        """
        
    async def async_get_scenes(
        self, names: list[str] | None = None
    ) -> list[TaskerScene] | None:
        """Get a list of Tasker scenes"""
        return [
            TaskerScene(**s) for s in
            await self._async_request_json(
                METH_GET,
                SCENES_PATH, 
                params={"name": names} if names else None,
            )
        ]
    
    async def async_get_scene(
        self, name: str
    ) -> TaskerScene | None:
        """Get a Tasker scene"""
        ret = await self.async_get_scenes([name])
        return ret[0] if ret else None
        
    async def async_set_scenes(
        self, names: list[str], states: list[str | None]
    ) -> list[dict[str, Any]] | None:
        """Set a list of Tasker scenes"""
        return await self._async_request_json(
            METH_POST,
            SCENES_PATH,
            json=[
                self._named_body(n, action=s)
                for (n, s) in zip(names, states)
            ],
        )
    
    async def async_set_scene(
        self,
        name: str,
        action: str | None = None,
        display_as: str | None = None,
    ) -> dict[str, Any] | None:
        """Set a Tasker scene"""
        body = self._named_body(name, action=action)
        if display_as is not None:
            body[ATTR_DISPLAY_AS] = display_as
        return TaskerScene(
            **await self._async_request_json(
                METH_POST,
                SCENES_PATH,
                json=body,
            )
        )
    
    async def async_get_globals(
        self, names: list[str] | None = None, structure_outputs: bool = True
    ) -> list[TaskerGlobal] | None:
        """Get a list of Tasker globals"""
        global_vars = [
            TaskerGlobalDecoded(**g) for g in
            await self._async_request_json(
                METH_GET,
                GLOBALS_PATH, 
                params={"name": names} if names else None,
            )
        ]
        if structure_outputs:
            for g in global_vars:
                g.value_json = parse_tasker_output(g.value)
            
        return global_vars
    
    async def async_get_global(
        self, name: str, structure_output: bool = True
    ) -> TaskerGlobal | None:
        """Get a Tasker global"""
        ret = await self.async_get_globals([name], structure_output)
        return ret[0] if ret else None
        
    async def async_set_globals(
        self,
        names: list[str],
        values: list[str | None],
        structure_outputs: bool = True,
    ) -> list[TaskerGlobal] | None:
        """Set a list of Tasker globals"""
        global_vars = [
            TaskerGlobalDecoded(**g) for g in
            await self._async_request_json(
                METH_POST,
                GLOBALS_PATH,
                json=[
                    asdict(TaskerGlobalEncoded(n, v))
                    for (n, v) in zip(names, values)
                ],
            )
        ]
        if structure_outputs:
            for g in global_vars:
                g.value_json = parse_tasker_output(g.value)
                
        return global_vars
    
    async def async_set_global(
        self, name: str,
        value: str | None = None,
        structure_output: bool = True
    ) -> TaskerGlobal | None:
        """Set a Tasker global"""
        g = TaskerGlobalDecoded(
            **await self._async_request_json(
                METH_POST,
                GLOBALS_PATH,
                json=asdict(TaskerGlobalEncoded(name, value)),
            )
        )
        if structure_output:
            g.value_json = parse_tasker_output(g.value)
        
    async def async_get_commands(self, clear: bool = True) -> list[str]:
        """Get a list of Tasker commands"""
        return await self._async_request_json(
            METH_GET,
            COMMANDS_PATH,
            params={"clear": "true" if clear else "false"},
        ) or []
    
    async def async_send_commands(self, *commands: str) -> int:
        """Send a list of Tasker commands"""
        return (await self._async_request_json(
            METH_POST,
            COMMANDS_PATH,
            json=commands,
        )).get("count", -1)
    
    async def async_import_task(
        self, data: str, name: str | None = None
    ) -> dict[str, Any] | None:
        """Import a task into Tasker"""
        return await self._async_request_json(
            METH_POST,
            IMPORT_PATH,
            data=rename_tasker_xml(name, data) if name else data,
        )
        
    async def async_get_file(
        self, path: str
    ) -> tuple[bytes, str]:
        """Get a file from the Tasker device"""
        return await self._async_request_bytes(
            METH_POST,
            f"{FILE_PATH}/{path}",
        )
        
    async def async_delete_file(
        self, path: str
    ) -> None:
        """Delete a file from the Tasker device"""
        async with self.session_fn() as session:
            await self._async_request(
                session,
                METH_DELETE,
                f"{FILE_PATH}/{path}",
            )
        
    async def async_device_info(
        self, import_task: bool | None = None
    ) -> dict[str, Any] | None:
        """Get Tasker device info"""
        if import_task is None:
            import_task = not await self.async_get_task(TASK_DEVICE_INFO)
        if import_task:
            from .xml import XML_DEVICE_INFO
            await self.async_import_task(XML_DEVICE_INFO)
        info = await self.async_perform_task(TASK_DEVICE_INFO)
        if not info:
            raise ValueError(f"Expected dict for device info. Got {info}")
        if (conns := info.get(ATTR_CONNECTIONS)):
            info[ATTR_CONNECTIONS] = {tuple(c) for c in conns}
        if (ids := info.get(ATTR_IDENTIFIERS)):
            info[ATTR_IDENTIFIERS] = {tuple(i) for i in ids}
        return info
        