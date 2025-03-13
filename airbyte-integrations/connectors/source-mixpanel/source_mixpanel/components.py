# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import logging
from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import dpath.util
import pendulum
import requests

from airbyte_cdk.models import AirbyteMessage, FailureType, SyncMode, Type
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import ConstantBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement
from airbyte_cdk.sources.declarative.schema import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import _default_file_path
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, ResponseAction
from source_mixpanel.backoff_strategy import DEFAULT_API_BUDGET
from source_mixpanel.property_transformation import transform_property_names
from source_mixpanel.streams.export import ExportSchema

from .source import SourceMixpanel
from .streams.engage import EngageSchema


class MixpanelHttpRequester(HttpRequester):
    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.api_budget = DEFAULT_API_BUDGET
        self.error_handler.backoff_strategies = ConstantBackoffStrategy(
            backoff_time_in_seconds=60 * 2, config=self.config, parameters=parameters
        )
        super().__post_init__(parameters)

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        project_id = self.config.get("credentials", {}).get("project_id")
        return {"project_id": project_id} if project_id else {}

    def _request_params(
        self,
        stream_state: Optional[StreamState],
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        extra_params: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Flatten extra_params if it contains pagination information
        """
        next_page_token = None  # reset it, pagination data is in extra_params
        if extra_params:
            page = extra_params.pop("page", {})
            extra_params.update(page)
        return super()._request_params(stream_state, stream_slice, next_page_token, extra_params)


class AnnotationsHttpRequester(MixpanelHttpRequester):
    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {}


class FunnelsHttpRequester(MixpanelHttpRequester):
    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params["unit"] = "day"
        return params


class EngagesHttpRequester(MixpanelHttpRequester):
    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if "start_time" in stream_slice:
            params["where"] = f'properties["$last_seen"] >= "{stream_slice["start_time"]}"'
        elif "start_date" in self.config:
            params["where"] = f'properties["$last_seen"] >= "{self.config["start_date"]}"'
        return params


class CohortMembersSubstreamPartitionRouter(SubstreamPartitionRouter):
    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # https://developer.mixpanel.com/reference/engage-query
        cohort_id = stream_slice["id"]
        return {"filter_by_cohort": f'{{"id":{cohort_id}}}'}


class EngageTransformation(RecordTransformation):
    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        """
        - flatten $properties fields
        - remove leading '$'
        """
        record["distinct_id"] = record.pop("$distinct_id")
        properties = record.pop("$properties")
        for property_name in properties:
            this_property_name = property_name
            if property_name.startswith("$"):
                # Just remove leading '$' for 'reserved' mixpanel properties name, example:
                # from API: '$browser'
                # to stream: 'browser'
                this_property_name = this_property_name[1:]
            record[this_property_name] = properties[property_name]

        return record


class RevenueDpathExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        """
        response.json() example:
        {
            'computed_at': '2021-07-03T12:43:48.889421+00:00',
            'results': {
                '$overall': {       <-- should be skipped
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                '2021-06-01': {
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                '2021-06-02': {
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                ...
            },
            'session_id': '162...',
            'status': 'ok'
        }
        """
        new_records = []
        for record in super().extract_records(response):
            for date_entry in record:
                if date_entry != "$overall":
                    list.append(new_records, {"date": date_entry, **record[date_entry]})
        return new_records


class FunnelsDpathExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        """
        response.json() example:
        {
            'computed_at': '2021-07-03T12:43:48.889421+00:00',
            'results': {
                '$overall': {       <-- should be skipped
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                '2021-06-01': {
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                ...
            },
            'session_id': '162...',
            'status': 'ok'
        }
        """
        new_records = []
        for record in super().extract_records(response):
            for date_entry in record:
                list.append(new_records, {"date": date_entry, **record[date_entry]})
        return new_records


class FunnelsSubstreamPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Add 'funnel_name' to the slice, the rest code is exactly the same as in super().stream_slices(...)
        Remove empty 'parent_slice' attribute to be compatible with LegacyToPerPartitionStateMigration
        """
        if not self.parent_stream_configs:
            yield from []
        else:
            for parent_stream_config in self.parent_stream_configs:
                parent_stream = parent_stream_config.stream
                parent_field = parent_stream_config.parent_key.eval(self.config)  # type: ignore # parent_key is always casted to an interpolated string
                partition_field = parent_stream_config.partition_field.eval(self.config)  # type: ignore # partition_field is always casted to an interpolated string
                for parent_stream_slice in parent_stream.stream_slices(
                    sync_mode=SyncMode.full_refresh, cursor_field=None, stream_state=None
                ):
                    empty_parent_slice = True
                    parent_partition = parent_stream_slice.partition if parent_stream_slice else {}

                    for parent_record in parent_stream.read_records(
                        sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
                    ):
                        # Skip non-records (eg AirbyteLogMessage)
                        if isinstance(parent_record, AirbyteMessage):
                            if parent_record.type == Type.RECORD:
                                parent_record = parent_record.record.data
                            else:
                                continue
                        elif isinstance(parent_record, Record):
                            parent_record = parent_record.data
                        try:
                            partition_value = dpath.util.get(parent_record, parent_field)
                        except KeyError:
                            pass
                        else:
                            empty_parent_slice = False
                            yield StreamSlice(
                                partition={partition_field: partition_value},
                                cursor_slice={"funnel_name": parent_record.get("name")},
                            )
                    # If the parent slice contains no records,
                    if empty_parent_slice:
                        yield from []


@dataclass
class EngagePaginationStrategy(PageIncrement):
    """
    Engage stream uses 2 params for pagination:
    session_id - returned after first request
    page - incremental page number
    """

    _total = 0

    def next_page_token(
        self,
        response: requests.Response,
        last_page_size: int,
        last_record: Optional[Record],
        last_page_token_value: Optional[Any],
    ) -> Optional[Any]:
        """
        Determines page and subpage numbers for the `items` stream

        Attributes:
            response: Contains `boards` and corresponding lists of `items` for each `board`
            last_records: Parsed `items` from the response
        """
        decoded_response = response.json()
        page_number = decoded_response.get("page")
        total = decoded_response.get("total")  # exist only on first page
        if total:
            self._total = total

        if self._total and page_number is not None and self._total > self._page_size * (page_number + 1):
            return {"session_id": decoded_response.get("session_id"), "page": page_number + 1}
        else:
            self._total = None
            return None

    def reset(self) -> None:
        super().reset()
        self._total = 0


class EngageJsonFileSchemaLoader(JsonFileSchemaLoader):
    """Engage schema combines static and dynamic approaches"""

    schema: Mapping[str, Any]

    def __post_init__(self, parameters: Mapping[str, Any]):
        if not self.file_path:
            self.file_path = _default_file_path()
        self.file_path = InterpolatedString.create(self.file_path, parameters=parameters)
        self.schema = {}

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Dynamically load additional properties from API
        Add cache to reduce a number of API calls because get_json_schema()
        is called for each extracted record
        """

        if self.schema:
            return self.schema

        schema = super().get_json_schema()

        types = {
            "boolean": {"type": ["null", "boolean"]},
            "number": {"type": ["null", "number"], "multipleOf": 1e-20},
            # no format specified as values can be "2021-12-16T00:00:00", "1638298874", "15/08/53895"
            "datetime": {"type": ["null", "string"]},
            "object": {"type": ["null", "object"], "additionalProperties": True},
            "list": {"type": ["null", "array"], "required": False, "items": {}},
            "string": {"type": ["null", "string"]},
        }

        params = {"authenticator": SourceMixpanel.get_authenticator(self.config), "region": self.config.get("region")}
        project_id = self.config.get("credentials", {}).get("project_id")
        if project_id:
            params["project_id"] = project_id

        schema["additionalProperties"] = self.config.get("select_properties_by_default", True)

        # read existing Engage schema from API
        schema_properties = EngageSchema(**params).read_records(sync_mode=SyncMode.full_refresh)
        for property_entry in schema_properties:
            property_name: str = property_entry["name"]
            property_type: str = property_entry["type"]
            if property_name.startswith("$"):
                # Just remove leading '$' for 'reserved' mixpanel properties name, example:
                # from API: '$browser'
                # to stream: 'browser'
                property_name = property_name[1:]
            # Do not overwrite 'standard' hard-coded properties, add 'custom' properties
            if property_name not in schema["properties"]:
                schema["properties"][property_name] = types.get(property_type, {"type": ["null", "string"]})
        self.schema = schema
        return schema


def iter_dicts(lines, logger=logging.getLogger("airbyte")):
    """
    The incoming stream has to be JSON lines format.
    From time to time for some reason, the one record can be split into multiple lines.
    We try to combine such split parts into one record only if parts go nearby.
    """
    parts = []
    for record_line in lines:
        if record_line == "terminated early":
            logger.warning(f"Couldn't fetch data from Export API. Response: {record_line}")
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


class ExportJsonFileSchemaLoader(JsonFileSchemaLoader):
    def __post_init__(self, parameters: Mapping[str, Any]):
        if not self.file_path:
            self.file_path = _default_file_path()
        self.file_path = InterpolatedString.create(self.file_path, parameters=parameters)
        self.schema = {}

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.

        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.
        """

        schema = super().get_json_schema()
        params = {
            "authenticator": SourceMixpanel.get_authenticator(self.config),
            "region": self.config.get("region"),
            "project_id": self.config.get("credentials").get("project_id"),
        }

        # Set whether to allow additional properties for engage and export endpoints
        # Event and Engage properties are dynamic and depend on the properties provided on upload,
        #   when the Event or Engage (user/person) was created.
        schema["additionalProperties"] = True

        # read existing Export schema from API
        schema_properties = ExportSchema(**params).read_records(sync_mode=SyncMode.full_refresh)
        for result in transform_property_names(schema_properties):
            # Schema does not provide exact property type
            # string ONLY for event properties (no other datatypes)
            # Reference: https://help.mixpanel.com/hc/en-us/articles/360001355266-Event-Properties#field-size-character-limits-for-event-properties
            schema["properties"][result.transformed_name] = {"type": ["null", "string"]}

        return schema


class ExportDpathExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
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
        records = []
        for record in iter_dicts(response.iter_lines(decode_unicode=True)):
            # transform record into flat dict structure
            item = {"event": record["event"]}
            properties = record["properties"]
            for result in transform_property_names(properties.keys()):
                # Convert all values to string (this is default property type)
                # because API does not provide properties type information
                item[result.transformed_name] = str(properties[result.source_name])

            # convert timestamp to datetime string
            item["time"] = pendulum.from_timestamp(int(item["time"]), tz="UTC").to_iso8601_string()

            records.append(item)

        return records


class ExportErrorHandler(DefaultErrorHandler):
    """
    Custom error handler for handling export errors specific to Mixpanel streams.

    This handler addresses:
    - 400 status code with "to_date cannot be later than today" message, indicating a potential timezone mismatch.
    - ConnectionResetError during response parsing, indicating a need to retry the request.

    If the response does not match these specific cases, the handler defers to the parent class's implementation.

    """

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            try:
                # trying to parse response to avoid ConnectionResetError and retry if it occurs
                iter_dicts(response_or_exception.iter_lines(decode_unicode=True))
            except ConnectionResetError:
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",
                )

        return super().interpret_response(response_or_exception)
