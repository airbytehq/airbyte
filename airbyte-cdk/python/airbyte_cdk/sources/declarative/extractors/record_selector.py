#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


@dataclass
class RecordSelector(HttpSelector):
    """
    Responsible for translating an HTTP response into a list of records by extracting records from the response and optionally filtering
    records based on a heuristic.

    Attributes:
        extractor (RecordExtractor): The record extractor responsible for extracting records from a response
        record_filter (RecordFilter): The record filter responsible for filtering extracted records
    """

    extractor: RecordExtractor
    parameters: InitVar[Mapping[str, Any]]
    record_filter: RecordFilter = None

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
        if self.record_filter:
            return self.record_filter.filter_records(
                all_records, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            )
        return all_records
