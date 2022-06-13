#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, Mapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class MetabaseStream(HttpStream, ABC):
    def __init__(self, instance_api_url: str, **kwargs):
        super().__init__(**kwargs)
        self.instance_api_url = instance_api_url

    primary_key = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Override this method to define a pagination strategy.

        The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.

        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """
        return None

    @property
    def url_base(self) -> str:
        return self.instance_api_url

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json


class Cards(MetabaseStream):
    def path(self, **kwargs) -> str:
        return "card"
