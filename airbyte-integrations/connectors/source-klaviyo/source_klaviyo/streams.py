#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


class KlaviyoStreamLatest(HttpStream, ABC):
    """Base stream for api version v2023-02-22"""

    url_base = "https://a.klaviyo.com/api/"
    primary_key = "id"
    page_size = 100

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self._api_key = api_key

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        base_headers = super().request_headers(**kwargs)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Revision": "2023-02-22",
            "Authorization": "Klaviyo-API-Key " + self._api_key,
        }

        return {**base_headers, **headers}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests.

        Klaviyo uses cursor-based pagination https://developers.klaviyo.com/en/reference/api_overview#pagination
        This method returns the params in the pre-constructed url nested in links[next]
        """
        decoded_response = response.json()

        links = decoded_response.get("links", {})
        next = links.get("next")
        if not next:
            return None

        next_url = urllib.parse.urlparse(next)
        return {str(k): str(v) for (k, v) in urllib.parse.parse_qsl(next_url.query)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        # If next_page_token is set, all of the parameters are already provided
        if next_page_token:
            return next_page_token
        else:
            return {"page[size]": self.page_size}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """:return an iterable containing each record in the response"""
        response_json = response.json()
        for record in response_json.get("data", []):  # API returns records in a container array "data"
            record = self.map_record(record)
            yield record

    def map_record(self, record: Mapping):
        """Subclasses can override this to apply custom mappings to a record"""
        return record


class IncrementalKlaviyoStreamLatest(KlaviyoStreamLatest, ABC):
    """Base class for all incremental streams, requires cursor_field to be declared"""

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self._start_ts = start_date

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.
        :return str: The name of the cursor field.
        """

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        """Add incremental filters"""

        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)

        if not params.get("filter"):
            latest_cursor = pendulum.parse(self._start_ts)
            stream_state_cursor_value = stream_state.get(self.cursor_field)
            if stream_state_cursor_value:
                latest_cursor = max(latest_cursor, pendulum.parse(stream_state[self.cursor_field]))
            params["filter"] = "greater-than(" + self.cursor_field + "," + latest_cursor.isoformat() + ")"
            params["sort"] = self.cursor_field
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        current_stream_cursor_value = current_stream_state.get(self.cursor_field, self._start_ts)
        latest_record_cursor_value = latest_record[self.cursor_field]
        latest_cursor = max(pendulum.parse(latest_record_cursor_value), pendulum.parse(current_stream_cursor_value))
        return {self.cursor_field: latest_cursor.isoformat()}


class Profiles(IncrementalKlaviyoStreamLatest):
    """Docs: https://developers.klaviyo.com/en/reference/get_profiles"""

    cursor_field = "updated"

    def path(self, *args, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return "profiles"

    def map_record(self, record: Mapping):
        record[self.cursor_field] = record["attributes"][self.cursor_field]
        return record


class KlaviyoStreamV1(HttpStream, ABC):
    """Base stream for api v1"""

    url_base = "https://a.klaviyo.com/api/v1/"
    primary_key = "id"
    page_size = 100

    transformer = TypeTransformer(TransformConfig.CustomSchemaNormalization)

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self._api_key = api_key
        transform_function = self.get_custom_transform()
        self.transformer.registerCustomTransform(transform_function)

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def get_custom_transform(self):
        def custom_transform_date_rfc3339(original_value, field_schema):
            if original_value and "format" in field_schema and field_schema["format"] == "date-time":
                transformed_value = pendulum.parse(original_value).to_rfc3339_string()
                return transformed_value
            return original_value

        return custom_transform_date_rfc3339

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
        """:return an iterable containing each record in the response"""

        response_json = response.json()
        for record in response_json.get("data", []):  # API returns records in a container array "data"
            yield record


class IncrementalKlaviyoStreamV1(KlaviyoStreamV1, ABC):
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
        latest_record = latest_record.get(self.cursor_field)

        if isinstance(latest_record, str):
            latest_record = datetime.datetime.strptime(latest_record, "%Y-%m-%d %H:%M:%S")
            latest_record = datetime.datetime.timestamp(latest_record)

        return {self.cursor_field: max(latest_record, state_ts)}

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


class ReverseIncrementalKlaviyoStreamV1(KlaviyoStreamV1, ABC):
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
        """:return an iterable containing each record in the response"""

        for record in super().parse_response(response=response, **kwargs):
            if self._reversed:
                if pendulum.parse(record[self.cursor_field]) < self._low_boundary:
                    self._reached_old_records = True
                    continue
            else:
                if pendulum.parse(record[self.cursor_field]) < self._start_datetime:
                    continue
            yield record


class Campaigns(KlaviyoStreamV1):
    """Docs: https://developers.klaviyo.com/en/reference/get-campaigns"""

    def path(self, **kwargs) -> str:
        return "campaigns"


class Lists(KlaviyoStreamV1):
    """Docs: https://developers.klaviyo.com/en/reference/get-lists"""

    max_retries = 10

    def path(self, **kwargs) -> str:
        return "lists"


class GlobalExclusions(ReverseIncrementalKlaviyoStreamV1):
    """Docs: https://developers.klaviyo.com/en/reference/get-global-exclusions"""

    page_size = 5000  # the maximum value allowed by API
    cursor_field = "timestamp"
    primary_key = "email"

    def path(self, **kwargs) -> str:
        return "people/exclusions"


class Metrics(KlaviyoStreamV1):
    """Docs: https://developers.klaviyo.com/en/reference/get-metrics"""

    def path(self, **kwargs) -> str:
        return "metrics"


class Events(IncrementalKlaviyoStreamV1):
    """Docs: https://developers.klaviyo.com/en/reference/metrics-timeline"""

    cursor_field = "timestamp"

    def path(self, **kwargs) -> str:
        return "metrics/timeline"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """:return an iterable containing each record in the response"""

        response_json = response.json()
        for record in response_json.get("data", []):
            flow = record["event_properties"].get("$flow")
            flow_message_id = record["event_properties"].get("$message")

            record["flow_id"] = flow
            record["flow_message_id"] = flow_message_id
            record["campaign_id"] = flow_message_id if not flow else None

            yield record


class Flows(ReverseIncrementalKlaviyoStreamV1):
    cursor_field = "created"

    def path(self, **kwargs) -> str:
        return "flows"


class EmailTemplates(KlaviyoStreamV1):
    """
    Docs: https://developers.klaviyo.com/en/v1-2/reference/get-templates
    """

    def path(self, **kwargs) -> str:
        return "email-templates"
