#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class MintegralStream(HttpStream, ABC):
    page_size = 50
    url_base = "https://ss-api.mintegral.com/api/open/v1/"
    use_cache = True  # it is used in all streams

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()["data"]
        if response_json["limit"] * response_json["page"] < response_json["total"]:
            next_page = response_json["page"] + 1
        else:
            return None

        return {
            "limit": self.page_size,
            "page": next_page
        }

    def request_params(
            self,
            stream_state: Optional[Mapping[str, Any]],
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ):
        if next_page_token:
            return next_page_token
        else:
            return {
                "limit": self.page_size
            }


class Offers(MintegralStream):
    primary_key = "campaign_id"

    def path(self, **kwargs) -> str:
        return "offers"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.text == "":
            return '{}'
        yield from response.json()["data"]["list"]
