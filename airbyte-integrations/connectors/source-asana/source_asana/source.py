#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple, Union

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_asana.oauth import AsanaOauth2Authenticator

from .streams import CustomFields, Projects, Sections, Stories, Tags, Tasks, TeamMemberships, Teams, Users, Workspaces


class SourceAsana(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            workspaces_stream = Workspaces(authenticator=self._get_authenticator(config))
            next(workspaces_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, e

    @staticmethod
    def _get_authenticator(config: dict) -> Union[TokenAuthenticator, AsanaOauth2Authenticator]:
        if "access_token" in config:
            # Before Oauth we had Person Access Token stored under "access_token"
            # config field, this code here is for backward compatibility
            return TokenAuthenticator(token=config["access_token"])
        creds = config.get("credentials")
        if "personal_access_token" in creds:
            return TokenAuthenticator(token=creds["personal_access_token"])
        else:
            return AsanaOauth2Authenticator(
                token_refresh_endpoint="https://app.asana.com/-/oauth_token",
                client_secret=creds["client_secret"],
                client_id=creds["client_id"],
                refresh_token=creds["refresh_token"],
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = {"authenticator": self._get_authenticator(config)}
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
