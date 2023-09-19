#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.abstract_stream import AbstractStream
from airbyte_cdk.sources.utils.types import StreamData


class StreamFacade(Stream):
    def __init__(self, stream: AbstractStream):
        self._stream = stream

    @property
    def name(self) -> str:
        return self._stream.name

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        """
        This method should be overridden by subclasses to read records based on the inputs
        """
        return self._stream.read()

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._stream

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        pass

    def get_json_schema(self) -> Mapping[str, Any]:
        pass

    @property
    def source_defined_cursor(self) -> bool:
        pass
