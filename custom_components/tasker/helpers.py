"""Helpers for Tasker integration"""
import csv
from typing import Any

class TaskerProfile:
    
    def __init__(self,
        raw_data = None, *,
        name = None,
        enabled = None,
        active = None,
    ) -> None:
        self._name = raw_data.get("name", name)
        self._enabled = raw_data.get("enabled", enabled)
        self._active = raw_data.get("active", active)
        self._raw_data = raw_data or {
            "name": name,
            "enabled": enabled,
            "active": active
        }
        
    @property
    def name(self) -> str:
        return self._raw_data["name"]
        
    @property
    def enabled(self) -> bool | None:
        return self._raw_data.get("enabled")
        
    @property
    def active(self) -> bool | None:
        return self._raw_data.get("active")
        
    def update(self, new_data):
        self._raw_data.update(new_data)
        
class TaskerTask:
    
    def __init__(self,
        raw_data = None, *,
        name = None,
        running = None,
        last_return = None,
    ) -> None:
        self._raw_data = raw_data or {
            "name": name,
            "running": running,
            "last_return": last_return,
        }
        
    @property
    def name(self) -> str:
        return self._raw_data.get["name"]
        
    @property
    def running(self) -> bool | None:
        return self._raw_data.get("running")
        
    @property
    def last_return(self) -> Any:
        return self._raw_data.get("last_return")
        
    def update(self, new_data):
        self._raw_data.update(new_data)
        
class TaskerScene:
    
    def __init__(self,
        raw_data = None, *,
        name = None,
        status = None,
    ) -> None:
        self._raw_data = raw_data or {
            "name": name,
            "status": status,
        }
        
    @property
    def name(self) -> str:
        return self._raw_data["name"]
        
    @property
    def status(self) -> str:
        return self._raw_data.get("status")
        
    def update(self, new_data):
        self._raw_data.update(new_data)
        
class TaskerGlobal:
    
    def __init__(self,
        raw_data = None, *,
        name = None,
        value = None
    ) -> None:
        self._raw_data = raw_data or {
            "name": name,
            "value": value,
        }
        
    @property
    def name(self) -> str:
        return self._raw_data["name"]
        
    @property
    def value(self) -> Any:
        return self._raw_data.get("value")
        
    def update(self, new_data):
        self._raw_data.update(new_data)
        
def maybe_cast(value):
    try:
        if value is None:
            return ""
        elif (lower := value.lower()) == "null":
            return ""
        elif lower == "true":
            return True
        elif lower == "false":
            return False
        elif value.isdigit():
            return int(value)
        else:
            return float(value)
    except:
        return value
        
def csv_to_dict(text: str) -> dict[str, Any]:
    reader = csv.DictReader(
        text.strip().splitlines(),
        delimiter=","
    )
    out: dict[str, Any] = {}
    for line in reader:
        for k, v in line.items():
            if k is None:
                continue
            v = maybe_cast(v)
            if k in out:
                out[k].append(v)
            else:
                out[k] = [v]
    if not out:
        raise csv.Error("Not CSV")
    return out
    
    
    