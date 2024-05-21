# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import time
from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import dpath.util
import requests
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement
from airbyte_cdk.sources.declarative.schema import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import _default_file_path
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState

from .source import SourceMixpanel
from .streams.engage import EngageSchema


class MixpanelHttpRequester(HttpRequester):
    reqs_per_hour_limit = 60
    is_first_request = True

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

    def send_request(self, **kwargs) -> Optional[requests.Response]:

        if self.reqs_per_hour_limit:
            if self.is_first_request:
                self.is_first_request = False
            else:
                # we skip this block, if self.reqs_per_hour_limit = 0,
                # in all other cases wait for X seconds to match API limitations
                # https://help.mixpanel.com/hc/en-us/articles/115004602563-Rate-Limits-for-Export-API-Endpoints#api-export-endpoint-rate-limits
                self.logger.info(
                    f"Sleep for {3600 / self.reqs_per_hour_limit} seconds to match API limitations after reading from {self.name}"
                )
                time.sleep(3600 / self.reqs_per_hour_limit)

        return super().send_request(**kwargs)


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

    def next_page_token(self, response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
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

        if self._total and page_number is not None and self._total > self.page_size * (page_number + 1):
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
