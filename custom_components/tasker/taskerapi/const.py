"""Constants for taskerapi"""
from typing import Any, Callable, Final
from typing_extensions import NotRequired, Required, TypedDict
from datetime import timedelta
from enum import Enum
from pathlib import Path

import aiohttp

TaskerStructure = (
    dict[str, 'TaskerStructure'] |
    list['TaskerStructure'] |
    str |
    int |
    float |
    bool |
    None
)

class TaskerStats(TypedDict):
    active_profiles: int
    total_profiles: int
    total_tasks: int
    total_scenes: int
    total_globals: int
    version: str

class TaskerProfile(TypedDict):
    name: str
    enabled: bool
    active: bool
    
class TaskerTask(TypedDict):
    name: str
    running: bool
    
class TaskerScene(TypedDict, total=False):
    name: Required[str]
    status: Required[str]
    display_as: str
    position: tuple[float, float]
    size: tuple[float, float]
    
class TaskerGlobal(TypedDict):
    name: str
    value: str
    value_json: NotRequired[TaskerStructure]
    
class TaskerDeviceInfo(TypedDict):
    android_id: str
    mac_address: NotRequired[str | None]
    manufacturer: str
    model: str
    name: NotRequired[str | None]
    sw_version: NotRequired[str | None]

class TaskerSceneStatus(str, Enum):
    UNCREATED = "uncreated"
    HIDDEN = "hidden"
    VISIBLE = "visible"
    BACKGROUND = "background"
    
class TaskerSceneAction(str, Enum):
    CREATE = "create"
    DESTROY = "destroy"
    HIDE = "hide"
    SHOW = "show"
    
class TaskerSceneOption(str, Enum):
    DESTROYED = "Destroyed"
    HIDDEN = "Hidden"
    VISIBLE = "Visible"
    
    OVERLAY = "Overlay"
    OVERLAY_BLOCKING = "Overlay, Blocking"
    OVERLAY_BLOCKING_FULL = "Overlay, Blocking, Full Window"
    DIALOG = "Dialog"
    DIALOG_DIM_HEAVY = "Dialog, Dim Behind Heavy"
    DIALOG_DIM = "Dialog, Dim Behind"
    ACTIVITY = "Activity"
    ACTIVITY_NO_BAR = "Activity, No Bar"
    ACTIVITY_NO_BAR_STATUS = "Activity, No Bar, No Status"
    ACTIVITY_NO_BAR_STATUS_NAV = "Activity, No Bar, No Status, No Nav"
    
ATTR_ANDROID_ID: Final = "android_id"
ATTR_MAC_ADDRESS: Final = "mac_address"

ATTR_PROFILES: Final = "profiles"
ATTR_TASKS: Final = "tasks"
ATTR_SCENES: Final = "scenes"
ATTR_GLOBALS: Final = "globals"

ATTR_ACTIVE: Final = "active"
ATTR_ENABLED: Final = "enabled"
ATTR_RUNNING: Final = "running"
ATTR_STATUS: Final = "status"
ATTR_DISPLAY_AS: Final = "display_as"
ATTR_POSITION: Final = "position"
ATTR_SIZE: Final = "size"
ATTR_VALUE: Final = "value"

ATTR_LAST_RETURN: Final = "last_return"

ATTR_PAR1: Final = "par1"
ATTR_PAR2: Final = "par2"
ATTR_VARIABLES: Final = "variables"
ATTR_STRUCTURE_OUTPUT: Final = "structure_output"

DEFAULT_PORT: Final = 1821

TASKER_COMMAND: Final = "tasker_command"

TIMEOUT: Final = 120

AUTH_PATH = "/api/auth"
AUTH_REFRESH_PATH = AUTH_PATH + "/refresh"
STATS_PATH = "/api/stats"
PROFILES_PATH = "/api/profiles"
TASKS_PATH = "/api/tasks"
SCENES_PATH = "/api/scenes"
GLOBALS_PATH = "/api/globals"
COMMANDS_PATH = "/api/commands"
IMPORT_PATH = "/api/import"
FILE_PATH = "/api/file"

DATA_DIR: Final = Path(__file__).parent.resolve() / "data"

TASK_BACKUP: Final = "Backup"
XML_BACKUP: Final = DATA_DIR / "Backup.tsk.xml"

TASK_DEVICE_INFO: Final = "Device Info"
XML_DEVICE_INFO: Final = DATA_DIR / "Device_Info.tsk.xml"

TASK_GET_VOICE: Final = "Get Voice"
XML_GET_VOICE: Final = DATA_DIR / "Get_Voice.tsk.xml"

"""Tasker Builtin Globals"""
GLOBAL_AIR: Final = "AIR"
GLOBAL_AIRR: Final = "AIRR"
GLOBAL_BATT: Final = "BATT"
GLOBAL_BLUE: Final = "BLUE"
GLOBAL_CPUFREQ: Final = "CPUFREQ"
GLOBAL_CPUGOV: Final = "CPUGOV"
GLOBAL_CALDESCR: Final = "CALDESCR"
GLOBAL_CALLOC: Final = "CALLOC"
GLOBAL_CALTITLE: Final = "CALTITLE"
GLOBAL_CALS: Final = "CALS"
GLOBAL_CDATE: Final = "CDATE"
GLOBAL_CODATE: Final = "CODATE"
GLOBAL_CODUR: Final = "CODUR"
GLOBAL_CTIME: Final = "CTIME"
GLOBAL_COTIME: Final = "COTIME"
GLOBAL_CONAME: Final = "CONAME"
GLOBAL_CONUM: Final = "CONUM"
GLOBAL_CNAME: Final = "CNAME"
GLOBAL_CNUM: Final = "CNUM"
GLOBAL_CELLID: Final = "CELLID"
GLOBAL_CELLSRV: Final = "CELLSRV"
GLOBAL_CELLSIG: Final = "CELLSIG"
GLOBAL_CLIP: Final = "CLIP"
GLOBAL_DATE: Final = "DATE"
GLOBAL_DAYM: Final = "DAYM"
GLOBAL_DAYW: Final = "DAYW"
GLOBAL_DEVID: Final = "DEVID"
GLOBAL_DEVMAN: Final = "DEVMAN"
GLOBAL_DEVMOD: Final = "DEVMOD"
GLOBAL_DEVPROD: Final = "DEVPROD"
GLOBAL_DEVTID: Final = "DEVTID"
GLOBAL_BRIGHT: Final = "BRIGHT"
GLOBAL_DTOUT: Final = "DTOUT"
GLOBAL_ECC: Final = "ECC"
GLOBAL_EDATE: Final = "EDATE"
GLOBAL_EFROM: Final = "EFROM"
GLOBAL_ESUBJ: Final = "ESUBJ"
GLOBAL_ETIME: Final = "ETIME"
GLOBAL_MEMF: Final = "MEMF"
GLOBAL_GPS: Final = "GPS"
GLOBAL_HTTPL: Final = "HTTPL"
GLOBAL_HTTPD: Final = "HTTPD"
GLOBAL_HTTPR: Final = "HTTPR"
GLOBAL_HEART: Final = "HEART"
GLOBAL_HUMIDITY: Final = "HUMIDITY"
GLOBAL_IMETHOD: Final = "IMETHOD"
GLOBAL_INTERRUPT: Final = "INTERRUPT"
GLOBAL_KEYG: Final = "KEYG"
GLOBAL_LAPP: Final = "LAPP"
GLOBAL_FOTO: Final = "FOTO"
GLOBAL_LIGHT: Final = "LIGHT"
GLOBAL_LOC: Final = "LOC"
GLOBAL_LOCN: Final = "LOCN"
GLOBAL_LOCACC: Final = "LOCACC"
GLOBAL_LOCNACC: Final = "LOCNACC"
GLOBAL_LOCALT: Final = "LOCALT"
GLOBAL_LOCTMS: Final = "LOCTMS"
GLOBAL_LOCNTMS: Final = "LOCNTMS"
GLOBAL_LOCSPD: Final = "LOCSPD"
GLOBAL_MFIELD: Final = "MFIELD"
GLOBAL_MTRACK: Final = "MTRACK"
GLOBAL_MUTED: Final = "MUTED"
GLOBAL_NIGHT: Final = "NIGHT"
GLOBAL_NTITLE: Final = "NTITLE"
GLOBAL_PNUM: Final = "PNUM"
GLOBAL_PRESSURE: Final = "PRESSURE"
GLOBAL_PACTIVE: Final = "PACTIVE"
GLOBAL_PENABLED: Final = "PENABLED"
GLOBAL_ROAM: Final = "ROAM"
GLOBAL_ROOT: Final = "ROOT"
GLOBAL_SDK: Final = "SDK"
GLOBAL_SIMNUM: Final = "SIMNUM"
GLOBAL_SIMSTATE: Final = "SIMSTATE"
GLOBAL_SCREEN: Final = "SCREEN"
GLOBAL_SILENT: Final = "SILENT"
GLOBAL_SPHONE: Final = "SPHONE"
GLOBAL_SPEECH: Final = "SPEECH"
GLOBAL_TRUN: Final = "TRUN"
GLOBAL_TNET: Final = "TNET"
GLOBAL_TEMP: Final = "TEMP"
GLOBAL_TETHER: Final = "TETHER"
GLOBAL_SMSRB: Final = "SMSRB"
GLOBAL_SMSRD: Final = "SMSRD"
GLOBAL_SMSRF: Final = "SMSRF"
GLOBAL_SMSRN: Final = "SMSRN"
GLOBAL_MMSRS: Final = "MMSRS"
GLOBAL_SMSRT: Final = "SMSRT"
GLOBAL_TIME: Final = "TIME"
GLOBAL_TIMEMS: Final = "TIMEMS"
GLOBAL_TIMES: Final = "TIMES"
GLOBAL_UIMODE: Final = "UIMODE"
GLOBAL_UPS: Final = "UPS"
GLOBAL_VOICE: Final = "VOICE"
GLOBAL_VOLA: Final = "VOLA"
GLOBAL_VOLC: Final = "VOLC"
GLOBAL_VOLD: Final = "VOLD"
GLOBAL_VOLM: Final = "VOLM"
GLOBAL_VOLN: Final = "VOLN"
GLOBAL_VOLR: Final = "VOLR"
GLOBAL_VOLS: Final = "VOLS"
GLOBAL_WIFII: Final = "WIFII"
GLOBAL_WIFI: Final = "WIFI"
GLOBAL_WIMAX: Final = "WIMAX"
GLOBAL_WIN: Final = "WIN"

BUILTIN_GLOBALS: Final = {
    GLOBAL_AIR: "Airplane Mode Status",
    GLOBAL_AIRR: "Airplane Radios",
    GLOBAL_BATT: "Battery Level",
    GLOBAL_BLUE: "Bluetooth Status",
    GLOBAL_CPUFREQ: "CPU Frequency",
    GLOBAL_CPUGOV: "CPU Governor",
    GLOBAL_CALDESCR: "Calendar Event Description",
    GLOBAL_CALLOC: "Calendar Event Location",
    GLOBAL_CALTITLE: "Calendar Event Title",
    GLOBAL_CALS: "Calendar List",
    GLOBAL_CDATE: "Call Date (In)",
    GLOBAL_CODATE: "Call Date (Out)",
    GLOBAL_CODUR: "Call Duration (Out)",
    GLOBAL_CTIME: "Call Time (In)",
    GLOBAL_COTIME: "Call Time (Out)",
    GLOBAL_CONAME: "Called Name (Out)",
    GLOBAL_CONUM: "Called Number (0ut)",
    GLOBAL_CNAME: "Caller Name (In)",
    GLOBAL_CNUM: "Caller Number (In)",
    GLOBAL_CELLID: "Cell ID",
    GLOBAL_CELLSRV: "Cell Service State",
    GLOBAL_CELLSIG: "Cell Signal Strength",
    GLOBAL_CLIP: "Clipboard Contents",
    GLOBAL_DATE: "Date",
    GLOBAL_DAYM: "Day Of Month",
    GLOBAL_DAYW: "Day Of Week",
    GLOBAL_DEVID: "Device ID",
    GLOBAL_DEVMAN: "Device Manufacturer",
    GLOBAL_DEVMOD: "Device Model",
    GLOBAL_DEVPROD: "Device Product",
    GLOBAL_DEVTID: "Device Telephony ID",
    GLOBAL_BRIGHT: "Display Brightness",
    GLOBAL_DTOUT: "Display Timeout",
    GLOBAL_ECC: "Email Cc",
    GLOBAL_EDATE: "Email Date",
    GLOBAL_EFROM: "Email From",
    GLOBAL_ESUBJ: "Email Subject",
    GLOBAL_ETIME: "Email Time",
    GLOBAL_MEMF: "Free Memory",
    GLOBAL_GPS: "GPS Status",
    GLOBAL_HTTPL: "HTTP Content Length",
    GLOBAL_HTTPD: "HTTP Data",
    GLOBAL_HTTPR: "HTTP Response Code",
    GLOBAL_HEART: "Heart Rate",
    GLOBAL_HUMIDITY: "Humidity",
    GLOBAL_IMETHOD: "Input Method",
    GLOBAL_INTERRUPT: "Interrupt Mode",
    GLOBAL_KEYG: "Keyguard Status",
    GLOBAL_LAPP: "Last Application",
    GLOBAL_FOTO: "Last Photo",
    GLOBAL_LIGHT: "Light Level",
    GLOBAL_LOC: "Location",
    GLOBAL_LOCN: "Location (Net)",
    GLOBAL_LOCACC: "Location Accuracy",
    GLOBAL_LOCNACC: "Location Accuracy (Net)",
    GLOBAL_LOCALT: "Location Altitude",
    GLOBAL_LOCTMS: "Location Fix Time Secs",
    GLOBAL_LOCNTMS: "Location Fix Time Secs (Net)",
    GLOBAL_LOCSPD: "Location Speed",
    GLOBAL_MFIELD: "Magnetic Field Strength",
    GLOBAL_MTRACK: "Music Track",
    GLOBAL_MUTED: "Muted",
    GLOBAL_NIGHT: "Night Mode",
    GLOBAL_NTITLE: "Notification Title",
    GLOBAL_PNUM: "Phone Number",
    GLOBAL_PRESSURE: "Pressure",
    GLOBAL_PACTIVE: "Profiles Active",
    GLOBAL_PENABLED: "Profiles Enabled",
    GLOBAL_ROAM: "Roaming",
    GLOBAL_ROOT: "Root Available",
    GLOBAL_SDK: "SDK Version",
    GLOBAL_SIMNUM: "SIM Serial Number",
    GLOBAL_SIMSTATE: "SIM State",
    GLOBAL_SCREEN: "Screen",
    GLOBAL_SILENT: "Silent Mode",
    GLOBAL_SPHONE: "Speakerphone",
    GLOBAL_SPEECH: "Speech",
    GLOBAL_TRUN: "Tasks Running",
    GLOBAL_TNET: "Telephone Network Operator",
    GLOBAL_TEMP: "Temperature (Celsius)",
    GLOBAL_TETHER: "Tether",
    GLOBAL_SMSRB: "Text Body",
    GLOBAL_SMSRD: "Text Date",
    GLOBAL_SMSRF: "Text From",
    GLOBAL_SMSRN: "Text From Name",
    GLOBAL_MMSRS: "Text Subject",
    GLOBAL_SMSRT: "Text Time",
    GLOBAL_TIME: "Time",
    GLOBAL_TIMEMS: "Time MilliSeconds",
    GLOBAL_TIMES: "Time Seconds",
    GLOBAL_UIMODE: "UI Mode",
    GLOBAL_UPS: "Uptime Seconds",
    GLOBAL_VOICE: "Voice Results",
    GLOBAL_VOLA: "Volume- Alarm",
    GLOBAL_VOLC: "Volume - Call",
    GLOBAL_VOLD: "Volume - DTMF",
    GLOBAL_VOLM: "Volume - Media",
    GLOBAL_VOLN: "Volume- Notification",
    GLOBAL_VOLR: "Volume - Ringer",
    GLOBAL_VOLS: "Volume - System",
    GLOBAL_WIFII: "WIFi Info",
    GLOBAL_WIFI: "WiFi Status",
    GLOBAL_WIMAX: "Wimax Status",
    GLOBAL_WIN: "Window Label"
}
