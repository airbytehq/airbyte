#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_protocol import SyncMode
from base_python import AbstractSource, Stream, TokenAuthenticator

from .api import Accounts, Agents, AgentTimelines, Bans, Chats, Departments, Goals, Roles, RoutingSettings, Shortcuts, Skills, Triggers


class SourceZendeskChat(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = TokenAuthenticator(token=config["access_token"])
            list(RoutingSettings(authenticator=authenticator).read_records(SyncMode.full_refresh))
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Zendesk Chat API with the provided credentials - {error}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(token=config["access_token"])
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
