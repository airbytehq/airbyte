#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from datetime import timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from pendulum import Date
from requests.auth import AuthBase

from airbyte_cdk import BackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import ConstantBackoffStrategy
from airbyte_cdk.sources.streams.call_rate import APIBudget
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from source_mixpanel.backoff_strategy import DEFAULT_API_BUDGET
from source_mixpanel.errors_handlers import MixpanelStreamErrorHandler
from source_mixpanel.utils import fix_date_time


class MixpanelStream(HttpStream, ABC):
    """
    Formatted API Rate Limit  (https://help.mixpanel.com/hc/en-us/articles/115004602563-Rate-Limits-for-API-Endpoints):
      A maximum of 5 concurrent queries
      60 queries per hour.
    """

    @property
    def state_checkpoint_interval(self) -> int:
        # to meet the requirement of emitting state at least once per 15 minutes,
        # we assume there's at least 1 record per request returned. Given that each request is followed by a 60 seconds sleep
        # we'll have to emit state every 15 records
        return 15

    @property
    def url_base(self):
        prefix = "eu." if self.region == "EU" else ""
        return f"https://{prefix}mixpanel.com/api/query/"

    def __init__(
        self,
        authenticator: AuthBase,
        region: str,
        api_budget: APIBudget = DEFAULT_API_BUDGET,
        project_timezone: Optional[str] = "US/Pacific",
        start_date: Optional[Date] = None,
        end_date: Optional[Date] = None,
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
        super().__init__(authenticator=authenticator, api_budget=api_budget)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Define abstract method"""
        return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def process_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
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
        **kwargs,
    ) -> Iterable[Mapping]:
        # parse the whole response
        yield from self.process_response(response, stream_state=stream_state, **kwargs)

    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        return ConstantBackoffStrategy(backoff_time_in_seconds=60 * 2, config={}, parameters={})

    def get_error_handler(self) -> Optional[ErrorHandler]:
        return MixpanelStreamErrorHandler(logger=self.logger)

    def get_stream_params(self) -> Mapping[str, Any]:
        """
        Fetch required parameters in a given stream. Used to create sub-streams
        """
        params = {
            "authenticator": self._http_client._session.auth,
            "region": self.region,
            "project_timezone": self.project_timezone,
        }
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
