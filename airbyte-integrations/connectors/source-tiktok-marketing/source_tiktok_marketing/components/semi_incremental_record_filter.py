# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.extractors import RecordFilter
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


class PerPartitionRecordFilter(RecordFilter):
    """
    Prepares per partition stream state to be used in the Record Filter condition.
    Gets current stream state cursor value for stream slice and passes it to condition.

    From
     {"states": [{"partition": {"advertiser_id": 1, "parent_slice": {}}, "cursor": {"start_time": "2023-12-31"}}]}
    To
     {"start_time": "2023-12-31"}.

    partition_field:str: Used to get partition value from current slice.
    """

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._partition_field = parameters["partition_field"]

    def filter_records(
        self,
        records: Iterable[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = next(
            (
                p["cursor"]
                for p in stream_state.get("states", [])
                if p["partition"][self._partition_field] == stream_slice[self._partition_field]
            ),
            {},
        )

        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}

        for record in records:
            if self._filter_interpolator.eval(self.config, record=record, **kwargs):
                yield record
