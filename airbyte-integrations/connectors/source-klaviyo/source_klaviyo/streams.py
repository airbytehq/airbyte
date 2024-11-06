#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import urllib.parse
from abc import ABC, abstractmethod
import json
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


class KlaviyoStreamLatest(HttpStream, ABC):
    """Base stream for api version v2023-02-22"""

    url_base = "https://a.klaviyo.com/api/"
    primary_key = "id"
    page_size = 100
    include = None

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
            "Revision": "2024-05-15",
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
        params = {}
        if self.page_size:
            params["page[size]"] = self.page_size
        if self.include:
            params["include"] = self.include
        return params

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

    def map_record(self, record: Mapping):
        record[self.cursor_field] = record["attributes"][self.cursor_field]
        return record

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.
        :return str: The name of the cursor field.
        """

    def request_params(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Mapping[str, Any] = None,
            **kwargs):
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


class IncrementalKlaviyoStreamLatestWithArchivedRecords(IncrementalKlaviyoStreamLatest, ABC):

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        return [{"archived": value} for value in [False, True]]

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        archived = latest_record.get("attributes", {}).get("archived", False)
        if archived:
            current_stream_cursor_value = current_stream_state.get("archived", {}).get(self.cursor_field, self._start_ts)
            latest_record_cursor_value = latest_record[self.cursor_field]
            latest_cursor = max(pendulum.parse(latest_record_cursor_value), pendulum.parse(current_stream_cursor_value))
            current_stream_state["archived"] = {self.cursor_field: str(latest_cursor)}
            return current_stream_state
        else:
            return super().get_updated_state(current_stream_state, latest_record)

    def request_params(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Mapping[str, Any] = None,
            **kwargs):
        current_stream_state = stream_state
        if stream_state.get("archived"):
            current_stream_state = stream_state.get("archived", {})
        params = super().request_params(current_stream_state, stream_slice, next_page_token)
        archived = stream_slice.get("archived", False)
        if archived:
            archived_filter = "equals(archived,true)"
            if "filter" in params and archived_filter not in params["filter"]:
                params["filter"] = f"and({params['filter']},{archived_filter})"
            elif "filter" not in params:
                params["filter"] = archived_filter
        return params


class Profiles(IncrementalKlaviyoStreamLatest):
    """Docs: https://developers.klaviyo.com/en/reference/get_profiles"""

    cursor_field = "updated"
    page_size = 100

    def path(self, *args, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return "profiles"

    def request_params(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Mapping[str, Any] = None,
            **kwargs):
        """Add incremental filters"""
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["additional-fields[profile]"] = "predictive_analytics,subscriptions"
        return params


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
        self._start_sync = int(pendulum.now().timestamp())

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        """How often to checkpoint state (i.e: emit a STATE message)"""
        return self.page_size

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.
        :return str: The name of the cursor field.
        """

    @property
    def look_back_window_in_seconds(self) -> Optional[int]:
        """
        How long in the past we can re fetch data to ensure we don't miss records

        :returns int: The window in seconds
        """
        return None

    def request_params(self, stream_state=None, **kwargs):
        """Add incremental filters"""
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)

        params["sort"] = "asc"
        if not params.get("since"):  # skip state filter if already have one from pagination
            state_ts = int(stream_state.get(self.cursor_field, 0))
            last_next_token = stream_state.get("last_next_token", None)
            if last_next_token is not None:
                token_timestamp = int(str(last_next_token).split(":")[0])
                # if the token stamp is equal to the state timestamp then we will use the next token as since value
                # This will allow us to recover from extreme cases where there millions of events for the same timestamp.
                if token_timestamp == state_ts:
                    params["since"] = last_next_token
                    return params

            if state_ts > 0 and self.look_back_window_in_seconds:
                state_ts -= self.look_back_window_in_seconds
            params["since"] = max(state_ts, self._start_ts)

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

        new_value = max(latest_record, state_ts)
        new_value = min(new_value, self._start_sync)
        return {self.cursor_field: new_value}

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

        data = decoded_response.get("data", [{}]) or [{}]
        self.logger.info("Last timestamp -> " + str(data[-1].get("timestamp", "No timestamp")))

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


class Campaigns(IncrementalKlaviyoStreamLatest):
    """Docs: https://developers.klaviyo.com/en/reference/get-campaigns"""

    cursor_field = "updated_at"
    page_size = None
    current_channel = None
    include = "campaign-messages,tags"

    def path(self, *args, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return "campaigns"

    def stream_slices(
            self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        archived_flags = [False, True]
        message_channels = ["email", "sms"]
        return [{"archived": flag, "channel": channel} for flag in archived_flags for channel in message_channels]

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        archived = latest_record.get("attributes", {}).get("archived", False)
        updated_state = super().get_updated_state(current_stream_state, latest_record)
        if archived:
            current_stream_cursor_value = current_stream_state.get("archived", {}).get(self.cursor_field, self._start_ts)
            latest_record_cursor_value = latest_record[self.cursor_field]
            latest_cursor = max(pendulum.parse(latest_record_cursor_value), pendulum.parse(current_stream_cursor_value))
            current_stream_state["archived"] = {self.current_channel: {self.cursor_field: latest_cursor}}
        else:
            current_stream_state[self.current_channel] = updated_state
        return current_stream_state

    def request_params(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Mapping[str, Any] = None,
            **kwargs):
        archived = stream_slice.get("archived", False)
        channel = stream_slice.get("channel", False)
        if archived:
            current_stream_state = stream_state.get("archived", {}).get(channel, {})
        else:
            current_stream_state = stream_state.get(channel, {})
        params = super().request_params(current_stream_state, stream_slice, next_page_token)

        self.current_channel = channel
        channel_filter = f"equals(messages.channel,'{channel}')"
        if "filter" in params and channel_filter not in params["filter"]:
            params["filter"] = f"{params['filter']},{channel_filter}"
        elif "filter" not in params:
            params["filter"] = channel_filter

        if archived:
            archived_filter = "equals(archived,true)"
            if "filter" in params and archived_filter not in params["filter"]:
                params["filter"] = f"{params['filter']},{archived_filter}"
            elif "filter" not in params:
                params["filter"] = archived_filter
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        included = response_json.get("included", [])
        campaign_messages = [record for record in included if record["type"] == "campaign-message"]
        campaign_message_cache = {record["id"]: record for record in campaign_messages}
        for record in response_json.get("data", []):
            relationships = record.get("relationships", {})
            campaign_messages_data = relationships.get("campaign-messages", {}).get("data", [])
            for idx, campaign_message in enumerate(campaign_messages_data):
                campaign_message_id = campaign_message.get("id", None)
                if campaign_message_id and campaign_message_id in campaign_message_cache:
                    message = campaign_message_cache.get(campaign_message_id)
                    from_email = message.get("attributes", {}).get("content", {}).get("from_email", None)
                    if from_email:
                        record[f"from_email_{idx}"] = from_email

            record = self.map_record(record)
            yield record

class Lists(IncrementalKlaviyoStreamLatest):
    """Docs: https://developers.klaviyo.com/en/reference/get-lists"""

    cursor_field = "updated"
    max_retries = 10
    page_size = None
    include = "tags"

    def path(self, **kwargs) -> str:
        return "lists"


class GlobalExclusions(Profiles):
    """Docs: https://developers.klaviyo.com/en/reference/get-global-exclusions"""
    suppression_fields = ["attributes", "subscriptions", "email", "marketing", "suppression"]

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """:return an iterable containing each record in the response"""
        response_json = response.json()
        for record in response_json.get("data", []):  # API returns records in a container array "data"
            record = self.map_record(record)
            if record:
                yield record

    def map_record(self, record: Mapping):
        nested_record = record
        for field in self.suppression_fields:
            if field not in nested_record:
                return None
            nested_record = nested_record[field]
        if not nested_record:
            return None

        record[self.cursor_field] = record["attributes"][self.cursor_field]
        return record


class Metrics(KlaviyoStreamLatest):
    """Docs: https://developers.klaviyo.com/en/reference/get-metrics"""
    page_size = None

    def path(self, **kwargs) -> str:
        return "metrics"


FLATTEN_LEVELS: int = 2


def process_record(record):
    processed_record = record

    # Recursively traverse record dict and string-ify all json values in the 3rd level
    def flatten_dict(rec, level):
        for key, value in rec.items():
            if isinstance(value, dict):
                if level > FLATTEN_LEVELS:
                    rec[key] = json.dumps(value)
                else:
                    flatten_dict(value, level + 1)

    flatten_dict(processed_record, 1)
    return processed_record


class Events(IncrementalKlaviyoStreamLatest):
    """Docs: https://developers.klaviyo.com/en/reference/metrics-timeline"""

    cursor_field = "datetime"
    page_size = None
    include = "attributions,metric,profile"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_next_token = None

    def path(self, **kwargs) -> str:
        return "events"

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        return 5000

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """:return an iterable containing each record in the response"""

        response_json = response.json()
        profiles = [record for record in response_json.get("included", []) if record["type"] == "profile"]
        profile_cache = {record["id"]: record for record in profiles}
        for record in response_json.get("data", []):
            attributes = record["attributes"]
            event_properties = attributes.get("event_properties", {})
            flow = event_properties.get("$flow")
            flow_message_id = event_properties.get("$message")
            record["flow_id"] = flow
            record["flow_message_id"] = flow_message_id
            record["campaign_id"] = flow_message_id if not flow else None
            profiles_data = record.get("relationships", {}).get("profile", {}).get("data", None)
            if profiles_data:
                profile_id = profiles_data.get("id", None)
                if profile_id and profile_id in profile_cache:
                    profile = profile_cache.get(profile_id)
                    profile_email = profile.get("attributes", {}).get("email", None)
                    if profile_email:
                        record["profile_email"] = profile_email
            self.map_record(record)
            yield process_record(record)


class Flows(IncrementalKlaviyoStreamLatestWithArchivedRecords):
    cursor_field = "updated"
    page_size = None
    include = "flow-actions,tags"

    def path(self, *args, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return "flows"


class EmailTemplates(IncrementalKlaviyoStreamLatest):
    """
    Docs: https://developers.klaviyo.com/en/v1-2/reference/get-templates
    """

    page_size = None
    cursor_field = "updated"

    def path(self, **kwargs) -> str:
        return "templates"


class Segments(IncrementalKlaviyoStreamLatest):
    """
    Docs: https://developers.klaviyo.com/en/v1-2/reference/get-templates
    """

    page_size = None
    cursor_field = "updated"

    def path(self, **kwargs) -> str:
        return "segments"


class SegmentsProfiles(KlaviyoStreamLatest):
    parent_id: str = "id"
    page_size = 100

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self._start_ts = start_date

    def stream_slices(
            self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream = Segments(api_key=self._api_key, start_date=self._start_ts)
        slices = parent_stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for _slice in slices:
            yield from parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=_slice)

    def request_params(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Mapping[str, Any] = None,
            **kwargs):
        """Add incremental filters"""
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["additional-fields[profile]"] = "subscriptions,predictive_analytics"
        return params

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"segments/{stream_slice[self.parent_id]}/profiles"
