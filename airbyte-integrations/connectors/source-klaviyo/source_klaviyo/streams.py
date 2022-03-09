#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from source_klaviyo.schemas import Campaign, Event, GlobalExclusion, Metric, PersonList


class KlaviyoStream(HttpStream, ABC):
    """Base stream"""

    url_base = "https://a.klaviyo.com/api/v1/"
    primary_key = "id"
    page_size = 100

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self._api_key = api_key

    @property
    @abstractmethod
    def schema(self):
        """Pydantic model that represents stream schema"""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        decoded_response = response.json()
        if decoded_response["end"] < decoded_response["total"] - 1:  # end is zero based
            return {
                "page": decoded_response["page"] + 1,
            }

        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """Usually contains common params e.g. pagination size etc."""
        next_page_token = next_page_token or {}
        return {**next_page_token, "api_key": self._api_key, "count": self.page_size}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        response_json = response.json()
        for record in response_json.get("data", []):  # API returns records in a container array "data"
            yield record

    def get_json_schema(self) -> Mapping[str, Any]:
        """Use Pydantic schema"""
        return self.schema.schema()


class IncrementalKlaviyoStream(KlaviyoStream, ABC):
    """Base class for all incremental streams, requires cursor_field to be declared"""

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self._start_ts = int(pendulum.parse(start_date).timestamp())

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """

    def request_params(self, stream_state=None, **kwargs):
        """Add incremental filters"""
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)

        if not params.get("since"):  # skip state filter if already have one from pagination
            state_ts = int(stream_state.get(self.cursor_field, 0))
            params["since"] = max(state_ts, self._start_ts)
        params["sort"] = "asc"

        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        state_ts = int(current_stream_state.get(self.cursor_field, 0))
        return {self.cursor_field: max(latest_record.get(self.cursor_field), state_ts)}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        decoded_response = response.json()
        if decoded_response.get("next"):
            return {"since": decoded_response["next"]}

        return None


class ReverseIncrementalKlaviyoStream(KlaviyoStream, ABC):
    """Base class for all streams that natively incremental but supports desc & asc order"""

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self._start_datetime = pendulum.parse(start_date)
        self._reversed = False
        self._reached_old_records = False
        self._low_boundary = None

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        """How often to checkpoint state (i.e: emit a STATE message). By default return the same value as page_size"""
        return None if self._reversed else self.page_size

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """

    def request_params(self, stream_state=None, **kwargs):
        """Add incremental filters"""
        stream_state = stream_state or {}
        if stream_state:
            self._reversed = True
            self._low_boundary = max(pendulum.parse(stream_state[self.cursor_field]), self._start_datetime)
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["sort"] = "desc" if self._reversed else "asc"

        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        latest_cursor = pendulum.parse(latest_record[self.cursor_field])
        if current_stream_state:
            latest_cursor = max(pendulum.parse(latest_record[self.cursor_field]), pendulum.parse(current_stream_state[self.cursor_field]))
        return {self.cursor_field: latest_cursor.isoformat()}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        next_page_token = super().next_page_token(response)
        if self._reversed and self._reached_old_records:
            return None

        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        for record in super().parse_response(response=response, **kwargs):
            if self._reversed:
                if pendulum.parse(record[self.cursor_field]) < self._low_boundary:
                    self._reached_old_records = True
                    continue
            else:
                if pendulum.parse(record[self.cursor_field]) < self._start_datetime:
                    continue
            yield record


class Campaigns(KlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/reference/get-campaigns"""

    schema = Campaign

    def path(self, **kwargs) -> str:
        return "campaigns"


class Lists(KlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/reference/get-lists"""

    schema = PersonList

    def path(self, **kwargs) -> str:
        return "lists"


class GlobalExclusions(ReverseIncrementalKlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/reference/get-global-exclusions"""

    schema = GlobalExclusion
    page_size = 5000  # the maximum value allowed by API
    cursor_field = "timestamp"
    primary_key = "email"

    def path(self, **kwargs) -> str:
        return "people/exclusions"


class Metrics(KlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/reference/get-metrics"""

    schema = Metric

    def path(self, **kwargs) -> str:
        return "metrics"


class Events(IncrementalKlaviyoStream):
    """Docs: https://developers.klaviyo.com/en/reference/metrics-timeline"""

    schema = Event
    cursor_field = "timestamp"

    def path(self, **kwargs) -> str:
        return "metrics/timeline"
