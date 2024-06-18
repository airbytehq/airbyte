#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import itertools
from collections import ChainMap
from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional

from airbyte_cdk.sources.declarative.partition_routers.partition_router import PartitionRouter
from airbyte_cdk.sources.types import StreamSlice, StreamState


@dataclass
class CartesianProductStreamSlicer(PartitionRouter):
    """
    Stream slicers that iterates over the cartesian product of input stream slicers
    Given 2 stream slicers with the following slices:
    A: [{"i": 0}, {"i": 1}, {"i": 2}]
    B: [{"s": "hello"}, {"s": "world"}]
    the resulting stream slices are
    [
        {"i": 0, "s": "hello"},
        {"i": 0, "s": "world"},
        {"i": 1, "s": "hello"},
        {"i": 1, "s": "world"},
        {"i": 2, "s": "hello"},
        {"i": 2, "s": "world"},
    ]

    Attributes:
        stream_slicers (List[PartitionRouter]): Underlying stream slicers. The RequestOptions (e.g: Request headers, parameters, etc..) returned by this slicer are the combination of the RequestOptions of its input slicers. If there are conflicts e.g: two slicers define the same header or request param, the conflict is resolved by taking the value from the first slicer, where ordering is determined by the order in which slicers were input to this composite slicer.
    """

    stream_slicers: List[PartitionRouter]
    parameters: InitVar[Mapping[str, Any]]

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return dict(
            ChainMap(
                *[  # type: ignore # ChainMap expects a MutableMapping[Never, Never] for reasons
                    s.get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
                    for s in self.stream_slicers
                ]
            )
        )

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return dict(
            ChainMap(
                *[  # type: ignore # ChainMap expects a MutableMapping[Never, Never] for reasons
                    s.get_request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
                    for s in self.stream_slicers
                ]
            )
        )

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return dict(
            ChainMap(
                *[  # type: ignore # ChainMap expects a MutableMapping[Never, Never] for reasons
                    s.get_request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
                    for s in self.stream_slicers
                ]
            )
        )

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return dict(
            ChainMap(
                *[  # type: ignore # ChainMap expects a MutableMapping[Never, Never] for reasons
                    s.get_request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
                    for s in self.stream_slicers
                ]
            )
        )

    def stream_slices(self) -> Iterable[StreamSlice]:
        sub_slices = (s.stream_slices() for s in self.stream_slicers)
        product = itertools.product(*sub_slices)
        for stream_slice_tuple in product:
            partition = dict(ChainMap(*[s.partition for s in stream_slice_tuple]))  # type: ignore # ChainMap expects a MutableMapping[Never, Never] for reasons
            cursor_slices = [s.cursor_slice for s in stream_slice_tuple if s.cursor_slice]
            if len(cursor_slices) > 1:
                raise ValueError(f"There should only be a single cursor slice. Found {cursor_slices}")
            if cursor_slices:
                cursor_slice = cursor_slices[0]
            else:
                cursor_slice = {}
            yield StreamSlice(partition=partition, cursor_slice=cursor_slice)

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Set the state of the parent streams.

        This method tries to set the parent state for every stream slicer. If a stream slicer does not have parent streams,
        this will be skipped due to the default StreamSlicer implementation.

        Args:
            stream_state (StreamState): The state of the streams to be set. If `parent_state` exists in the
            stream_state, it will update the state of each parent stream with the corresponding state from the stream_state.

        Example of state format:
        {
            "parent_state": {
                "parent_stream_name_1": {
                    "last_updated": "2023-05-27T00:00:00Z"
                },
                "parent_stream_name_2": {
                    "last_updated": "2023-05-27T00:00:00Z"
                }
            }
        }
        """
        for stream_slicer in self.stream_slicers:
            stream_slicer.set_initial_state(stream_state)

    def get_stream_state(self) -> Optional[Mapping[str, StreamState]]:
        """
        Get the state of the parent streams.

        This method returns the combined parent states from all stream slicers. If a stream slicer does not have parent streams,
        this will be skipped due to the default StreamSlicer implementation.

        Returns:
            Optional[Mapping[str, StreamState]]: The current state of the parent streams in a dictionary format.
                 The returned format will be:
                 {
                     "parent_stream_name1": {
                         "last_updated": "2023-05-27T00:00:00Z"
                     },
                     "parent_stream_name2": {
                         "last_updated": "2023-05-27T00:00:00Z"
                     }
                 }
        """
        combined_state: dict[str, StreamState] = {}
        for s in self.stream_slicers:
            parent_state = s.get_stream_state()
            if parent_state:
                combined_state.update(parent_state)
        return combined_state
