#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import CustomFields, Projects, Sections, Stories, Tags, Tasks, TeamMemberships, Teams, Users, Workspaces


class SourceAsana(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            workspaces_stream = Workspaces(authenticator=TokenAuthenticator(token=config["access_token"]))
            next(workspaces_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(token=config["access_token"])
        args = {"authenticator": authenticator}
        return [
            CustomFields(**args),
            Projects(**args),
            Sections(**args),
            Stories(**args),
            Tags(**args),
            Tasks(**args),
            Teams(**args),
            TeamMemberships(**args),
            Users(**args),
            Workspaces(**args),
        ]
