#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


@dataclass
class RecordSelector(HttpSelector):
    """
    Responsible for translating an HTTP response into a list of records by extracting records from the response and optionally filtering
    records based on a heuristic.

    Attributes:
        extractor (RecordExtractor): The record extractor responsible for extracting records from a response
        record_filter (RecordFilter): The record filter responsible for filtering extracted records
        transformations (List[RecordTransformation]): The transformations to be done on the records
    """

    extractor: RecordExtractor
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    record_filter: RecordFilter = None
    transformations: List[RecordTransformation] = field(default_factory=lambda: [])

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._parameters = parameters

    def select_records(
        self,
        response: requests.Response,
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> List[Record]:
        all_records = [Record(data, stream_slice) for data in self.extractor.extract_records(response)]
        filtered_records = self._filter(all_records, stream_state, stream_slice, next_page_token)
        self._transform(filtered_records, stream_state, stream_slice)
        return filtered_records

    def _filter(
        self,
        records: List[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
    ) -> List[Mapping[str, Any]]:
        if self.record_filter:
            return self.record_filter.filter_records(
                records, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            )
        return records

    def _transform(
        self,
        records: List[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        for record in records:
            for transformation in self.transformations:
                transformation.transform(record, config=self.config, stream_state=stream_state, stream_slice=stream_slice)
