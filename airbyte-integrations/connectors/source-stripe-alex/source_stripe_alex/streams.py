#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class StripeAlexStream(HttpStream, ABC):
    def __init__(
        self,
        *,
        path: str,
        url_base: str,
        primary_key: str,
        retry_factor: float,
        max_retries: int,
        headers: Mapping[str, str],
        response_key: str,
        request_parameters: Mapping[str, Any],
        start_date: int,
        cursor_field: str,
    ):
        super().__init__()
        self._path = path
        self._primary_key = primary_key
        self.url_base = url_base
        self._retry_factor = retry_factor
        self._max_retries = max_retries
        self._headers = headers
        self._response_key = response_key
        self._request_parameters = request_parameters
        self._start_date = start_date
        self._cursor_field = cursor_field
        self._cursor_value = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return self._headers

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = self._request_parameters
        # FIXME would be great to extract this too!
        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get(self._response_key, [])  # Stripe puts records in a container array "data"

    def url_base(self) -> str:
        return self._url_base

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return self._path

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        return {self.cursor_field: max(latest_record.get(self.cursor_field), current_stream_state.get(self.cursor_field, 0))}

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @primary_key.setter
    def set_primary_key(self, value):
        self._primary_key = value

    @property
    def retry_factor(self) -> float:
        return self._retry_factor

    @retry_factor.setter
    def set_retry_factor(self, value):
        self.retry_factor = value

    @property
    def max_retries(self) -> Union[int, None]:
        return self._max_retries

    @max_retries.setter
    def set_max_retries(self, value):
        self._max_retries = value

    @property
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        return self._cursor_field


class Invoices(StripeAlexStream):
    def __init__(self, **kwargs):
        super().__init__(path="v1/invoices", **kwargs)
