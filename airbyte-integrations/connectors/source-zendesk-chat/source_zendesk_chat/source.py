#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .streams import Accounts, Agents, AgentTimelines, Bans, Chats, Departments, Goals, Roles, RoutingSettings, Shortcuts, Skills, Triggers


class ZendeskAuthentication:
    """Provides the authentication capabilities for both old and new methods."""

    def __init__(self, config: Dict):
        self.config = config

    def get_auth(self) -> TokenAuthenticator:
        """Return the TokenAuthenticator object with access_token."""

        # the old config supports for backward capability
        access_token = self.config.get("access_token")
        if not access_token:
            # the new config supports `OAuth2.0`
            access_token = self.config["credentials"]["access_token"]

        return TokenAuthenticator(token=access_token)


class SourceZendeskChat(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        authenticator = ZendeskAuthentication(config).get_auth()
        try:
            records = RoutingSettings(authenticator=authenticator).read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Zendesk Chat API with the provided credentials - {error}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = ZendeskAuthentication(config).get_auth()
        return [
            Accounts(authenticator=authenticator),
            AgentTimelines(authenticator=authenticator, start_date=config["start_date"]),
            Agents(authenticator=authenticator),
            Bans(authenticator=authenticator),
            Chats(authenticator=authenticator, start_date=config["start_date"]),
            Departments(authenticator=authenticator),
            Goals(authenticator=authenticator),
            Roles(authenticator=authenticator),
            RoutingSettings(authenticator=authenticator),
            Shortcuts(authenticator=authenticator),
            Skills(authenticator=authenticator),
            Triggers(authenticator=authenticator),
        ]
