
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import datetime
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class JunipReviewsStream(HttpStream, ABC):
    url_base = "https://api.juniphq.com/v1/"
    primary_key = None

    def __init__(self, junip_store_key, **kwargs):
        super().__init__(**kwargs)
        self.junip_store_key = junip_store_key

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Implements the pagination approach for stream.

        Returns: Next page token
        """
        decoded_response = response.json()
        page_token = None

        if decoded_response.get("after"):
            page_token = {
                "page[after]": decoded_response.get("after")
            }
        return page_token

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Adds query params in requested URL.
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
        :return an iterable containing each record in the response
        """
        return {}

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:

        return self.name


class IncrementalJunipReviewsStream(JunipReviewsStream, ABC):
    """
    Baseclass for all incremental streams of Bold source. Override cursor field property in order to use
    incremental stream.
    """
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.
        :return str: The name of the cursor field.
        """
        pass

    def _convert_date_to_timestamp(self, date: datetime):
        return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        base_date = (
            datetime.datetime.combine(
                datetime.date.fromtimestamp(0),
                datetime.datetime.min.time()
            ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        state_dt = self._convert_date_to_timestamp(current_stream_state.get(self.cursor_field, base_date))
        latest_record = self._convert_date_to_timestamp(latest_record.get(self.cursor_field, base_date))

        return {self.cursor_field: max(latest_record, state_dt)}


class Products(IncrementalJunipReviewsStream):
    """
    Ref: https://junip.co/docs/api/

    url: "self.base_url/self.name"
    """
    cursor_field = "created_at"
    primary_key = "id"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Ref: https://junip.co/docs/api/
        """

        json_response = response.json()
        for product in json_response.get("products"):
            yield product


class ProductOverviews(IncrementalJunipReviewsStream):
    """
    Ref: https://junip.co/docs/api/

    url: "self.base_url/self.name"
    """
    cursor_field = "created_at"
    primary_key = "id"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Ref: https://junip.co/docs/api/
        """

        json_response = response.json()
        for product_overview in json_response.get("product_overviews"):
            yield product_overview


class ProductReviews(IncrementalJunipReviewsStream):
    """
    Ref: https://junip.co/docs/api/

    url: "self.base_url/self.name"
    """
    cursor_field = "created_at"
    primary_key = "id"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Ref: https://junip.co/docs/api/
        """

        json_response = response.json()
        for product_reviews in json_response.get("product_reviews"):
            yield product_reviews


class Stores(IncrementalJunipReviewsStream):
    """
    Ref: https://junip.co/docs/api/

    url: "self.base_url/self.name"
    """
    cursor_field = "created_at"
    primary_key = "id"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Ref: https://junip.co/docs/api/
        """

        json_response = response.json()
        for store in json_response.get("stores"):
            yield store


class StoreReviews(IncrementalJunipReviewsStream):
    """
    Ref: https://junip.co/docs/api/

    url: "self.base_url/self.name"
    """
    cursor_field = "created_at"
    primary_key = "id"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Ref: https://junip.co/docs/api/
        """

        json_response = response.json()
        for store_reviews in json_response.get("store_reviews"):
            yield store_reviews
