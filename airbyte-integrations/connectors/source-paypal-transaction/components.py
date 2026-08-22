#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from dataclasses import InitVar, dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, Optional, Union

import backoff
import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options import RequestOptionsProvider
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


logger = logging.getLogger("airbyte")

RESULT_SET_TOO_LARGE = "RESULTSET_TOO_LARGE"
SMALLEST_WINDOW_REJECTED_MESSAGE = (
    "PayPal transaction search result set exceeds the API maximum for the smallest one-second time_window slice."
)


@dataclass
class PayPalOauth2Authenticator(DeclarativeOauth2Authenticator):
    """Request example for API token extraction:
    For `old_config` scenario:
        curl -v POST https://api-m.sandbox.paypal.com/v1/oauth2/token \
        -H "Accept: application/json" \
        -H "Accept-Language: en_US" \
        -u "CLIENT_ID:SECRET" \
        -d "grant_type=client_credentials"
    """

    # config: Mapping[str, Any]
    # client_id: Union[InterpolatedString, str]
    # client_secret: Union[InterpolatedString, str]
    # refresh_request_body: Optional[Mapping[str, Any]] = None
    # token_refresh_endpoint: Union[InterpolatedString, str]
    # grant_type: Union[InterpolatedString, str] = "refresh_token"
    # expires_in_name: Union[InterpolatedString, str] = "expires_in"
    # access_token_name: Union[InterpolatedString, str] = "access_token"
    # parameters: InitVar[Mapping[str, Any]]

    def get_refresh_request_headers(self):
        basic_auth = base64.b64encode(bytes(f"{self.get_client_id()}:{self.get_client_secret()}", "utf-8")).decode("utf-8")
        return {"Authorization": f"Basic {basic_auth}"}

    @backoff.on_exception(
        backoff.expo,
        DefaultBackoffException,
        max_tries=2,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        max_time=300,
    )
    def _get_refresh_access_token_response(self):
        try:
            request_url = self.get_token_refresh_endpoint()
            request_headers = self.get_refresh_request_headers()
            request_body = self.build_refresh_request_body()

            logger.info(f"Sending request to URL: {request_url}")

            response = requests.request(method="POST", url=request_url, data=request_body, headers=request_headers)

            self._log_response(response)
            response.raise_for_status()

            response_json = response.json()

            self.access_token = response_json.get("access_token")

            return response.json()

        except requests.exceptions.RequestException as e:
            if e.response and (e.response.status_code == 429 or e.response.status_code >= 500):
                raise DefaultBackoffException(request=e.response.request, response=e.response)
            raise
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


class ResultSetTooLargeError(Exception):
    """Raised when PayPal rejects a transaction search query because its result set exceeds the API maximum."""


@dataclass
class ResultSetTooLargeErrorHandler(ErrorHandler):
    """Reports an oversized transaction search result set to `DateWindowSplittingRetriever`.

    PayPal rejects the whole query instead of paginating through it, so the date window has to shrink
    before any record can be read. Other responses are left to the sibling error handlers.
    """

    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    @property
    def max_retries(self) -> Optional[int]:
        return None

    @property
    def max_time(self) -> Optional[int]:
        return None

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> Optional[ErrorResolution]:
        if isinstance(response_or_exception, requests.Response) and response_or_exception.status_code == 400:
            if self._error_name(response_or_exception) == RESULT_SET_TOO_LARGE:
                raise ResultSetTooLargeError(response_or_exception.text)
        return None

    @staticmethod
    def _error_name(response: requests.Response) -> Optional[str]:
        try:
            body = response.json()
        except ValueError:
            return None
        return body.get("name") if isinstance(body, Mapping) else None


@dataclass
class DateWindowSplittingRetriever(SimpleRetriever):
    """Reads a date window in halves when PayPal rejects it with RESULTSET_TOO_LARGE.

    PayPal rejects a transaction search whose result set exceeds 10,000 transactions without returning
    any page, so pagination and the CDK pagination reset cannot make progress: the window itself must
    shrink. Reading each half recursively keeps every transaction of the original window in the sync and
    lets the cursor advance past a high-volume window.
    """

    request_options_provider: Optional[RequestOptionsProvider] = None
    partition_field_start: str = "start_time"
    partition_field_end: str = "end_time"
    datetime_format: str = "%Y-%m-%dT%H:%M:%SZ"
    cursor_granularity: timedelta = timedelta(seconds=1)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        # Custom components are instantiated generically, so the cursor's request options provider comes
        # in under the name used by the factory instead of the one used by SimpleRetriever.
        if self.request_options_provider is not None:
            self.request_option_provider = self.request_options_provider

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        yield from self._read_window(records_schema, stream_slice)

    def _read_window(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice],
    ) -> Iterable[StreamData]:
        try:
            yield from super().read_records(records_schema=records_schema, stream_slice=stream_slice)
        except ResultSetTooLargeError:
            windows = self._split(stream_slice)
            if not windows:
                raise AirbyteTracedException(
                    message=SMALLEST_WINDOW_REJECTED_MESSAGE,
                    internal_message=f"PayPal returned {RESULT_SET_TOO_LARGE} for {stream_slice}, which cannot be narrowed further.",
                    failure_type=FailureType.config_error,
                )

            logger.info(f"PayPal returned {RESULT_SET_TOO_LARGE} for {stream_slice}. Reading the window as {windows} instead.")
            for window in windows:
                yield from self._read_window(records_schema, window)

    def _split(self, stream_slice: Optional[StreamSlice]) -> List[StreamSlice]:
        if stream_slice is None:
            return []

        start_value = stream_slice.cursor_slice.get(self.partition_field_start)
        end_value = stream_slice.cursor_slice.get(self.partition_field_end)
        if not start_value or not end_value:
            return []

        start = datetime.strptime(start_value, self.datetime_format)
        end = datetime.strptime(end_value, self.datetime_format)
        if end - start <= self.cursor_granularity:
            return []

        granularity_units = (end - start) // self.cursor_granularity
        midpoint = start + (granularity_units // 2) * self.cursor_granularity
        return [
            self._window(stream_slice, start, midpoint),
            self._window(stream_slice, midpoint + self.cursor_granularity, end),
        ]

    def _window(self, stream_slice: StreamSlice, start: datetime, end: datetime) -> StreamSlice:
        return StreamSlice(
            partition=stream_slice.partition,
            cursor_slice={
                **stream_slice.cursor_slice,
                self.partition_field_start: start.strftime(self.datetime_format),
                self.partition_field_end: end.strftime(self.datetime_format),
            },
            extra_fields=stream_slice.extra_fields,
        )
