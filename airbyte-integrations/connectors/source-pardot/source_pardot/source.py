#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .api import Pardot
from .stream import (
    Campaigns,
    EmailClicks,
    EmailStats,
    ListMembership,
    Lists,
    Opportunities,
    ProspectAccounts,
    Prospects,
    Users,
    VisitorActivities,
    Visitors,
    Visits,
)


# Source
class SourcePardot(AbstractSource):
    @staticmethod
    def _get_pardot_object(config: Mapping[str, Any]) -> Pardot:
        pardot = Pardot(**config)
        pardot.login()
        return pardot

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        _ = self._get_pardot_object(config)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        pardot = self._get_pardot_object(config)
        auth = TokenAuthenticator(pardot.access_token)
        args = {"authenticator": auth, "config": config}

        visitors = Visitors(**args)
        visitor_activities = VisitorActivities(**args)

        return [
            EmailClicks(**args),
            Campaigns(**args),
            ListMembership(**args),
            Lists(**args),
            Opportunities(**args),
            ProspectAccounts(**args),
            Prospects(**args),
            Users(**args),
            visitor_activities,
            visitors,
            Visits(parent_stream=visitors, **args),
            EmailStats(parent_stream=visitor_activities, **args),
        ]
