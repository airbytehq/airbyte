#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.models import SchemaNormalization
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

SCHEMA_TRANSFORMER_TYPE_MAPPING = {
    SchemaNormalization.None_: TransformConfig.NoTransform,
    SchemaNormalization.Default: TransformConfig.DefaultSchemaNormalization,
}


@dataclass
class RecordSelector(HttpSelector):
    """
    Responsible for translating an HTTP response into a list of records by extracting records from the response and optionally filtering
    records based on a heuristic.

    Attributes:
        extractor (RecordExtractor): The record extractor responsible for extracting records from a response
        schema_normalization (TypeTransformer): The record normalizer responsible for casting record values to stream schema types
        record_filter (RecordFilter): The record filter responsible for filtering extracted records
        transformations (List[RecordTransformation]): The transformations to be done on the records
    """

    extractor: RecordExtractor
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    schema_normalization: TypeTransformer
    record_filter: Optional[RecordFilter] = None
    transformations: List[RecordTransformation] = field(default_factory=lambda: [])

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    def select_records(
        self,
        response: requests.Response,
        stream_state: StreamState,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> List[Record]:
        """
        Selects records from the response
        :param response: The response to select the records from
        :param stream_state: The stream state
        :param records_schema: json schema of records to return
        :param stream_slice: The stream slice
        :param next_page_token: The paginator token
        :return: List of Records selected from the response
        """
        all_data = self.extractor.extract_records(response)
        filtered_data = self._filter(all_data, stream_state, stream_slice, next_page_token)
        self._transform(filtered_data, stream_state, stream_slice)
        self._normalize_by_schema(filtered_data, schema=records_schema)
        return [Record(data, stream_slice) for data in filtered_data]

    def _normalize_by_schema(self, records: List[Mapping[str, Any]], schema: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
        if schema:
            # record has type Mapping[str, Any], but dict[str, Any] expected
            return [self.schema_normalization.transform(record, schema) for record in records]  # type: ignore
        return records

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
                # record has type Mapping[str, Any], but Record expected
                transformation.transform(record, config=self.config, stream_state=stream_state, stream_slice=stream_slice)  # type: ignore
