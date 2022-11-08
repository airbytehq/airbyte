#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class LemlistStream(HttpStream):
    """Default and max value page_size can have is 100"""

    url_base = "https://api.lemlist.com/api/"
    primary_key = "_id"
    page_size = 100
    initial_offset = 0
    offset = initial_offset

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Pagination is offset-based and response doesn't contain a next_page_token
        Thus, the only way to know if there are any more pages is to check if the
        number of items in current page is equal to the page_size limit"""

        if len(response.json()) == self.page_size:
            self.offset += self.page_size
            next_page_params = {"offset": self.offset}
            return next_page_params
        return None

    def path(self, **kwargs) -> str:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        params["offset"] = self.initial_offset
        params["limit"] = self.page_size
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json()
        yield from records

    def backoff_time(self, response: requests.Response):
        if "Retry-After" in response.headers:
            return int(response.headers["Retry-After"])
        else:
            self.logger.info("Retry-after header not found. Using default backoff value")
            return 2


class Team(LemlistStream):
    """https://developer.lemlist.com/#get-team-information"""

    def path(self, **kwargs) -> str:
        return "team"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json()
        yield from [records]


class Campaigns(LemlistStream):
    """https://developer.lemlist.com/#campaigns"""

    def path(self, **kwargs) -> str:
        return "campaigns"


class Activities(LemlistStream):
    """https://developer.lemlist.com/#activities"""

    def path(self, **kwargs) -> str:
        return "activities"


class Unsubscribes(LemlistStream):
    """https://developer.lemlist.com/#unsubscribes"""

    def path(self, **kwargs) -> str:
        return "unsubscribes"
