#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.types import StreamSlice, StreamState


@dataclass
class SinglePartitionRouter(PartitionRouter):
    """Partition router returning only a stream slice"""

    parameters: InitVar[Mapping[str, Any]]

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_body_data(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def stream_slices(self) -> Iterable[StreamSlice]:
        yield StreamSlice(partition={}, cursor_slice={})

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        SinglePartitionRouter doesn't have parent streams
        """
        pass

    def get_stream_state(self) -> Optional[Mapping[str, StreamState]]:
        """
        SinglePartitionRouter doesn't have parent streams
        """
        pass
