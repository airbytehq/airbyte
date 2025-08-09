# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional

from requests_cache import Response

from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, FieldPointer, StreamSlice, StreamState


@dataclass
class LabelsRecordExtractor(DpathExtractor):
    """
    A custom record extractor is needed to handle cases when records are represented as list of strings insted of dictionaries.
    Example:
        -> ["label 1", "label 2", ..., "label n"]
        <- [{"label": "label 1"}, {"label": "label 2"}, ..., {"label": "label n"}]
    """

    def extract_records(self, response: Response) -> List[Mapping[str, Any]]:
        records = super().extract_records(response)
        return [{"label": record} for record in records]


class SprintIssuesSubstreamPartitionRouter(SubstreamPartitionRouter):
    """
    We often require certain data to be fully retrieved from the parent stream before we begin requesting data from the child stream.
    In this custom component, we execute stream slices twice: first, we retrieve all the parent_stream_fields,
    and then we call stream slices again, this time with the previously fetched fields.
    """

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        fields_parent_stream_config, *parent_stream_configs = self.parent_stream_configs
        self.fields_parent_stream_config = fields_parent_stream_config
        self.parent_stream_configs = parent_stream_configs

    def stream_slices(self) -> Iterable[StreamSlice]:
        self.parent_stream_configs, parent_stream_configs = [self.fields_parent_stream_config], self.parent_stream_configs
        fields = [s.partition[self.fields_parent_stream_config.partition_field.eval(self.config)] for s in super().stream_slices()]
        fields += ["key", "status", "created", "updated"]
        self.parent_stream_configs = parent_stream_configs
        for stream_slice in super().stream_slices():
            stream_slice = StreamSlice(
                partition=stream_slice.partition, cursor_slice=stream_slice.cursor_slice, extra_fields={"fields": fields}
            )
            yield stream_slice


class SubstreamOrSinglePartitionRouter(SubstreamPartitionRouter):
    """
    Depending on the configuration option, we may or may not need to iterate over the parent stream.
    By default, if no projects are set, the child stream should produce records as a normal stream without the parent stream.

    If we do not specify a project in a child stream, it means we are requesting information for all of them,
    so there is no need to slice by all the projects and request data as many times as we have projects one by one.
    That's why an empty slice is returned.

    If projects are defined in the configuration,
    we need to iterate over the given projects and provide a child stream with a slice per project so that it can make a query per project.

    Therefore, if the option is not set, it does not necessarily mean there is no data.
    """

    def stream_slices(self) -> Iterable[StreamSlice]:
        if self.config.get("projects"):
            yield from super().stream_slices()
        else:
            yield from [StreamSlice(partition={}, cursor_slice={})]


@dataclass
class RemoveEmptyFields(RecordTransformation):
    """
    Removes key-value pairs with None values from specified nested dictionaries in a record.

    This transformation is used in the issues stream to clean up record data
    by eliminating empty fields that don't provide any useful information.
    It iterates through the specified field pointers and,
    for each dictionary found at those locations, filters out
    any entries where the value is None.

    Args:
        field_pointers: List of paths to dictionaries in the record that should be cleaned.
        parameters: Additional parameters for the transformation (unused).

    Returns:
        The record with None values removed from the specified dictionaries.
    """

    field_pointers: FieldPointer
    parameters: InitVar[Mapping[str, Any]]

    def transform(
        self,
        record: Mapping[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Mapping[str, Any]:
        for pointer in self.field_pointers:
            if pointer in record:
                record[pointer] = {k: v for k, v in record[pointer].items() if v is not None}
        return record
