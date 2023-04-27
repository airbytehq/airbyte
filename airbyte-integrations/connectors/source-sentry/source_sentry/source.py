#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from requests.exceptions import HTTPError

from .streams import Events, Issues, ProjectDetail, Projects, Releases


# Source
class SourceSentry(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        try:
            events_stream = Events(
                authenticator=TokenAuthenticator(token=config["auth_token"]),
                hostname=config.get("hostname"),
                organization=config.get("organization"),
                project=config.get("project"),
            )
            next(events_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except HTTPError:
            return False, "Check failed: either project's or organization's name is invalid"
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        stream_args = {
            "authenticator": TokenAuthenticator(token=config["auth_token"]),
            "hostname": config.get("hostname"),
        }
        project_stream_args = {
            **stream_args,
            "organization": config["organization"],
            "project": config["project"],
        }
        return [
            Events(**project_stream_args),
            Issues(**project_stream_args),
            ProjectDetail(**project_stream_args),
            Projects(**stream_args),
            Releases(**project_stream_args),
        ]
