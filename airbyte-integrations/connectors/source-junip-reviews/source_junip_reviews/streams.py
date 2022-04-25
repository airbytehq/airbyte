
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class JunipReviewsStream(HttpStream, ABC):
    url_base = "https://api.juniphq.com/v1/"
    primary_key = None

    def __init__(self, junip_store_key,**kwargs):
        super().__init__(**kwargs)
        self.junip_store_key = junip_store_key

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()

        if decoded_response.get("after") is not None:
            return {
                "page[after]": decoded_response.get("after")
            }
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        This method is for add query params in request URL
        """
        params = {}

        if next_page_token:
            params.update(next_page_token)

        return params

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return {"Junip_Store_key": self.junip_store_key}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        return [response.json()]

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:

        return self.name


class Products(JunipReviewsStream):
    """
    url: "self.base_url/self.name"
    """


class ProductOverviews(JunipReviewsStream):
    """
    url: "self.base_url/self.name"
    """


class ProductReviews(JunipReviewsStream):
    """
     url: "self.base_url/self.name"
     """


class Stores(JunipReviewsStream):
    """
    url: "self.base_url/self.name"
    """


class StoreReviews(JunipReviewsStream):
    """
    url: "self.base_url/self.name"
    """
