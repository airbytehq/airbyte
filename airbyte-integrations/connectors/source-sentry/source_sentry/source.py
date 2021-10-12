#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import Events, Issues, ProjectDetail


# Source
class SourceSentry(AbstractSource):
    DEFAULT_HOST = "sentry.io"

    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        try:
            project_detail_stream = ProjectDetail(
                authenticator=TokenAuthenticator(token=config["auth_token"]),
                hostname=config.get("hostname", self.DEFAULT_HOST),
                organization=config["organization"],
                project=config["project"],
            )
            next(project_detail_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        stream_args = {
            "authenticator": TokenAuthenticator(token=config["auth_token"]),
            "hostname": config.get("hostname", self.DEFAULT_HOST),
            "organization": config["organization"],
            "project": config["project"],
        }
        return [Events(**stream_args), Issues(**stream_args)]
