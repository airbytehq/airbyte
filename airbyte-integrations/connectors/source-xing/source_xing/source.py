#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams_ads import Ads
from .streams_customers import Customers
from .streams_daily_insights import DailyInsights
from .streams_lifetime_insights import LifetimeInsights


class SourceXing(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        header = TokenAuthenticator(token=config["access_token"]).get_auth_header()
        profile_url = "https://api.xing.com/vendor/ad-manager-api/v1/customers"
        try:
            response = requests.get(url=profile_url, headers=header)
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, f"{e}, {response.json().get('message')}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(config["access_token"])

        return [
            Customers(authenticator=auth, config=config),
            Ads(authenticator=auth, config=config),
            DailyInsights(authenticator=auth, config=config),
            LifetimeInsights(authenticator=auth, config=config),
        ]
