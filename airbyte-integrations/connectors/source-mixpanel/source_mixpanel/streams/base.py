#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time
from abc import ABC
from datetime import timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from pendulum import Date


class MixpanelStream(HttpStream, ABC):
    """
    Formatted API Rate Limit  (https://help.mixpanel.com/hc/en-us/articles/115004602563-Rate-Limits-for-API-Endpoints):
      A maximum of 5 concurrent queries
      60 queries per hour.

    API Rate Limit Handler: after each request freeze for the time period: 3600/reqs_per_hour_limit seconds
    """

    @property
    def url_base(self):
        prefix = "eu." if self.region == "EU" else ""
        return f"https://{prefix}mixpanel.com/api/2.0/"

    # https://help.mixpanel.com/hc/en-us/articles/115004602563-Rate-Limits-for-Export-API-Endpoints#api-export-endpoint-rate-limits
    reqs_per_hour_limit: int = 60  # 1 query per minute

    def __init__(
        self,
        authenticator: HttpAuthenticator,
        region: str,
        project_timezone: str,
        start_date: Date = None,
        end_date: Date = None,
        date_window_size: int = 30,  # in days
        attribution_window: int = 0,  # in days
        select_properties_by_default: bool = True,
        project_id: int = None,
        **kwargs,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.date_window_size = date_window_size
        self.attribution_window = attribution_window
        self.additional_properties = select_properties_by_default
        self.region = region
        self.project_timezone = project_timezone
        self.project_id = project_id

        super().__init__(authenticator=authenticator)

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Define abstract method"""
        return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        try:
            return super()._send_request(request, request_kwargs)
        except requests.exceptions.HTTPError as e:
            error_message = e.response.text
            if error_message:
                self.logger.error(f"Stream {self.name}: {e.response.status_code} {e.response.reason} - {error_message}")
            raise e

    def process_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        if self.data_field is not None:
            data = json_response.get(self.data_field, [])
        elif isinstance(json_response, list):
            data = json_response
        elif isinstance(json_response, dict):
            data = [json_response]

        for record in data:
            yield record

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        **kwargs,
    ) -> Iterable[Mapping]:

        # parse the whole response
        yield from self.process_response(response, stream_state=stream_state, **kwargs)

        if self.reqs_per_hour_limit > 0:
            # we skip this block, if self.reqs_per_hour_limit = 0,
            # in all other cases wait for X seconds to match API limitations
            self.logger.info("Sleep for %s seconds to match API limitations", 3600 / self.reqs_per_hour_limit)
            time.sleep(3600 / self.reqs_per_hour_limit)

    def backoff_time(self, response: requests.Response) -> float:
        """
        Some API endpoints do not return "Retry-After" header
        some endpoints return a strangely low number
        """
        return max(int(response.headers.get("Retry-After", 600)), 60)

    def get_stream_params(self) -> Mapping[str, Any]:
        """
        Fetch required parameters in a given stream. Used to create sub-streams
        """
        params = {"authenticator": self.authenticator, "region": self.region, "project_timezone": self.project_timezone}
        if self.project_id:
            params["project_id"] = self.project_id
        return params

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        if self.project_id:
            return {"project_id": str(self.project_id)}
        return {}


class DateSlicesMixin:
    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        date_slices: list = []

        # use the latest date between self.start_date and stream_state
        start_date = self.start_date
        if stream_state and self.cursor_field and self.cursor_field in stream_state:
            # Remove time part from state because API accept 'from_date' param in date format only ('YYYY-MM-DD')
            # It also means that sync returns duplicated entries for the date from the state (date range is inclusive)
            stream_state_date = pendulum.parse(stream_state[self.cursor_field]).date()
            start_date = max(start_date, stream_state_date)

        # move start_date back <attribution_window> days to sync data since that time as well
        start_date = start_date - timedelta(days=self.attribution_window)

        # end_date cannot be later than today
        end_date = min(self.end_date, pendulum.today(tz=self.project_timezone).date())

        while start_date <= end_date:
            current_end_date = start_date + timedelta(days=self.date_window_size - 1)  # -1 is needed because dates are inclusive
            date_slices.append(
                {
                    "start_date": str(start_date),
                    "end_date": str(min(current_end_date, end_date)),
                }
            )
            # add 1 additional day because date range is inclusive
            start_date = current_end_date + timedelta(days=1)

        return date_slices

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        return {
            **params,
            "from_date": stream_slice["start_date"],
            "to_date": stream_slice["end_date"],
        }


class IncrementalMixpanelStream(MixpanelStream, ABC):
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        updated_state = latest_record.get(self.cursor_field)
        if updated_state:
            state_value = current_stream_state.get(self.cursor_field)
            if state_value:
                updated_state = max(updated_state, state_value)
            current_stream_state[self.cursor_field] = updated_state
        return current_stream_state
