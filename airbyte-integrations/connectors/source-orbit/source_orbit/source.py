#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import Members, Workspace

# Source
class SourceOrbit(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            workspace_stream = Workspace(
                authenticator=TokenAuthenticator(token=config["api_token"]),
                workspace=config["workspace"],
            )
            next(workspace_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        stream_args = {
            "authenticator": TokenAuthenticator(token=config["api_token"]),
            "workspace": config["workspace"],
        }

        return [Members(**stream_args),
                Workspace(**stream_args)]
