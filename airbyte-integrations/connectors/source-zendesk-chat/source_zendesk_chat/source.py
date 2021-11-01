#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, List, Mapping, Tuple

from airbyte_protocol import SyncMode
from base_python import AbstractSource, Stream, TokenAuthenticator

from .api import Accounts, Agents, AgentTimelines, Bans, Chats, Departments, Goals, Roles, RoutingSettings, Shortcuts, Skills, Triggers


class ZendeskAuthentication(TokenAuthenticator):
    """ Provides the authentication capabilities for both old and new methods. """

    def __init__(self, config: Dict):
        self.config = config

    def get_auth(self) -> TokenAuthenticator:
        """ Return the TokenAuthenticator object with access_token. """

        # the old config supports for backward capability
        access_token = self.config.get("access_token")
        if not access_token:
            # the new config supports `OAuth2.0`
            access_token = self.config["credentials"]["access_token"]
        return TokenAuthenticator(token=access_token)
        


class SourceZendeskChat(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = ZendeskAuthentication(config).get_auth()
            list(RoutingSettings(authenticator=authenticator).read_records(SyncMode.full_refresh))
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Zendesk Chat API with the provided credentials - {error}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = ZendeskAuthentication(config).get_auth()
        return [
            Agents(authenticator=authenticator),
            AgentTimelines(authenticator=authenticator, start_date=config["start_date"]),
            Accounts(authenticator=authenticator),
            Chats(authenticator=authenticator),
            Shortcuts(authenticator=authenticator),
            Triggers(authenticator=authenticator),
            Bans(authenticator=authenticator),
            Departments(authenticator=authenticator),
            Goals(authenticator=authenticator),
            Skills(authenticator=authenticator),
            Roles(authenticator=authenticator),
            RoutingSettings(authenticator=authenticator),
        ]
