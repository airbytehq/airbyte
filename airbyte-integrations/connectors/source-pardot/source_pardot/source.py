#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .api import Pardot
from .stream import Campaigns, EmailClicks, ListMembership, Lists, ProspectAccounts, Prospects, Users, VisitorActivities, Visitors, Visits


# Source
class SourcePardot(AbstractSource):
    @staticmethod
    def _get_pardot_object(config: Mapping[str, Any]) -> Pardot:
        pardot = Pardot(**config)
        pardot.login()
        return pardot

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            pardot = self._get_pardot_object(config)
            pardot.access_token
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        pardot = self._get_pardot_object(config)
        auth = TokenAuthenticator(pardot.access_token)
        args = {"authenticator": auth, "config": config}

        return [
            EmailClicks(**args),
            Campaigns(**args),
            ListMembership(**args),
            Lists(**args),
            ProspectAccounts(**args),
            Prospects(**args),
            Users(**args),
            VisitorActivities(**args),
            Visitors(**args),
            Visits(parent_stream=Visitors(**args), **args),
        ]
