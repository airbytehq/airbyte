#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import Calls, Contacts, RingAttempts, StudioFlowExecution, UserStatus
from .talkdesk_auth import TalkdeskAuth


class SourceTalkdeskExplore(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        talkdesk_auth = TalkdeskAuth(config)
        token_request = talkdesk_auth.request_bearer_token()

        # Check for valid token and scope
        if "access_token" not in token_request.keys():
            return False, "Unable to retrieve access token. Check your credentials."
        elif "data-reports:read" and "data-reports:write" not in token_request["scope"]:
            return (
                False,
                "Provided credential does not have necessary privileges to read data. Required scope: data-reports:read AND data-reports:write",
            )
        else:
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        talkdesk_auth = TalkdeskAuth(config)
        token_request = talkdesk_auth.request_bearer_token()
        talkdesk_auth_token = token_request.get("access_token", None)

        authenticator = TokenAuthenticator(token=talkdesk_auth_token)

        start_date = config.get("start_date", None)
        timezone = config.get("timezone", None)

        streams_ = [
            Calls(start_date=start_date, timezone=timezone, authenticator=authenticator),
            UserStatus(start_date=start_date, timezone=timezone, authenticator=authenticator),
            StudioFlowExecution(start_date=start_date, timezone=timezone, authenticator=authenticator),
            Contacts(start_date=start_date, timezone=timezone, authenticator=authenticator),
            RingAttempts(start_date=start_date, timezone=timezone, authenticator=authenticator),
        ]

        return streams_
