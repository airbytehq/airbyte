#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from .api import Pardot
from .stream import (
    EmailClicks,
    Campaigns,
    ListMemberships,
    Lists,
    Opportunities,
    ProspectAccounts,
    Prospects,
    Users,
    Visitors,
    VisitorActivities,
    Visitors
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
        args = {'authenticator': auth, 'config': config}
        return [
            EmailClicks(**args),
            Campaigns(**args),
            ListMemberships(**args),
            Lists(**args),
            Opportunities(**args),
            ProspectAccounts(**args),
            Prospects(**args),
            Users(**args),
            # Visit(**args), #TODO: Implement Visit and email stat streams
            Visitors(**args),
            VisitorActivities(**args),
            Visitors(**args),
        ]
