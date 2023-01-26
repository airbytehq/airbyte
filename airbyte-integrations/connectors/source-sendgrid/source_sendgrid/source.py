#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    Blocks,
    Bounces,
    Campaigns,
    Contacts,
    GlobalSuppressions,
    InvalidEmails,
    Lists,
    Scopes,
    Segments,
    SingleSends,
    SpamReports,
    StatsAutomations,
    SuppressionGroupMembers,
    SuppressionGroups,
    Templates,
)


class SourceSendgrid(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            start_time = config.get("start_time")
            if start_time and isinstance(start_time, str):
                pendulum.parse(start_time)
            authenticator = TokenAuthenticator(config["apikey"])
            scopes_gen = Scopes(authenticator=authenticator).read_records(sync_mode=SyncMode.full_refresh)
            next(scopes_gen)
            return True, None
        except pendulum.parsing.exceptions.ParserError:
            return False, "Please, provide a valid Start Time parameter"
        except Exception as error:
            return False, f"Unable to connect to Sendgrid API with the provided credentials - {error}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(config["apikey"])
        start_time = config.get("start_time")

        streams = [
            Lists(authenticator=authenticator),
            Campaigns(authenticator=authenticator),
            Contacts(authenticator=authenticator),
            StatsAutomations(authenticator=authenticator),
            Segments(authenticator=authenticator),
            SingleSends(authenticator=authenticator),
            Templates(authenticator=authenticator),
            GlobalSuppressions(authenticator=authenticator, start_time=start_time),
            SuppressionGroups(authenticator=authenticator),
            SuppressionGroupMembers(authenticator=authenticator),
            Blocks(authenticator=authenticator, start_time=start_time),
            Bounces(authenticator=authenticator, start_time=start_time),
            InvalidEmails(authenticator=authenticator, start_time=start_time),
            SpamReports(authenticator=authenticator, start_time=start_time),
        ]

        return streams
