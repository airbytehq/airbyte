#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_freshcaller.streams import CallMetrics, Calls, Teams, Users

logger = logging.getLogger("airbyte")


class FreshcallerTokenAuthenticator(TokenAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Api-Auth": self._token}


class SourceFreshcaller(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        api_url = f"https://{config['domain']}.freshcaller.com/api/v1"
        auth = FreshcallerTokenAuthenticator(token=config["api_key"]).get_auth_header()
        url = "{api_url}/users".format(api_url=api_url)
        auth.update({"Accept": "application/json"})
        auth.update({"Content-Type": "application/json"})

        try:
            session = requests.get(url, headers=auth)
            session.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = FreshcallerTokenAuthenticator(token=config["api_key"])
        args = {"authenticator": authenticator, "config": config}
        return [
            Users(**args),
            Teams(**args),
            Calls(**args),
            CallMetrics(**args),
        ]
