#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.extractors.jello import JelloExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class RecordSelector(HttpSelector):
    """
    Responsible for translating an HTTP response into a list of records by extracting records from the response and optionally filtering
    records based on a heuristic.
    """

    def __init__(self, extractor: JelloExtractor, record_filter: RecordFilter = None, **options: Optional[Mapping[str, Any]]):
        """
        :param extractor: The record extractor responsible for extracting records from a response
        :param record_filter: The record filter responsible for filtering extracted records
        :param options: Additional runtime parameters to be used for string interpolation
        """
        self._extractor = extractor
        self._record_filter = record_filter
        self._options = options

    def select_records(
        self,
        response: requests.Response,
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> List[Record]:
        all_records = self._extractor.extract_records(response)
        if self._record_filter:
            return self._record_filter.filter_records(
                all_records, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            )
        return all_records
