#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import requests
import hashlib
import time
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

from source_mintegral.streams import Offers, Campaigns, Reports


class HeaderAuthenticator(HttpAuthenticator):

    def __init__(self, headers):
        self.headers = headers

    def get_auth_header(self) -> Mapping[str, Any]:
        return self.headers


# Basic full refresh stream
class SourceMintegral(AbstractSource):

    def auth_headers(self, config):
        api_key = config["api_key"]
        access_key = config["access_key"]

        now = str(int(time.time()))
        token = hashlib.md5((api_key + hashlib.md5(now.encode()).hexdigest()).encode()).hexdigest()

        return {
            "access-key": access_key,
            "token": token,
            "timestamp": now
        }

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        headers = self.auth_headers(config)

        try:
            response = requests.get(f"https://ss-api.mintegral.com/api/open/v1/offers", headers=headers)
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        headers = self.auth_headers(config)
        authenticator = HeaderAuthenticator(headers)

        args = {
            "authenticator": authenticator
        }
        return [Offers(**args), Campaigns(**args), Reports(**args)]
