#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import Accounts, Publishers, AdvertiserTransactions


class SourceAwin(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        if 'attribution_window' in config and config['attribution_window'] < 1:
            return False, f"Invalid input for Attribution Window. The attribution window must be 1 or greater."
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config['oauth2_token'])
        accounts = config.get("accounts", [])
        start_date = pendulum.parse(config["start_date"])
        attribution_window = config.get("attribution_window", 30)
        args = {"authenticator": auth, "accounts": accounts, "start_date": start_date, "attribution_window": attribution_window}
        return [Accounts(**args), Publishers(**args), AdvertiserTransactions(**args)]
