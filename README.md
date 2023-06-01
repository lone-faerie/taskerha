# TaskerHA

The [TaskerHA integration](https://github.com/lone-faerie/taskerha/) allows you to connect the [Tasker Android app](https://tasker.joaoapps.com/) with Home Assistant.

**This makes use of the new HTTP Request event in the latest Tasker Beta. Requires Tasker 6.2+**

## What it does
1. Expose Tasker profiles as `switch` entities
2. Expose Tasker tasks as `binary_sensor` entities
3. Expose Tasker scenes as `select` entities
4. Expose Tasker global `variables` as text entities
5. Trigger automations from Tasker commands
6. `tasker.perform_task` service to perform Tasker tasks, like the `Perform Task` action in Tasker
7. `tasker.send_command` service to send Tasker commands, like the `Command` action in Tasker
8. `tasker.backup` service to backup Tasker config, like the `Data Backup` action in Tasker
9. `tasker.import_task` service to import a Tasker task from XML, like the `Import` action in Tasker

## How to use it
### Installation & Setup
1. Import and setup the accompanying [HTTP API Tasker project](https://taskernet.com/shares/?user=AS35m8kgT7%2Fg4ls8ijzQzKetgy0bfSM3ifU47We%2BDxSEZ7%2FmVpu2beWrD%2FErLXwjCiPkbdRz&id=Project%3ATasker+HTTP+API)
2. Add repository to HACS. HACS > Integrations > Custom Repositories
3. Add Integration in Home Assistant. Settings > Devices & Services > Add Integration
4. Follow the instructions on screen to complete the setup.
5. Enable the profile, task, scene, and global variable entities that you are interested in.

### Configuration 
- Builtin Global Variables
	- Choose builtin Tasker global variables to add as `text` entities, the same as user-defined global variables.
- Structure Global Variables Outputs
	- Works similar to Tasker. If the output is either JSON, HTML, XML, or CSV, enable this option so that you can easily read its contents via the `value_json` attribute.
- Track Tasker commands
	- Fire Home Assistant events and trigger automations from Tasker commands. Commands will be queued and fired every scan interval. Disable if you aren't tracking commands in Tasker.
- Scan Interval
	- Tasker data and commands poll rate

## Reference
### Profiles
- `switch` entity

| Attribute | Description |
| --------- | ----------- |
| `state` | Tasker profile is enabled |
| `active` | Tasker profile is active |

### Tasks
- `binary_sensor` entity

| Attribute | Description |
| --------- | ----------- |
| `state` | Tasker task is running |
| `last_return` | Last return value from calling `tasker.perform_task` |

- `tasker.perform_task` service

| Field | Description |
| ----- | ----------- |
| `target` | Tasker task to perform |
| `par1`, `par2` | Values assigned to `par1` and `par2` are available in the selected task as normal variables. |
| `variables` | Variables to forward to the task as local variables. |
| `structure_output` | If the return value is either JSON or XML, enable this option so you can easily read its contents in the last_return attribute of the selected task's entity. |

### Scenes
- `select` entity

| Attribute | Description |
| --------- | ----------- |
| `state` | Tasker scene displaying as |
| `options` | Options for `Display As` in `Show Scene` Tasker action |

### Globals
- `text` entity

| Attribute | Description |
| --------- | ----------- |
| `state` | Current value of Tasker global variable |
| `value_json` | Structured output of `state` |

### Commands
*Rate limited by scan interval*
- `tasker_command` event

| Field | Description |
| ----- | ----------- |
| `command` | The full command |
| `prefix` | The part of the command on the left of `=:=` or the whole command if `=:=` is not present |
| `params` | List of parts on the right of `=:=` |`

- `Tasker command received` device trigger

| Field | Description |
| ----- | ----------- |
| `command` | Command to trigger on. You can use regex to match multiple commands. If not set will trigger on any command. |

### Misc
- `tasker.backup` service

| Field | Description |
| ----- | ----------- |
| `username` | If you set this account, a file will be created in your backup folder on Google Drive. |

- `tasker.import_task` service

| Field | Description |
| ----- | ----------- |
| `xml` | Tasker XML Data for the task being imported |
