#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.source import Source
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class CheckStream(ConnectionChecker, JsonSchemaMixin):
    """
    Checks the connections by trying to read records from one or many of the streams selected by the developer

    Attributes:
        stream_name (List[str]): name of streams to read records from
    """

    stream_names: List[str]
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        self._options = options

    def check_connection(self, source: Source, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        streams = source.streams(config)
        stream_name_to_stream = {s.name: s for s in streams}
        if len(streams) == 0:
            return False, f"No streams to connect to from source {source}"
        for stream_name in self.stream_names:
            if stream_name in stream_name_to_stream.keys():
                stream = stream_name_to_stream[stream_name]
                try:
                    # Some streams need a stream slice to read records (eg if they have a SubstreamSlicer)
                    stream_slice = self._get_stream_slice(stream)
                    records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
                    next(records)
                except Exception as error:
                    return False, f"Unable to connect to stream {stream_name} - {error}"
            else:
                raise ValueError(f"{stream_name} is not part of the catalog. Expected one of {stream_name_to_stream.keys()}")
        return True, None

    def _get_stream_slice(self, stream):
        # We wrap the return output of stream_slices() because some implementations return types that are iterable,
        # but not iterators such as lists or tuples
        slices = iter(
            stream.stream_slices(
                cursor_field=stream.cursor_field,
                sync_mode=SyncMode.full_refresh,
            )
        )
        try:
            return next(slices)
        except StopIteration:
            return {}
