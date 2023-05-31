"""Helpful Tasker tasks as python functions"""
import logging
from typing import Final

from . import TaskerClient
from .const import TaskerDeviceInfo, DATA_DIR

_LOGGER = logging.getLogger(__name__)

TASK_BACKUP: Final = "Backup"
TASK_DEVICE_INFO: Final = "Device Info"
TASK_GET_VOICE: Final = "Get Voice"

XML_BACKUP = DATA_DIR / "Backup.tsk.xml"
XML_DEVICE_INFO = DATA_DIR / "Device_Info.tsk.xml"
XML_GET_VOICE = DATA_DIR / "Get_Voice.tsk.xml"

async def async_device_info(
    client: TaskerClient, *,
    name: str | None = None,
    import_task: bool | None = None
) -> TaskerDeviceInfo | None:
    """Get Tasker device info"""
    if import_task is None:
        import_task = not await client.async_get_task(TASK_DEVICE_INFO)
    # _LOGGER.warning(str(task))
    if import_task:
        _LOGGER.warning("Importing Device Info Task")
        await client.async_import_task(XML_DEVICE_INFO.read_text())
    #_LOGGER.warning("Performing Device Info")
    info = await client.async_perform_task(TASK_DEVICE_INFO)
    if name:
        info["name"] = name
    return info

async def async_backup(
    client: TaskerClient, *,
    username: str | None = None,
    import_task: bool | None = None,
) -> None:
    """Backup Tasker config"""
    if import_task is None:
        import_task = not await client.async_get_task(TASK_BACKUP)
    if import_task:
        _LOGGER.warning("Importing Backup Task")
        await client.async_import_task(XML_BACKUP.read_text())
    await client.async_perform_task(
        TASK_BACKUP,
        structure_output=False,
        kwargs={"par1": username} if username else {}
    )

async def async_get_voice(
    client: TaskerClient,
    method: str = "text",
    timeout: int = 30,
    import_task: bool | None = None, 
) -> str | bytes:
    """Get voice, either as text or audio"""
    if import_task is None:
        import_task = not await client.async_get_task(TASK_GET_VOICE)
    if import_task:
        _LOGGER.warning("Importing Get Voice Task")
        await client.async_import_task(XML_GET_VOICE.read_text())
    resp = await client.async_perform_task(
        TASK_GET_VOICE,
        structure_output=True,
        kwargs={"par1": method, "par2": timeout},
        timeout=timeout,
    )
    if method == "text" and (text := resp.get("text")):
        return text
    else:
        return (await client.async_get_file(resp["file"]))[0]
    
    
    
    
    