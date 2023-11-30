#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import StreamData


class MockStream(Stream):
    def __init__(
        self,
        slices_and_records_or_exception: Iterable[Tuple[Optional[Mapping[str, Any]], Iterable[Union[Exception, Mapping[str, Any]]]]],
        name,
        json_schema,
        primary_key=None,
    ):
        self._slices_and_records_or_exception = slices_and_records_or_exception
        self._name = name
        self._json_schema = json_schema
        self._primary_key = primary_key

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        for _slice, records_or_exception in self._slices_and_records_or_exception:
            if stream_slice == _slice:
                for item in records_or_exception:
                    if isinstance(item, Exception):
                        raise item
                    yield item

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @property
    def name(self) -> str:
        return self._name

    def get_json_schema(self) -> Mapping[str, Any]:
        return self._json_schema

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if self._slices_and_records_or_exception:
            yield from [_slice for _slice, records_or_exception in self._slices_and_records_or_exception]
        else:
            yield None
