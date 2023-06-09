#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .auth import AudienceProjectAuthenticator
from .streams import AudienceprojectStream
from .streams_campaigns import Campaigns
from .streams_devices import Devices
from .streams_profile import Profile
from .streams_reach import Reach
from .streams_report import Report


class SourceAudienceproject(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        auth = AudienceProjectAuthenticator(url_base=AudienceprojectStream.oauth_url_base, config=config)
        auth_header = auth.get_auth_header()
        url_base = AudienceprojectStream.url_base + "campaigns"
        try:
            response = requests.get(url=url_base, headers=auth_header)
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = AudienceProjectAuthenticator(url_base=AudienceprojectStream.oauth_url_base, config=config)
        return [
            Campaigns(authenticator=auth, config=config),
            Report(authenticator=auth, config=config),
            Devices(authenticator=auth, config=config),
            Reach(authenticator=auth, config=config),
            Profile(authenticator=auth, config=config),
        ]
