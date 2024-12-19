#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests

from airbyte_cdk import AirbyteTracedException, BackoffStrategy
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import WaitTimeFromHeaderBackoffStrategy
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, ResponseAction
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_protocol.models import FailureType

from .utils import get_analytics_columns, to_datetime_str


# For Pinterest analytics streams rate limit is 300 calls per day / per user.
# once hit - response would contain `code` property with int.
MAX_RATE_LIMIT_CODE = 8


class NonJSONResponse(Exception):
    pass


class RateLimitExceeded(Exception):
    pass


class PinterestErrorHandler(ErrorHandler):
    def __init__(self, logger: logging.Logger, stream_name: str) -> None:
        self._logger = logger
        self._stream_name = stream_name

    @property
    def max_retries(self) -> Optional[int]:
        """
        Default value from HttpStream before the migration
        """
        return 5

    @property
    def max_time(self) -> Optional[int]:
        """
        Default value from HttpStream before the migration
        """
        return 60 * 10

    def _handle_unknown_error(self, response: Optional[Union[requests.Response, Exception]]) -> Optional[ErrorResolution]:
        """
        Error handling could potentially be improved. For example, connection errors are probably transient as we could retry.
        """
        if isinstance(response, Exception):
            return ErrorResolution(
                ResponseAction.FAIL,
                FailureType.system_error,
                f"Failed because of the following error: {response}",
            )
        return None

    def interpret_response(self, response: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        unhandled_error_resolution = self._handle_unknown_error(response)
        if unhandled_error_resolution:
            return unhandled_error_resolution

        try:
            resp = response.json()
        except requests.exceptions.JSONDecodeError:
            raise NonJSONResponse(f"Received unexpected response in non json format: '{response.text}'")

        # when max rate limit exceeded, we should skip the stream.
        if response.status_code == requests.codes.too_many_requests and (
            isinstance(resp, dict) and resp.get("code", 0) == MAX_RATE_LIMIT_CODE
        ):
            self._logger.error(f"For stream {self._stream_name} Max Rate Limit exceeded.")
            return ErrorResolution(
                ResponseAction.FAIL,
                FailureType.transient_error,
                "Max Rate Limit exceeded",
            )
        elif response.status_code == requests.codes.too_many_requests or 500 <= response.status_code < 600:
            return ErrorResolution(
                ResponseAction.RETRY,
                FailureType.transient_error,
                f"Failed after retrying on status code {response.status_code}: {response.content}",
            )
        elif not response.ok:
            return ErrorResolution(
                response_action=ResponseAction.FAIL,
                failure_type=FailureType.system_error,
                error_message=f"Response status code: {response.status_code}. Unexpected error. Failed.",
            )

        return ErrorResolution(ResponseAction.SUCCESS)


def _create_retry_after_backoff_strategy() -> BackoffStrategy:
    return WaitTimeFromHeaderBackoffStrategy(header="Retry-After", max_waiting_time_in_seconds=600, parameters={}, config={})


class PinterestStream(HttpStream, ABC):
    url_base = "https://api.pinterest.com/v5/"
    primary_key = "id"
    data_fields = ["items"]
    raise_on_http_errors = True
    max_rate_limit_exceeded = False
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, config: Mapping[str, Any]) -> None:
        super().__init__(authenticator=config["authenticator"])
        self.config = config

    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        return _create_retry_after_backoff_strategy()

    def get_error_handler(self) -> ErrorHandler:
        return PinterestErrorHandler(self.logger, self.name)

    @property
    def start_date(self) -> str:
        return self.config["start_date"]

    @property
    def window_in_days(self) -> int:
        return 30  # Set window_in_days to 30 days date range

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.json().get("bookmark", {}) if self.data_fields else {}

        if next_page:
            return {"bookmark": next_page}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token or {}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        Parsing response data with respect to Rate Limits.
        """
        data = response.json()

        if not self.max_rate_limit_exceeded:
            for data_field in self.data_fields:
                data = data.get(data_field, [])

            for record in data:
                yield record


class PinterestSubStream(HttpSubStream):
    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )
        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)

            # iterate over all parent records with current stream_slice
            for record in parent_records:
                yield {"parent": record, "sub_parent": stream_slice}


class IncrementalPinterestStream(PinterestStream, ABC):
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        default_value = self.start_date.format("YYYY-MM-DD")
        latest_state = latest_record.get(self.cursor_field, default_value)
        current_state = current_stream_state.get(self.cursor_field, default_value)
        latest_state_is_numeric = isinstance(latest_state, int) or isinstance(latest_state, float)

        if latest_state_is_numeric and isinstance(current_state, str):
            current_state = datetime.strptime(current_state, "%Y-%m-%d").timestamp()

        return {self.cursor_field: max(latest_state, current_state)}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:
        """
        Override default stream_slices CDK method to provide date_slices as page chunks for data fetch.
        Returns list of dict, example: [{
            "start_date": "2020-01-01",
            "end_date": "2021-01-02"
            },
            {
            "start_date": "2020-01-03",
            "end_date": "2021-01-04"
            },
            ...]
        """

        start_date = self.start_date
        end_date = pendulum.now()

        # determine stream_state, if no stream_state we use start_date
        if stream_state:
            state = stream_state.get(self.cursor_field)

            state_is_timestamp = isinstance(state, int) or isinstance(state, float)
            if state_is_timestamp:
                state = str(datetime.fromtimestamp(state).date())

            start_date = pendulum.parse(state)

        # use the lowest date between start_date and self.end_date, otherwise API fails if start_date is in future
        start_date = min(start_date, end_date)
        date_slices = []

        while start_date < end_date:
            # the amount of days for each data-chunk beginning from start_date
            end_date_slice = (
                end_date if end_date.subtract(days=self.window_in_days) < start_date else start_date.add(days=self.window_in_days)
            )
            date_slices.append({"start_date": to_datetime_str(start_date), "end_date": to_datetime_str(end_date_slice)})

            # add 1 day for start next slice from next day and not duplicate data from previous slice end date.
            start_date = end_date_slice.add(days=1)

        return date_slices


class IncrementalPinterestSubStream(IncrementalPinterestStream):
    cursor_field = "updated_time"

    def __init__(self, parent: Stream, with_data_slices: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parent = parent
        self.with_data_slices = with_data_slices

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        date_slices = super().stream_slices(sync_mode, cursor_field, stream_state) if self.with_data_slices else [{}]
        parents_slices = PinterestSubStream.stream_slices(self, sync_mode, cursor_field, stream_state) if self.parent else [{}]

        for parents_slice in parents_slices:
            for date_slice in date_slices:
                parents_slice.update(date_slice)

                yield parents_slice


def _lookback_date_limit_reached(response: requests.Response) -> bool:
    """
    After few consecutive requests, analytics API return bad request error with 'You can only get data from the last 90 days' error
    message. But with next request all working good. So, we wait 1 sec and request again if we get this issue.
    """
    if isinstance(response.json(), dict):
        return response.json().get("code", 0) and response.status_code == 400
    return False


class PinterestAnalyticsErrorHandler(ErrorHandler):
    def __init__(self, logger: logging.Logger, stream_name: str) -> None:
        self._decorated = PinterestErrorHandler(logger, stream_name)

    @property
    def max_retries(self) -> Optional[int]:
        """
        Default value from HttpStream before the migration
        """
        return 5

    @property
    def max_time(self) -> Optional[int]:
        """
        Default value from HttpStream before the migration
        """
        return 60 * 10

    def interpret_response(self, response: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        if isinstance(response, requests.Response) and _lookback_date_limit_reached(response):
            return ErrorResolution(
                ResponseAction.RETRY,
                FailureType.transient_error,
                f"Analytics API returns bad request error when under load. This error should be retried after a second. If this error message appears, it means the Analytics API did not recover or there might be a bigger issue so please contact the support team.",
            )

        return self._decorated.interpret_response(response)


class AnalyticsApiBackoffStrategyDecorator(BackoffStrategy):
    def __init__(self) -> None:
        self._decorated = _create_retry_after_backoff_strategy()

    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response) and _lookback_date_limit_reached(response_or_exception):
            return 1
        return self._decorated.backoff_time(response_or_exception)


class PinterestAnalyticsStream(IncrementalPinterestSubStream):
    primary_key = None
    cursor_field = "DATE"
    data_fields = []
    granularity = "DAY"
    analytics_target_ids = None

    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        return AnalyticsApiBackoffStrategyDecorator()

    def get_error_handler(self) -> ErrorHandler:
        return PinterestAnalyticsErrorHandler(self.logger, self.name)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update(
            {
                "start_date": stream_slice["start_date"],
                "end_date": stream_slice["end_date"],
                "granularity": self.granularity,
                "columns": get_analytics_columns(),
            }
        )

        if self.analytics_target_ids:
            params.update({self.analytics_target_ids: stream_slice["parent"]["id"]})

        return params
