#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from typing import Any, Dict, Generator, Iterator, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (AirbyteCatalog, AirbyteConnectionStatus,
                                AirbyteMessage, AirbyteRecordMessage,
                                AirbyteStream, ConfiguredAirbyteCatalog,
                                Status, Type)
from airbyte_cdk.models.airbyte_protocol import ConnectorSpecification, DestinationSyncMode, SyncMode
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.streams.core import Stream
from pydantic.fields import Field
from pydantic.main import BaseModel

from .streams import (
    ActiveDirectories,
    AppleMdm,
    Directories,
    LdapServer,
    Policies,
    PolicyResults,
    PolicyTemplates,
    SystemGroups,
    SystemInsightsApps,
    SystemInsightsBattery,
    SystemInsightsBitlockerInfo,
    SystemInsightsBrowserPlugins,
    SystemInsightsChromeExtensions,
    SystemInsightsCrashes,
    SystemInsightsDiskEncryption,
    SystemInsightsDiskInfo,
    SystemInsightsEtcHosts,
    SystemInsightsFirefoxAddons,
    SystemInsightsGroups,
    SystemInsightsIeExtensions,
    SystemInsightsInterfaceAddresses,
    SystemInsightsKernelInfo,
    SystemInsightsLaunchd,
    SystemInsightsLoggedInUsers,
    SystemInsightsLogicalDrives,
    SystemInsightsMounts,
    SystemInsightsOsVersion,
    SystemInsightsPatches,
    SystemInsightsPrograms,
    SystemInsightsSafariExtensions,
    SystemInsightsSystemControls,
    SystemInsightsSystemInfo,
    SystemInsightsUptime,
    SystemInsightsUsbDevices,
    SystemInsightsUserGroups,
    SystemInsightsUsers,
    UserGroups
)

from .jumpcloud import Jumpcloud

class SourceJumpcloud(AbstractSource):

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        try:
            Jumpcloud(config.get("api_key"))
        except Exception as exc:
            return False, "Error Occurred. Check API KEY or Internet Conenection"
        
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        api = Jumpcloud(config.get("api_key"))
        return [
            AppleMdm(api),
            ActiveDirectories(api),
            Directories(api),
            LdapServer(api),
            Policies(api),
            PolicyResults(api),
            PolicyTemplates(api),
            SystemGroups(api),
            UserGroups(api),
            SystemInsightsApps(api),
            SystemInsightsBattery(api),
            SystemInsightsBitlockerInfo(api),
            SystemInsightsBrowserPlugins(api),
            SystemInsightsChromeExtensions(api),
            SystemInsightsCrashes(api),
            SystemInsightsDiskEncryption(api),
            SystemInsightsDiskInfo(api),
            SystemInsightsEtcHosts(api),
            SystemInsightsFirefoxAddons(api),
            SystemInsightsGroups(api),
            SystemInsightsIeExtensions(api),
            SystemInsightsInterfaceAddresses(api),
            SystemInsightsKernelInfo(api),
            SystemInsightsLaunchd(api),
            SystemInsightsLoggedInUsers(api),
            SystemInsightsLogicalDrives(api),
            SystemInsightsMounts(api),
            SystemInsightsOsVersion(api),
            SystemInsightsPatches(api),
            SystemInsightsPrograms(api),
            SystemInsightsSafariExtensions(api),
            SystemInsightsSystemInfo(api),
            # SystemInsightsSystemControls(api),
            SystemInsightsUptime(api),
            SystemInsightsUsbDevices(api),
            SystemInsightsUserGroups(api),
            SystemInsightsUsers(api)
        ]
