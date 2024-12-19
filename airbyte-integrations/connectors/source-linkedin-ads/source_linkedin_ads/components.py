#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import datetime
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import urlencode

import pendulum
import requests
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.incremental import CursorFactory, DatetimeBasedCursor, PerPartitionCursor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import SinglePartitionRouter
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
    RequestInput,
)
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.transformations import AddFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from airbyte_cdk.sources.streams.http.http import BODY_REQUEST_METHODS
from isodate import Duration, parse_duration

from .utils import ANALYTICS_FIELDS_V2, FIELDS_CHUNK_SIZE, transform_data


class SafeHttpClient(HttpClient):
    """
    A custom HTTP client that safely validates query parameters, ensuring that the symbols ():,% are preserved
    during UTF-8 encoding.
    """

    def _create_prepared_request(
        self,
        http_method: str,
        url: str,
        dedupe_query_params: bool = False,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        json: Optional[Mapping[str, Any]] = None,
        data: Optional[Union[str, Mapping[str, Any]]] = None,
    ) -> requests.PreparedRequest:
        """
        Prepares an HTTP request with optional deduplication of query parameters and safe encoding.
        """
        if dedupe_query_params:
            query_params = self._dedupe_query_params(url, params)
        else:
            query_params = params or {}
        query_params = urlencode(query_params, safe="():,%")
        args = {"method": http_method, "url": url, "headers": headers, "params": query_params}
        if http_method.upper() in BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data
        prepared_request: requests.PreparedRequest = self._session.prepare_request(requests.Request(**args))

        return prepared_request


@dataclass
class SafeEncodeHttpRequester(HttpRequester):
    """
    A custom HTTP requester that ensures safe encoding of query parameters, preserving the symbols ():,% during UTF-8 encoding.
    """

    request_body_json: Optional[RequestInput] = None
    request_headers: Optional[RequestInput] = None
    request_parameters: Optional[RequestInput] = None
    request_body_data: Optional[RequestInput] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        """
        Initializes the request options provider with the provided parameters and any
        configured request components like headers, parameters, or bodies.
        """
        self.request_options_provider = InterpolatedRequestOptionsProvider(
            request_body_data=self.request_body_data,
            request_body_json=self.request_body_json,
            request_headers=self.request_headers,
            request_parameters=self.request_parameters,
            config=self.config,
            parameters=parameters or {},
        )
        super().__post_init__(parameters)

        if self.error_handler is not None and hasattr(self.error_handler, "backoff_strategies"):
            backoff_strategies = self.error_handler.backoff_strategies
        else:
            backoff_strategies = None

        self._http_client = SafeHttpClient(
            name=self.name,
            logger=self.logger,
            error_handler=self.error_handler,
            authenticator=self._authenticator,
            use_cache=self.use_cache,
            backoff_strategy=backoff_strategies,
            disable_retries=self.disable_retries,
            message_repository=self.message_repository,
        )


@dataclass
class AnalyticsDatetimeBasedCursor(DatetimeBasedCursor):
    """
    A cursor for LinkedIn Ads that chunks requests into smaller groups due to the API's limitation
    of a maximum of 20 fields per request. This class splits the date range into slices and ensures
    each chunk includes necessary fields like `dateRange`.
    """

    @staticmethod
    def chunk_analytics_fields(
        fields: List = ANALYTICS_FIELDS_V2,
        fields_chunk_size: int = FIELDS_CHUNK_SIZE,
    ) -> Iterable[List]:
        """
        Chunks the list of available fields into smaller chunks, ensuring required fields are included.
        """

        # Make chunks
        chunks = list((fields[f : f + fields_chunk_size] for f in range(0, len(fields), fields_chunk_size)))

        # Make sure base_fields are within the chunks
        for chunk in chunks:
            if "dateRange" not in chunk:
                chunk.append("dateRange")
            if "pivotValues" not in chunk:
                chunk.append("pivotValues")
        yield from chunks

    def _partition_daterange(
        self, start: datetime.datetime, end: datetime.datetime, step: Union[datetime.timedelta, Duration]
    ) -> List[StreamSlice]:
        """
        Partitions a date range into slices, applying field chunking to ensure API constraints are respected.
        """
        start_field = self._partition_field_start.eval(self.config)
        end_field = self._partition_field_end.eval(self.config)
        dates = []
        while start <= end:
            next_start = self._evaluate_next_start_date_safely(start, step)
            end_date = self._get_date(next_start - self._cursor_granularity, end, min)
            date_slice_with_fields: List = []
            for fields_set in self.chunk_analytics_fields():
                date_range = {
                    "start.day": start.day,
                    "start.month": start.month,
                    "start.year": start.year,
                    "end.day": end_date.day,
                    "end.month": end_date.month,
                    "end.year": end_date.year,
                }

                fields = ",".join(fields_set)
                date_slice_with_fields.append(
                    {
                        start_field: self._format_datetime(start),
                        end_field: self._format_datetime(end_date),
                        "fields": fields,
                        **date_range,
                    }
                )
            dates.append(StreamSlice(partition={}, cursor_slice={"field_date_chunks": date_slice_with_fields}))
            start = next_start
        return dates


@dataclass
class LinkedInAdsRecordExtractor(RecordExtractor):
    """
    Extracts and transforms LinkedIn Ads records, ensuring that 'lastModified' and 'created'
    date-time fields are formatted to RFC3339.
    """

    def _date_time_to_rfc3339(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Converts 'lastModified' and 'created' fields in the record to RFC3339 format.
        """
        for item in ["lastModified", "created"]:
            if record.get(item) is not None:
                record[item] = pendulum.parse(record[item]).to_rfc3339_string()
        return record

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        """
        Extracts and transforms records from an HTTP response.
        """
        for record in transform_data(response.json().get("elements")):
            yield self._date_time_to_rfc3339(record)


@dataclass
class LinkedInAdsCustomRetriever(SimpleRetriever):
    """
    A custom retriever for LinkedIn Ads that reads and merges records for each field date chunk,
    ensuring that records are appropriately grouped by date slices.
    """

    partition_router: Optional[Union[List[StreamSlicer], StreamSlicer]] = field(
        default_factory=lambda: SinglePartitionRouter(parameters={})
    )

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        """
        Initializes the cursor and partition router for the retriever.
        """
        super().__post_init__(parameters)
        self.cursor = self._initialize_cursor()

    def _initialize_cursor(self):
        """
        Initializes the cursor for the retriever, supporting multiple partition routers.
        """
        partition_router = (
            CartesianProductStreamSlicer(self.partition_router, parameters={})
            if isinstance(self.partition_router, list)
            else self.partition_router
        )

        return PerPartitionCursor(
            cursor_factory=CursorFactory(
                lambda: deepcopy(self.stream_slicer),
            ),
            partition_router=partition_router,
        )

    def stream_slices(self) -> Iterable[Optional[StreamSlice]]:
        """
        Generates stream slices based on the cursor's partitioning.
        """
        return self.cursor.stream_slices()

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        """
        Reads and merges records for each field date chunk in the stream slice.
        """
        merged_records = defaultdict(dict)

        self._apply_transformations()

        for field_slice in stream_slice.cursor_slice.get("field_date_chunks", []):
            updated_slice = StreamSlice(partition=stream_slice.partition, cursor_slice={**field_slice})
            for record in super().read_records(records_schema, stream_slice=updated_slice):
                merged_records[f"{record['end_date']}-{record['pivotValues']}"].update(record)

        yield from merged_records.values()

    def _apply_transformations(self):
        """
        Applies transformations to the records based on the configured record selector.
        """
        transformations = [
            AddFields(
                fields=[
                    AddedFieldDefinition(
                        path=field["path"],
                        value=InterpolatedString(string=field["value"], default=field["value"], parameters={}),
                        value_type=str,
                        parameters={},
                    )
                    for field in transformation.get("fields", [])
                ],
                parameters={},
            )
            for transformation in self.record_selector.transformations
            if isinstance(transformation, dict)
        ]

        if transformations:
            self.record_selector.transformations = transformations
