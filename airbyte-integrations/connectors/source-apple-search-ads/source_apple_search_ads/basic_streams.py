from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib import request

import requests

from airbyte_cdk.sources.streams.http import HttpStream

from .authenticator import AppleSearchAdsAuthenticator

class AppleSearchAdsStream(HttpStream, ABC):

    url_base = "https://api.searchads.apple.com/api/v4/"

    limit = 1000

    org_id: str

    def __init__(
        self,
        org_id: str,
        authenticator: AppleSearchAdsAuthenticator,
        **kwargs,
    ):
        self.org_id = org_id

        super().__init__(authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pagination = response.json()["pagination"]

        if pagination == None:
            return None

        if pagination["totalResults"] > (pagination["startIndex"] + 1) * self.limit:
            return {"limit": self.limit, "offset": ((pagination["startIndex"] + 1) * self.limit) + 1 }
        else:
            return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {
            "X-AP-Context": f"orgId={self.org_id}"
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()["data"]

        yield from data


class Campaigns(AppleSearchAdsStream):
    primary_key = "id"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "limit": self.limit,
            "offset": 0
        }

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "campaigns"
