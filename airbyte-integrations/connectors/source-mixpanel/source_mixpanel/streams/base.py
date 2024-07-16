#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time
from abc import ABC
from datetime import timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk import BackoffStrategy
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from pendulum import Date
from requests.auth import AuthBase
from source_mixpanel.errors_handlers import DateSlicesMixinErrorHandler, MixpanelStreamErrorHandler
from source_mixpanel.utils import MixpanelStreamBackoffStrategy, fix_date_time


class MixpanelStream(HttpStream, ABC):
    """
    Formatted API Rate Limit  (https://help.mixpanel.com/hc/en-us/articles/115004602563-Rate-Limits-for-API-Endpoints):
      A maximum of 5 concurrent queries
      60 queries per hour.
    """

    DEFAULT_REQS_PER_HOUR_LIMIT = 60

    @property
    def state_checkpoint_interval(self) -> int:
        # to meet the requirement of emitting state at least once per 15 minutes,
        # we assume there's at least 1 record per request returned. Given that each request is followed by a 60 seconds sleep
        # we'll have to emit state every 15 records
        return 15

    @property
    def url_base(self) -> str:
        prefix = "eu." if self.region == "EU" else ""
        return f"https://{prefix}mixpanel.com/api/2.0/"

    @property
    def reqs_per_hour_limit(self) -> int:
        # https://help.mixpanel.com/hc/en-us/articles/115004602563-Rate-Limits-for-Export-API-Endpoints#api-export-endpoint-rate-limits
        return self._reqs_per_hour_limit

    @reqs_per_hour_limit.setter
    def reqs_per_hour_limit(self, value: int) -> None:
        self._reqs_per_hour_limit = value

    def __init__(
        self,
        authenticator: AuthBase,
        region: str,
        project_timezone: Optional[str] = "US/Pacific",
        start_date: Optional[Date] = None,
        end_date: Optional[Date] = None,
        date_window_size: int = 30,  # in days
        attribution_window: int = 0,  # in days
        select_properties_by_default: bool = True,
        project_id: Optional[int] = None,
        reqs_per_hour_limit: int = DEFAULT_REQS_PER_HOUR_LIMIT,
        **kwargs: Any,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.date_window_size = date_window_size
        self.attribution_window = attribution_window
        self.additional_properties = select_properties_by_default
        self.region = region
        self.project_timezone = project_timezone
        self.project_id = project_id
        self.retries = 0
        self._reqs_per_hour_limit = reqs_per_hour_limit
        super().__init__(authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Define abstract method"""
        return None

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def process_response(self, response: requests.Response, **kwargs: Any) -> Iterable[Mapping[str, Any]]:
        json_response = response.json()
        if self.data_field is not None:
            data = json_response.get(self.data_field, [])
        elif isinstance(json_response, list):
            data = json_response
        elif isinstance(json_response, dict):
            data = [json_response]

        for record in data:
            fix_date_time(record)
            yield record

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        **kwargs: Any,
    ) -> Iterable[Mapping[str, Any]]:
        # parse the whole response
        yield from self.process_response(response, stream_state=stream_state, **kwargs)

        if self.reqs_per_hour_limit > 0:
            # we skip this block, if self.reqs_per_hour_limit = 0,
            # in all other cases wait for X seconds to match API limitations
            self.logger.info(f"Sleep for {3600 / self.reqs_per_hour_limit} seconds to match API limitations after reading from {self.name}")
            time.sleep(3600 / self.reqs_per_hour_limit)

    @property
    def max_retries(self) -> Union[int, None]:
        # we want to limit the max sleeping time by 2^3 * 60 = 8 minutes
        return 3

    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        return MixpanelStreamBackoffStrategy(stream=self)

    def get_error_handler(self) -> Optional[ErrorHandler]:
        return MixpanelStreamErrorHandler(logger=self.logger, max_retries=self.max_retries, error_mapping=DEFAULT_ERROR_MAPPING)

    def get_stream_params(self) -> Mapping[str, Any]:
        """
        Fetch required parameters in a given stream. Used to create sub-streams
        """
        params = {
            "authenticator": self._http_client._session.auth,
            "region": self.region,
            "project_timezone": self.project_timezone,
            "reqs_per_hour_limit": self.reqs_per_hour_limit,
        }
        if self.project_id:
            params["project_id"] = self.project_id
        return params

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        if self.project_id:
            return {"project_id": str(self.project_id)}
        return {}


class DateSlicesMixin:
    def get_error_handler(self) -> Optional[ErrorHandler]:
        return DateSlicesMixinErrorHandler(
            logger=self.logger, max_retries=self.max_retries, error_mapping=DEFAULT_ERROR_MAPPING, stream=self  # type: ignore[attr-defined]
        )

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._timezone_mismatch = False

    def parse_response(self, *args: Any, **kwargs: Any) -> Iterable[Mapping[str, Any]]:
        if self._timezone_mismatch:
            return []
        yield from super().parse_response(*args, **kwargs)  # type: ignore[misc]

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # use the latest date between self.start_date and stream_state
        start_date = self.start_date  # type: ignore[attr-defined]
        cursor_value = None

        if stream_state and self.cursor_field and self.cursor_field in stream_state:  # type: ignore[attr-defined]
            # Remove time part from state because API accept 'from_date' param in date format only ('YYYY-MM-DD')
            # It also means that sync returns duplicated entries for the date from the state (date range is inclusive)
            cursor_value = stream_state[self.cursor_field]  # type: ignore[attr-defined]
            stream_state_date = pendulum.parse(stream_state[self.cursor_field]).date()  # type: ignore[attr-defined]
            start_date = max(start_date, stream_state_date)

        # move start_date back <attribution_window> days to sync data since that time as well
        start_date = start_date - timedelta(days=self.attribution_window)  # type: ignore[attr-defined]

        # end_date cannot be later than today
        end_date = min(self.end_date, pendulum.today(tz=self.project_timezone).date())  # type: ignore[attr-defined]

        while start_date <= end_date:
            if self._timezone_mismatch:
                return
            current_end_date = start_date + timedelta(days=self.date_window_size - 1)  # type: ignore[attr-defined] # -1 is needed because dates are inclusive
            stream_slice = {
                "start_date": str(start_date),
                "end_date": str(min(current_end_date, end_date)),
            }
            if cursor_value:
                stream_slice[self.cursor_field] = cursor_value  # type: ignore[attr-defined]
            yield stream_slice
            # add 1 additional day because date range is inclusive
            start_date = current_end_date + timedelta(days=1)

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[MutableMapping[str, Any], Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)  # type: ignore[misc]
        if stream_slice is None:
            return params
        return {
            **params,
            "from_date": stream_slice["start_date"],
            "to_date": stream_slice["end_date"],
        }


class IncrementalMixpanelStream(MixpanelStream, ABC):
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        updated_state = latest_record.get(self.cursor_field)
        if updated_state:
            state_value = current_stream_state.get(self.cursor_field)
            if state_value:
                updated_state = max(updated_state, state_value)
            current_stream_state[self.cursor_field] = updated_state
        return current_stream_state
