#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.models import SchemaNormalization
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
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
    ) -> Iterable[Record]:
        """
        Selects records from the response
        :param response: The response to select the records from
        :param stream_state: The stream state
        :param records_schema: json schema of records to return
        :param stream_slice: The stream slice
        :param next_page_token: The paginator token
        :return: List of Records selected from the response
        """
        all_data: Iterable[Mapping[str, Any]] = self.extractor.extract_records(response)
        filtered_data = self._filter(all_data, stream_state, stream_slice, next_page_token)
        transformed_data = self._transform(filtered_data, stream_state, stream_slice)
        normalized_data = self._normalize_by_schema(transformed_data, schema=records_schema)
        for data in normalized_data:
            yield Record(data, stream_slice)

    def _normalize_by_schema(
        self, records: Iterable[Mapping[str, Any]], schema: Optional[Mapping[str, Any]]
    ) -> Iterable[Mapping[str, Any]]:
        if schema:
            # record has type Mapping[str, Any], but dict[str, Any] expected
            for record in records:
                normalized_record = dict(record)
                self.schema_normalization.transform(normalized_record, schema)
                yield normalized_record
        else:
            yield from records

    def _filter(
        self,
        records: Iterable[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
    ) -> Iterable[Mapping[str, Any]]:
        if self.record_filter:
            yield from self.record_filter.filter_records(
                records, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            )
        else:
            yield from records

    def _transform(
        self,
        records: Iterable[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in records:
            for transformation in self.transformations:
                # record has type Mapping[str, Any], but Record expected
                transformation.transform(record, config=self.config, stream_state=stream_state, stream_slice=stream_slice)  # type: ignore
            yield record
