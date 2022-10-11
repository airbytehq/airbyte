#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from base64 import b64encode
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class FinnStatisticsStream(HttpStream, ABC):

    def __init__(self, partnerId: str, changedLastDays: str, **kwargs):
        super().__init__(**kwargs)
        self.partnerId = partnerId
        self.changedLastDays = changedLastDays

    # TODO: Fill in the url base. Required.
    url_base = "https://api.schibsted.com/finn/statistics/summary/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        partner_id = self.partnerId
        changed_last_days = self.changedLastDays

        params = {"partnerId": partner_id,
                  "changedLastDays": changed_last_days}
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        if response.status_code != 200:
            return []

        response_json = response.json()
        if response_json:
            yield from response_json


class Ads(FinnStatisticsStream):

    primary_key = "statisticsPageUrl"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "ads"


# Source
class SourceFinnStatistics(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        try:
            auth = (config["client_id"], config["client_secret"])
            params = {"partnerId": config["partnerId"],
                      "changedLastDays": config["changedLastDays"]}
            url = "https://api.schibsted.com/finn/statistics/summary/ads"
            session = requests.get(url, auth=auth, params=params)
            session.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        token = b64encode(bytes(
            config["client_id"] + ":" + config["client_secret"], "utf-8")).decode("ascii")
        auth = TokenAuthenticator(token, auth_method="Basic")

        return [Ads(authenticator=auth, partnerId=config["partnerId"], changedLastDays=config["changedLastDays"])]
