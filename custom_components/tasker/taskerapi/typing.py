"""Typing Helpers for taskerapi"""
import base64
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

TaskerStructure = (
    dict[str, 'TaskerStructure'] |
    list['TaskerStructure'] |
    str |
    int |
    float |
    bool |
    None
)

class TaskerStructureType(str, Enum):
    NONE = "None"
    AUTO = "Auto"
    JSON = "JSON"
    HTML_XML = "HTML_XML"
    CSV = "CSV"

@dataclass
class TaskerStats:
    active_profiles: int
    total_profiles: int
    total_tasks: int
    total_scenes: int
    total_globals: int
    version: str
    
@dataclass
class TaskerProfile:
    name: str
    enabled: bool
    active: bool = field(default=False)
    
@dataclass
class TaskerTask:
    name: str
    running: bool = field(default=False)
    
@dataclass
class TaskerScene:
    name: str
    status: str
    display_as: str = field(default="")
    position: Sequence[int] = field(default_factory=tuple)
    size: Sequence[int] = field(default_factory=tuple)
    
    def __post_init__(self):
        self.position = tuple(self.position[:2])
        self.size = tuple(self.size[:2])
    
@dataclass
class TaskerGlobal:
    name: str
    value: str | bytes | int | float | bool | None = field(default=None)
    value_json: TaskerStructure = field(default=None, init=False)
    
@dataclass
class TaskerGlobalDecoded(TaskerGlobal):
    
    def __post_init__(self):
        if self.value is not None and type(self.value) in [str, bytes]:
            self.value = base64.b64decode(self.value).decode('ascii')
            
@dataclass
class TaskerGlobalEncoded(TaskerGlobal):
    
    def __post_init__(self):
        value: bytes | None = None
        if type(self.value) is bytes:
            value = self.value
        elif type(self.value) is str:
            value = self.value.encode()
        elif self.value is not None:
            value = str(self.value).lower().encode()
        self.value = base64.b64encode(value).decode() if value else ""

