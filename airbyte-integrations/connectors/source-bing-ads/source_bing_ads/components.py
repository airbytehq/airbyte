# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Dict, Iterable, List, Mapping, Optional

from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


PARENT_SLICE_KEY: str = "parent_slice"


@dataclass
class DuplicatedRecordsFilter(RecordFilter):
    """
    Filter duplicated records based on the "Id" field.
    This can happen when we use predicates that could match the same record multiple times.

    e.g.
    With one record like:
    {"type":"RECORD","record":{"stream":"accounts","data":{"Id":151049662,"Name":"Airbyte Plumbing"},"emitted_at":1748277607993}}
    account_names in config:
    [
        {
          "name": "Airbyte",
          "operator": "Contains"
        },
        {
          "name": "Plumbing",
          "operator": "Contains"
        }
    ],
    will return the same record twice, once for each predicate.
    """

    CONFIG_PREDICATES = "account_names"

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._seen_keys = set()

    @cached_property
    def _using_predicates(self) -> bool:
        """
        Indicates whether the connection uses predicates.
        :return: True if the connector uses predicates, False otherwise
        """
        predicates = self.config.get(self.CONFIG_PREDICATES)
        return bool(predicates and isinstance(predicates, list) and predicates)

    def filter_records(
        self, records: List[Mapping[str, Any]], stream_state: StreamState, stream_slice: Optional[StreamSlice] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        for record in records:
            if not self._using_predicates:
                yield record
            else:
                key = record["Id"]
                if key not in self._seen_keys:
                    self._seen_keys.add(key)
                    yield record


@dataclass
class LightSubstreamPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        For migration to manifest connector we needed to migrate legacy state to per partition
        but regular SubstreamPartitionRouter will include the parent_slice in the partition that
        LegacyToPerPartitionStateMigration can't add in transformed state.
        Then, we remove the parent_slice.

        e.g.
        super().stream_slices() = [
            StreamSlice(partition={"parent_slice": {"user_id": 1, "parent_slice": {}}, "account_id": 1}, cursor_slice={}, extra_fields=None),
            StreamSlice(partition={"parent_slice": {"user_id": 2, "parent_slice": {}}, "account_id": 2}, cursor_slice={}, extra_fields=None)            ]
        Router yields: [
            StreamSlice(partition={"account_id": 1}, cursor_slice={}, extra_fields=None),
            StreamSlice(partition={"account_id": 2}, cursor_slice={}, extra_fields=None),
        ]
        """
        stream_slices = super().stream_slices()
        for stream_slice in stream_slices:
            stream_slice_partition: Dict[str, Any] = dict(stream_slice.partition)
            partition_keys = list(stream_slice_partition.keys())
            if PARENT_SLICE_KEY in partition_keys:
                partition_keys.remove(PARENT_SLICE_KEY)
                stream_slice_partition.pop(PARENT_SLICE_KEY, None)
            if len(partition_keys) != 1:
                raise ValueError(f"SubstreamDedupPartitionRouter expects a single partition key-value pair. Got {stream_slice_partition}")

            yield StreamSlice(
                partition=stream_slice_partition,
                cursor_slice=stream_slice.cursor_slice,
                extra_fields=stream_slice.extra_fields,
            )
