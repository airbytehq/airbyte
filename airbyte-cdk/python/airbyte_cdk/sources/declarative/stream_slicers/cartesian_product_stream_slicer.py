#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import itertools
from collections import ChainMap
from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class CartesianProductStreamSlicer(StreamSlicer, JsonSchemaMixin):
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
        stream_slicers (List[StreamSlicer]): Underlying stream slicers. The RequestOptions (e.g: Request headers, parameters, etc..) returned by this slicer are the combination of the RequestOptions of its input slicers. If there are conflicts e.g: two slicers define the same header or request param, the conflict is resolved by taking the value from the first slicer, where ordering is determined by the order in which slicers were input to this composite slicer.
    """

    stream_slicers: List[StreamSlicer]
    options: InitVar[Mapping[str, Any]]

    def update_cursor(self, stream_slice: Mapping[str, Any], last_record: Optional[Mapping[str, Any]] = None):
        for slicer in self.stream_slicers:
            slicer.update_cursor(stream_slice, last_record)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return dict(
            ChainMap(
                *[
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
                *[
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
                *[
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
    ) -> Optional[Mapping]:
        return dict(
            ChainMap(
                *[
                    s.get_request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
                    for s in self.stream_slicers
                ]
            )
        )

    def get_stream_state(self) -> Mapping[str, Any]:
        return dict(ChainMap(*[slicer.get_stream_state() for slicer in self.stream_slicers]))

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        sub_slices = (s.stream_slices(sync_mode, stream_state) for s in self.stream_slicers)
        return (ChainMap(*a) for a in itertools.product(*sub_slices))
