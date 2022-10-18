#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator

from .streams import Clients, Projects, Tags, Tasks, TimeEntries, UserGroups, Users


# Source
class SourceClockify(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            workspace_stream = Users(
                authenticator=TokenAuthenticator(token=config["api_key"], auth_header="X-Api-Key", auth_method=""),
                workspace_id=config["workspace_id"],
            )
            next(workspace_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, f"Please check that your API key and workspace id are entered correctly: {repr(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(token=config["api_key"], auth_header="X-Api-Key", auth_method="")

        args = {"authenticator": authenticator, "workspace_id": config["workspace_id"]}

        return [Users(**args), Projects(**args), Clients(**args), Tags(**args), UserGroups(**args), TimeEntries(**args), Tasks(**args)]
