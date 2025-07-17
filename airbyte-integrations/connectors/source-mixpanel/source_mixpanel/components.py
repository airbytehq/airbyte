# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import dpath.util
import pendulum
import requests

from airbyte_cdk.models import AirbyteMessage, FailureType, SyncMode, Type
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import ExponentialBackoffStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, ResponseAction
from source_mixpanel.backoff_strategy import DEFAULT_API_BUDGET
from source_mixpanel.property_transformation import transform_property_names
from source_mixpanel.source import raise_config_error


class MixpanelHttpRequester(HttpRequester):
    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.api_budget = DEFAULT_API_BUDGET
        self.error_handler.backoff_strategies = ExponentialBackoffStrategy(factor=30, config=self.config, parameters=parameters)
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


class EngagePropertiesDpathExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        properties = next(super().extract_records(response))
        _properties = []
        for field_name in properties:
            properties[field_name].update({"name": field_name})
            _properties.append(properties[field_name])

        yield _properties


class ExportHttpRequester(MixpanelHttpRequester):
    cursor_field = "time"
    default_project_timezone = "US/Pacific"

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)

        self._from_date_lookback_window = max(
            self.config.get("export_lookback_window", 0), self.config.get("attribution_window", 0) * 24 * 60 * 60
        )
        self._to_date_lookback_window = 1
        self._time_lookback_window = self.config.get("export_lookback_window", 0)

        if self.config.get("end_date"):
            self._validate_end_date()
            self._end_date = pendulum.parse(self.config.get("end_date")).date()
        else:
            self._end_date = (
                pendulum.today(tz=self.config.get("project_timezone", self.default_project_timezone))
                - timedelta(days=self._to_date_lookback_window)
            ).date()

    def _validate_end_date(self) -> None:
        date_str = self.config.get("end_date")
        try:
            return pendulum.parse(date_str).date()
        except pendulum.parsing.exceptions.ParserError as e:
            raise_config_error(f"time data '{date_str}' does not match format '%Y-%m-%dT%H:%M:%SZ'", e)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        request_params = super().get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        start_time = stream_slice.cursor_slice.get("start_time")

        from_date_value = (pendulum.parse(start_time) - timedelta(seconds=self._from_date_lookback_window)).date()
        to_date_value = self._end_date
        time_value = int((pendulum.parse(start_time) - timedelta(seconds=self._time_lookback_window)).timestamp())

        request_params["from_date"] = from_date_value.format("YYYY-MM-DD")
        request_params["to_date"] = to_date_value.format("YYYY-MM-DD")
        request_params["where"] = f'properties["$time"]>=datetime({time_value})'

        return request_params


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


class ExportDpathExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        # We prefer response.iter_lines() to response.text.split_lines() as the later can missparse text properties embeding linebreaks
        records = list(iter_dicts(response.iter_lines(decode_unicode=True)))
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


class PropertiesTransformation(RecordTransformation):
    properties_field: str = None

    def __init__(self, properties_field: str = None) -> None:
        self.properties_field = properties_field

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        updated_record = {}
        to_transform = record[self.properties_field] if self.properties_field else record

        for result in transform_property_names(to_transform.keys()):
            updated_record[result.transformed_name] = to_transform[result.source_name]

        if self.properties_field:
            record[self.properties_field].clear()
            record[self.properties_field].update(updated_record)
        else:
            record.clear()
            record.update(updated_record)
