#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class TimelyIntegrationStream(HttpStream, ABC):
    FIRST_PAGE = 1
    primary_key = "id"
    url_base = "https://api.timelyapp.com/1.1/"

    def __init__(self, account_id: str, start_date: str, bearer_token: str, **kwargs):
        super().__init__(**kwargs)
        self.account_id = account_id
        self.start_date = start_date
        self.bearer_token = bearer_token

    def request_params(
        self, stream_state: Mapping[str, any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        if next_page_token is None:
            return {"page": self.FIRST_PAGE, "per_page": "1000", "account_id": self.account_id}

        return next_page_token

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        bearer_token = self.bearer_token
        event_headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
        return event_headers

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        return response.json()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        results = response.json()
        if results:
            if len(results) > 0:
                url_query = urlparse(response.url).query
                query_params = parse_qs(url_query)

                new_params = {param_name: param_value[0] for param_name, param_value in query_params.items()}
                if "page" in new_params:
                    new_params["page"] = int(new_params["page"]) + 1
                return new_params


class Events(TimelyIntegrationStream):
    # https://dev.timelyapp.com/#list-all-events
    primary_key = "id"

    def path(self, **kwargs) -> str:
        account_id = self.account_id
        start_date = self.start_date
        upto = datetime.today().strftime("%Y-%m-%d")
        return f"{account_id}/events?since={start_date}&upto={upto}"


class SourceTimely(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        account_id = config["account_id"]
        start_date = config["start_date"]
        bearer_token = config["bearer_token"]

        headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
        url = f"https://api.timelyapp.com/1.1/{account_id}/events?since={start_date}&upto=2022-05-01"

        try:
            session = requests.get(url, headers=headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = {"bearer_token": config["bearer_token"], "account_id": config["account_id"], "start_date": config["start_date"]}
        return [Events(**args)]
