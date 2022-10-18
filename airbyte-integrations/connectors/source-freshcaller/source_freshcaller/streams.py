#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream


class FreshcallerStream(HttpStream, ABC):
    """Abstract class curated for Freshcaller"""

    primary_key = "id"
    data_field = ""
    start = 1
    page_limit = 1000
    api_version = 2
    curr_page_param = "page"

    def __init__(self, config: Dict, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    @property
    def url_base(self) -> str:
        return f"https://{self.config['domain']}.freshcaller.com/api/v1/"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        params = {"per_page": self.page_limit, self.curr_page_param: self.start}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            self.logger.debug(f"The next page is: {next_page_token}")
            params.update(next_page_token)
        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Accept": "application/json", "User-Agent": "PostmanRuntime/7.28.0", "Content-Type": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        meta_data = decoded_response.get("meta")
        if meta_data:
            total_pages = meta_data["total_pages"]
            current_page = meta_data["current"]
            if current_page < total_pages:
                current_page += 1
                return {self.curr_page_param: current_page}
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get(self.data_field, [])

    @property
    def max_retries(self) -> Union[int, None]:
        return 10


class APIIncrementalFreshcallerStream(FreshcallerStream):
    """
    Base abstract class for a "true" incremental stream, i.e., for an endpoint that supports
    filtering by date or time
    """

    start_param = "by_time[from]"
    end_param = "by_time[to]"

    def __init__(self, config: Dict, **kwargs):
        super().__init__(config, **kwargs)
        self.config = config
        self.start_date = config["start_date"]
        self.window_in_days = config.get("window_in_days", 5)
        self.sync_lag_minutes = config.get("sync_lag_minutes", 30)

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """
        Override default get_updated_state CDK method to return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        last_synced_at = current_stream_state.get(self.cursor_field, self.start_date)
        last_synced_at = pendulum.parse(last_synced_at) if isinstance(last_synced_at, str) else last_synced_at
        return {self.cursor_field: max(pendulum.parse(latest_record.get(self.cursor_field)).in_tz("UTC"), last_synced_at)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params[self.start_param] = stream_slice[self.start_param]
        params[self.end_param] = stream_slice[self.end_param]
        self.logger.info(f"Endpoint[{self.path()}] - Request params: {params}")
        return params

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override default stream_slices CDK method to provide date_slices as page chunks for data fetch.
        Returns list of dict, example: [{
            "by_time[from]": "2022-03-07 15:00:01",
            "by_time[to]": "2022-03-07 18:00:00"
            },
            {
            "by_time[from]": "2022-03-07 18:00:01",
            "by_time[to]": "2022-03-07 21:00:00"
            },
            ...]
        """
        start_date = pendulum.parse(self.start_date).in_timezone("UTC")
        end_date = pendulum.utcnow().subtract(minutes=self.sync_lag_minutes)  # have a safe lag

        # Determine stream_state, if no stream_state we use start_date
        if stream_state:
            start_date = stream_state.get(self.cursor_field)
            start_date = pendulum.parse(start_date) if isinstance(start_date, str) else start_date
            start_date = start_date.in_tz("UTC")
        # use the lowest date between start_date and self.end_date, otherwise API fails if start_date is in future
        start_date: pendulum.Pendulum = min(start_date, end_date)
        date_slices = []

        while start_date <= end_date:
            end_date_slice = start_date.add(days=self.window_in_days)
            # add 1 second for start next slice to not duplicate data from previous slice end date.
            stream_slice = {
                self.start_param: start_date.add(seconds=1).to_datetime_string(),
                self.end_param: min(end_date_slice, end_date).to_datetime_string(),
            }
            date_slices.append(stream_slice)
            start_date = end_date_slice

        return date_slices


class Users(FreshcallerStream):
    """
    API docs: https://developers.freshcaller.com/api/#users
    """

    data_field = "users"

    def path(self, **kwargs) -> str:
        return "users"


class Teams(FreshcallerStream):
    """
    API docs: https://developers.freshcaller.com/api/#teams
    """

    data_field = "teams"

    def path(self, **kwargs) -> str:
        return "teams"


class Calls(APIIncrementalFreshcallerStream):
    """
    API docs: https://developers.freshcaller.com/api/#calls
    """

    data_field = "calls"
    cursor_field = "created_time"

    def path(self, **kwargs) -> str:
        return "calls"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {**super().request_params(stream_state, stream_slice, next_page_token), "has_ancestry": "true"}
        return params


class CallMetrics(APIIncrementalFreshcallerStream):
    """
    API docs: https://developers.freshcaller.com/api/#call-metrics
    """

    data_field = "call_metrics"
    cursor_field = "created_time"

    def path(self, **kwargs) -> str:
        return "call_metrics"
