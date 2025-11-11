#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, List, Mapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.extractors.type_transformer import (
    TypeTransformer as DeclarativeTypeTransformer,
)
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.models import SchemaNormalization
from airbyte_cdk.sources.declarative.retrievers.file_uploader import DefaultFileUploader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.utils.transform import TypeTransformer


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
    schema_normalization: Union[TypeTransformer, DeclarativeTypeTransformer]
    name: str
    _name: Union[InterpolatedString, str] = field(init=False, repr=False, default="")
    record_filter: Optional[RecordFilter] = None
    transformations: List[RecordTransformation] = field(default_factory=lambda: [])
    transform_before_filtering: bool = False
    file_uploader: Optional[DefaultFileUploader] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters
        self._name = (
            InterpolatedString(self._name, parameters=parameters)
            if isinstance(self._name, str)
            else self._name
        )

    @property  # type: ignore
    def name(self) -> str:
        """
        :return: Stream name
        """
        return (
            str(self._name.eval(self.config))
            if isinstance(self._name, InterpolatedString)
            else self._name
        )

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, property):
            self._name = value

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
        yield from self.filter_and_transform(
            all_data, stream_state, records_schema, stream_slice, next_page_token
        )

    def filter_and_transform(
        self,
        all_data: Iterable[Mapping[str, Any]],
        stream_state: StreamState,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Record]:
        """
        There is an issue with the selector as of 2024-08-30: it does technology-agnostic processing like filtering, transformation and
        normalization with an API that is technology-specific (as requests.Response is only for HTTP communication using the requests
        library).

        Until we decide to move this logic away from the selector, we made this method public so that users like AsyncJobRetriever could
        share the logic of doing transformations on a set of records.
        """
        if self.transform_before_filtering:
            transformed_data = self._transform(all_data, stream_state, stream_slice)
            transformed_filtered_data = self._filter(
                transformed_data, stream_state, stream_slice, next_page_token
            )
        else:
            filtered_data = self._filter(all_data, stream_state, stream_slice, next_page_token)
            transformed_filtered_data = self._transform(filtered_data, stream_state, stream_slice)
        normalized_data = self._normalize_by_schema(
            transformed_filtered_data, schema=records_schema
        )
        for data in normalized_data:
            record = Record(data=data, stream_name=self.name, associated_slice=stream_slice)
            if self.file_uploader:
                self.file_uploader.upload(record)
            yield record

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
                records,
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
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
                transformation.transform(
                    record,  # type: ignore  # record has type Mapping[str, Any], but Dict[str, Any] expected
                    config=self.config,
                    stream_state=stream_state,
                    stream_slice=stream_slice,
                )
            yield record
