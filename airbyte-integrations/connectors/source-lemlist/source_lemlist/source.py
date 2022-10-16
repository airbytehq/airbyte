#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_lemlist.auth import HttpBasicAuthenticator

from .streams import Activities, Campaigns, Team, Unsubscribes


class SourceLemlist(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = HttpBasicAuthenticator(
                (
                    "",
                    config["api_key"],
                ),
            )

            team_stream = Team(authenticator=auth)
            team_gen = team_stream.read_records(sync_mode=SyncMode.full_refresh)

            next(team_gen)
            return True, None
        except Exception as error:
            return False, f"The provided API key {config['api_key']} is invalid. - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = HttpBasicAuthenticator(
            (
                "",
                config["api_key"],
            ),
        )
        return [Team(authenticator=auth), Campaigns(authenticator=auth), Activities(authenticator=auth), Unsubscribes(authenticator=auth)]
