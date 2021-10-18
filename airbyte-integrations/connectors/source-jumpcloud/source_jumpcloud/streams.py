from abc import ABC, abstractmethod
import copy
import math
from typing import Any, Iterable, List, Mapping, MutableMapping, Union
from airbyte_cdk.models.airbyte_protocol import AirbyteStream, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from airbyte_cdk.sources import source
from airbyte_cdk.sources.streams.core import Stream
import json
from datetime import datetime
import pendulum

from .jumpcloud import Jumpcloud

class JumpcloudStream(Stream, ABC):
    '''
    Base class for Jumpcloud Stream
    '''
    primary_key = None

    def __init__(self, api : Jumpcloud, **kwargs) -> None:
        '''
        Initialize Jumpcloud Object
        '''
        self.api = api
        super().__init__(**kwargs)

class IncrementalJumpcloudStream(JumpcloudStream, ABC):
    '''
    Base class for Incremental Jumpcloud Stream
    '''

    primary_key = None
    cursor_field = "collection_time"

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)     

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        '''
        Default Implementation
        '''
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        
        max_cursor = max(pendulum.parse(current_state), pendulum.parse(latest_state))

        new_stream_state = {
            self.cursor_field : str(max_cursor)
        }

        return new_stream_state

# --------------- All Streams ------------------------------

# --------------- Apple MDM Stream -------------------------

class AppleMdm(JumpcloudStream):
    '''
    Stream for Apple MDMs
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)
    
    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_apple_mdms()

# --------------- Active Directories Stream ----------------

class ActiveDirectories(JumpcloudStream):
    '''
    Stream for Active Directories
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_active_directories()
    
# --------------- Directories Stream -----------------------

class Directories(JumpcloudStream):
    '''
    Stream for Directories
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_directories()

# --------------- LDAP Servers Stream ----------------------

class LdapServer(JumpcloudStream):
    '''
    Stream for LDAP Servers
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_ldap_servers()

# --------------- Policies Streams -------------------------

class Policies(JumpcloudStream):
    '''
    Stream for Policies 
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_policies()

class PolicyResults(JumpcloudStream):
    '''
    Stream for Policy Results
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_policy_results()

class PolicyTemplates(JumpcloudStream):
    '''
    Stream for Policy Templates
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_policy_templates()

# --------------- System Groups Streams --------------------

class SystemGroups(JumpcloudStream):
    '''
    Stream for System Groups
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_groups()

# ---------------- User Groups Streams ----------------------

class UserGroups(JumpcloudStream):
    '''
    Stream for User Groups
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_user_groups()

# --------------- System Insights Streams ------------------

class SystemInsightsApps(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Apps
    '''

    primary_key : List[str] = ["system_id", "name", "path"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_apps()

class SystemInsightsBattery(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Battery
    '''

    primary_key = "system_id"

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_battery()

class SystemInsightsBitlockerInfo(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Bitlocker Info
    '''

    primary_key : List[str] = ["system_id", "drive_letter"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_bitlocker_info()

class SystemInsightsBrowserPlugins(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Browser Plugins
    '''

    primary_key : List[str] = ["system_id", "name", "version"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_browser_plugins()

class SystemInsightsChromeExtensions(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Chrome Extensions
    '''

    primary_key : List[str] = ["system_id", "identifier"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_chrome_extensions()

class SystemInsightsCrashes(JumpcloudStream):
    '''
    Stream for System Insights of Crashes
    '''

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_crashes()

class SystemInsightsDiskEncryption(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Disk Encryption
    '''

    primary_key : List[str] = ["system_id", "name"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_disk_encryption()

class SystemInsightsDiskInfo(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Disk Info
    '''

    primary_key : List[str] = ["system_id", "id"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_disk_info()

class SystemInsightsEtcHosts(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Etc Hosts
    '''

    primary_key : List[str] = ["system_id", "hostnames"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_etc_hosts()

class SystemInsightsFirefoxAddons(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Firefox Addons
    '''

    primary_key : List[str] = ["system_id", "identifier"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_firefox_addons()

class SystemInsightsGroups(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Groups
    '''

    primary_key : List[str] = ["system_id", "gid"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_groups()

class SystemInsightsIeExtensions(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of IE Extensions
    '''

    primary_key : List[str] = ["system_id", "registry_path"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_ie_extensions()

class SystemInsightsInterfaceAddresses(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Interface Addresses
    '''

    primary_key : List[str] = ["system_id", "address"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_interface_addresses()

class SystemInsightsKernelInfo(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Kernel Info
    '''

    primary_key = "system_id"

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_kernel_info()

class SystemInsightsLaunchd(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Launchd
    '''

    primary_key : List[str] = ["system_id", "name", "path"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_launchd()

class SystemInsightsLoggedInUsers(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Logged-In Users
    '''

    primary_key : List[str] = ["system_id", "pid", "tty"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_logged_in_users()

class SystemInsightsLogicalDrives(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Logical Drives
    '''

    primary_key : List[str] = ["system_id", "device_id"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_logical_drives()

class SystemInsightsMounts(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Mounts
    '''

    primary_key : List[str] = ["system_id", "path", "device"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_mounts()

class SystemInsightsOsVersion(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of OS Versions
    '''

    primary_key = "system_id"

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_os_version()

class SystemInsightsPatches(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Patches
    '''    
    
    primary_key : List[str] = ["system_id", "hotfix_id"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_patches()

class SystemInsightsPrograms(JumpcloudStream):
    '''
    Stream for System Insights of Programs
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_programs()

class SystemInsightsSafariExtensions(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Safari Extensions
    '''

    primary_key : List[str] = ["system_id", "uid", "version"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_safari_extensions()

class SystemInsightsUptime(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Uptime
    '''

    primary_key = "system_id"

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_uptime()

class SystemInsightsUsbDevices(JumpcloudStream):
    '''
    Stream for System Insights of USB Devices
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_usb_devices()

class SystemInsightsUserGroups(JumpcloudStream):
    '''
    Stream for System Insights of User Groups
    '''
    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_user_groups()

class SystemInsightsUsers(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of Users
    '''

    primary_key : List[str] = ["system_id", "uid"]

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_users()

class SystemInsightsSystemControls(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of System Controls
    '''

    primary_key = "system_id"

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_system_controls()

class SystemInsightsSystemInfo(IncrementalJumpcloudStream):
    '''
    Stream for System Insights of System Info
    '''

    primary_key = "system_id"

    def __init__(self, api: Jumpcloud, **kwargs) -> None:
        super().__init__(api, **kwargs)

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        return self.api.get_all_system_insights_system_info()