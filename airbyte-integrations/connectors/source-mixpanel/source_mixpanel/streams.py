# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
import time
from abc import ABC
from datetime import timedelta
from functools import cache
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from pendulum import Date
from requests.auth import AuthBase

from airbyte_cdk import BackoffStrategy
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_mixpanel.property_transformation import transform_property_names

from .utils import fix_date_time


class MixpanelStreamBackoffStrategy(BackoffStrategy):
    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response):
            retry_after = response_or_exception.headers.get("Retry-After")
            if retry_after:
                self._logger.debug(f"API responded with `Retry-After` header: {retry_after}")
                return float(retry_after)
        return None


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
    def url_base(self):
        prefix = "eu." if self.region == "EU" else ""
        return f"https://{prefix}mixpanel.com/api/query/"

    @property
    def reqs_per_hour_limit(self):
        # https://help.mixpanel.com/hc/en-us/articles/115004602563-Rate-Limits-for-Export-API-Endpoints#api-export-endpoint-rate-limits
        return self._reqs_per_hour_limit

    @reqs_per_hour_limit.setter
    def reqs_per_hour_limit(self, value):
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
        export_lookback_window: int = 0,  # in seconds
        select_properties_by_default: bool = True,
        project_id: int = None,
        reqs_per_hour_limit: int = DEFAULT_REQS_PER_HOUR_LIMIT,
        **kwargs,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.date_window_size = date_window_size
        self.attribution_window = attribution_window
        self.export_lookback_window = export_lookback_window
        self.additional_properties = select_properties_by_default
        self.region = region
        self.project_timezone = project_timezone
        self.project_id = project_id
        self._reqs_per_hour_limit = reqs_per_hour_limit
        super().__init__(authenticator=authenticator)

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

        if self.reqs_per_hour_limit > 0:
            # we skip this block, if self.reqs_per_hour_limit = 0,
            # in all other cases wait for X seconds to match API limitations
            self.logger.info(f"Sleep for {3600 / self.reqs_per_hour_limit} seconds to match API limitations after reading from {self.name}")
            time.sleep(3600 / self.reqs_per_hour_limit)

    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        return MixpanelStreamBackoffStrategy(stream=self)

    def get_error_handler(self) -> Optional[ErrorHandler]:
        return ExportErrorHandler(logger=self.logger, stream=self)

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
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        if self.project_id:
            return {"project_id": str(self.project_id)}
        return {}


class IncrementalMixpanelStream(MixpanelStream, ABC):
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        updated_state = latest_record.get(self.cursor_field)
        if updated_state:
            state_value = current_stream_state.get(self.cursor_field)
            if state_value:
                updated_state = max(updated_state, state_value)
            current_stream_state[self.cursor_field] = updated_state
        return current_stream_state


class DateSlicesMixin:
    raise_on_http_errors = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._timezone_mismatch = False

    def parse_response(self, *args, **kwargs):
        if self._timezone_mismatch:
            return []
        yield from super().parse_response(*args, **kwargs)

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # use the latest date between self.start_date and stream_state
        start_date = self.start_date
        cursor_value = None

        if stream_state and self.cursor_field and self.cursor_field in stream_state:
            # Remove time part from state because API accept 'from_date' param in date format only ('YYYY-MM-DD')
            # It also means that sync returns duplicated entries for the date from the state (date range is inclusive)
            cursor_value = stream_state[self.cursor_field]
            # This stream is only used for Export stream, so we use export_lookback_window here
            cursor_value = (pendulum.parse(cursor_value) - timedelta(seconds=self.export_lookback_window)).to_iso8601_string()
            stream_state_date = pendulum.parse(stream_state[self.cursor_field])
            start_date = max(start_date, stream_state_date.date())

        final_lookback_window = max(self.export_lookback_window, self.attribution_window * 24 * 60 * 60)
        # move start_date back <attribution_window> days to sync data since that time as well
        start_date = start_date - timedelta(seconds=final_lookback_window)

        # end_date cannot be later than today
        end_date = min(self.end_date, pendulum.today(tz=self.project_timezone).date())

        while start_date <= end_date:
            if self._timezone_mismatch:
                return
            current_end_date = start_date + timedelta(days=self.date_window_size - 1)  # -1 is needed because dates are inclusive
            stream_slice = {
                "start_date": str(start_date),
                "end_date": str(min(current_end_date, end_date)),
            }
            if cursor_value:
                stream_slice[self.cursor_field] = cursor_value
            yield stream_slice
            # add 1 additional day because date range is inclusive
            start_date = current_end_date + timedelta(days=1)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        return {
            **params,
            "from_date": stream_slice["start_date"],
            "to_date": stream_slice["end_date"],
        }


class ExportErrorHandler(HttpStatusErrorHandler):
    """
    Custom error handler for handling export errors specific to Mixpanel streams.

    This handler addresses:
    - 400 status code with "to_date cannot be later than today" message, indicating a potential timezone mismatch.
    - ConnectionResetError during response parsing, indicating a need to retry the request.

    If the response does not match these specific cases, the handler defers to the parent class's implementation.

    Attributes:
        stream (HttpStream): The HTTP stream associated with this error handler.
    """

    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            if response_or_exception.status_code == requests.codes.bad_request:
                if "to_date cannot be later than today" in response_or_exception.text:
                    self.stream._timezone_mismatch = True
                    message = (
                        "Your project timezone must be misconfigured. Please set it to the one defined in your Mixpanel project settings. "
                        "Stopping current stream sync."
                    )
                    return ErrorResolution(
                        response_action=ResponseAction.IGNORE,
                        failure_type=FailureType.config_error,
                        error_message=message,
                    )
                if "Unable to authenticate request" in response_or_exception.text:
                    message = (
                        f"Your credentials might have expired. Please update your config with valid credentials."
                        f" See more details: {response_or_exception.text}"
                    )
                    return ErrorResolution(
                        response_action=ResponseAction.FAIL,
                        failure_type=FailureType.config_error,
                        error_message=message,
                    )
            if response_or_exception.status_code == 402:
                message = f"Unable to perform a request. Payment Required: {response_or_exception.json()['error']}"
                return ErrorResolution(
                    response_action=ResponseAction.FAIL,
                    failure_type=FailureType.transient_error,
                    error_message=message,
                )
            try:
                # trying to parse response to avoid ConnectionResetError and retry if it occurs
                self.stream.iter_dicts(response_or_exception.iter_lines(decode_unicode=True))
            except ConnectionResetError:
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",
                )
        return super().interpret_response(response_or_exception)


class ExportSchema(MixpanelStream):
    """
    Export helper stream for dynamic schema extraction.
    :: reqs_per_hour_limit: int - property is set to the value of 1 million,
       to get the sleep time close to the zero, while generating dynamic schema.
       When `reqs_per_hour_limit = 0` - it means we skip this limits.
    """

    primary_key: str = None
    data_field: str = None
    reqs_per_hour_limit: int = 0  # see the docstring

    def path(self, **kwargs) -> str:
        return "events/properties/top"

    def process_response(self, response: requests.Response, **kwargs) -> Iterable[str]:
        """
        response.json() example:
        {
            "$browser": {
                "count": 6
            },
            "$browser_version": {
                "count": 6
            },
            "$current_url": {
                "count": 6
            },
            "mp_lib": {
                "count": 6
            },
            "noninteraction": {
                "count": 6
            },
            "$event_name": {
                "count": 6
            },
            "$duration_s": {},
            "$event_count": {},
            "$origin_end": {},
            "$origin_start": {}
        }
        """
        records = response.json()
        for property_name in records:
            yield property_name

    def iter_dicts(self, lines):
        """
        The incoming stream has to be JSON lines format.
        From time to time for some reason, the one record can be split into multiple lines.
        We try to combine such split parts into one record only if parts go nearby.
        """
        parts = []
        for record_line in lines:
            if record_line == "terminated early":
                self.logger.warning(f"Couldn't fetch data from Export API. Response: {record_line}")
                return
            try:
                yield json.loads(record_line)
            except ValueError:
                parts.append(record_line)
            else:
                parts = []

            if len(parts) > 1:
                try:
                    yield json.loads("".join(parts))
                except ValueError:
                    pass
                else:
                    parts = []


class Export(DateSlicesMixin, IncrementalMixpanelStream):
    """Export event data as it is received and stored within Mixpanel, complete with all event properties
     (including distinct_id) and the exact timestamp the event was fired.

    API Docs: https://developer.mixpanel.com/reference/export
    Endpoint: https://data.mixpanel.com/api/2.0/export

    Raw Export API Rate Limit (https://help.mixpanel.com/hc/en-us/articles/115004602563-Rate-Limits-for-API-Endpoints):
     A maximum of 100 concurrent queries,
     3 queries per second and 60 queries per hour.
    """

    primary_key: str = None
    cursor_field: str = "time"

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    @property
    def url_base(self):
        prefix = "-eu" if self.region == "EU" else ""
        return f"https://data{prefix}.mixpanel.com/api/2.0/"

    def path(self, **kwargs) -> str:
        return "export"

    def get_error_handler(self) -> Optional[ErrorHandler]:
        return ExportErrorHandler(logger=self.logger, stream=self)

    def iter_dicts(self, lines):
        """
        The incoming stream has to be JSON lines format.
        From time to time for some reason, the one record can be split into multiple lines.
        We try to combine such split parts into one record only if parts go nearby.
        """
        parts = []
        for record_line in lines:
            if record_line == "terminated early":
                self.logger.warning(f"Couldn't fetch data from Export API. Response: {record_line}")
                return
            try:
                yield json.loads(record_line)
            except ValueError:
                parts.append(record_line)
            else:
                parts = []

            if len(parts) > 1:
                try:
                    yield json.loads("".join(parts))
                except ValueError:
                    pass
                else:
                    parts = []

    def process_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """Export API return response in JSONL format but each line is a valid JSON object
        Raw item example:
            {
                "event": "Viewed E-commerce Page",
                "properties": {
                    "time": 1623860880,
                    "distinct_id": "1d694fd9-31a5-4b99-9eef-ae63112063ed",
                    "$browser": "Chrome",                                           -> will be renamed to "browser"
                    "$browser_version": "91.0.4472.101",
                    "$current_url": "https://unblockdata.com/solutions/e-commerce/",
                    "$insert_id": "c5eed127-c747-59c8-a5ed-d766f48e39a4",
                    "$mp_api_endpoint": "api.mixpanel.com",
                    "mp_lib": "Segment: analytics-wordpress",
                    "mp_processing_time_ms": 1623886083321,
                    "noninteraction": true
                }
            }
        """

        # We prefer response.iter_lines() to response.text.split_lines() as the later can missparse text properties embeding linebreaks
        for record in self.iter_dicts(response.iter_lines(decode_unicode=True)):
            # transform record into flat dict structure
            item = {"event": record["event"]}
            properties = record["properties"]
            for result in transform_property_names(properties.keys()):
                # Convert all values to string (this is default property type)
                # because API does not provide properties type information
                item[result.transformed_name] = str(properties[result.source_name])

            # convert timestamp to datetime string
            item["time"] = pendulum.from_timestamp(int(item["time"]), tz="UTC").to_iso8601_string()

            yield item

    @cache
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.

        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.
        """

        schema = super().get_json_schema()

        # Set whether to allow additional properties for engage and export endpoints
        # Event and Engage properties are dynamic and depend on the properties provided on upload,
        #   when the Event or Engage (user/person) was created.
        schema["additionalProperties"] = self.additional_properties

        # read existing Export schema from API
        schema_properties = ExportSchema(**self.get_stream_params()).read_records(sync_mode=SyncMode.full_refresh)
        for result in transform_property_names(schema_properties):
            # Schema does not provide exact property type
            # string ONLY for event properties (no other datatypes)
            # Reference: https://help.mixpanel.com/hc/en-us/articles/360001355266-Event-Properties#field-size-character-limits-for-event-properties
            schema["properties"][result.transformed_name] = {"type": ["null", "string"]}

        return schema

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        # additional filter by timestamp because required start date and end date only allow to filter by date
        cursor_param = stream_slice.get(self.cursor_field)
        if cursor_param:
            timestamp = int(pendulum.parse(cursor_param).timestamp())
            params["where"] = f'properties["$time"]>=datetime({timestamp})'
        return params

    def request_kwargs(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"stream": True}
