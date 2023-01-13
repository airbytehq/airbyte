#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import traceback
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
        """Check configuration parameters for a source by attempting to get the first record for each stream in the CheckStream's `stream_name` list."""
        streams = source.streams(config)
        stream_name_to_stream = {s.name: s for s in streams}
        if len(streams) == 0:
            return False, f"No streams to connect to from source {source}"
        for stream_name in self.stream_names:
            if stream_name not in stream_name_to_stream.keys():
                raise ValueError(f"{stream_name} is not part of the catalog. Expected one of {stream_name_to_stream.keys()}.")
            stream = stream_name_to_stream[stream_name]

            try:
                # Some streams need a stream slice to read records (e.g. if they have a SubstreamSlicer)
                # Streams that don't need a stream slice will return `None` as their first stream slice.
                stream_slice = self._get_first_stream_slice(stream)
            except StopIteration:
                # If stream_slices has no `next()` item (Note - this is different from stream_slices returning [None]!)
                # This can happen when a substream's `stream_slices` method does a `for record in parent_records: yield <something>`
                # without accounting for the case in which the parent stream is empty.
                reason = f"Cannot attempt to connect to stream {stream_name} - no stream slices were found, likely because the parent stream is empty."
                return False, reason

            try:
                self._get_first_record_for_slice(stream, stream_slice)
                return True, None
            except StopIteration:
                logger.info(f"Successfully connected to stream {stream.name}, but got 0 records.")
                return True, None
            except Exception as error:
                logger.error(f"Encountered an error trying to connect to stream {stream.name}. Error: \n {traceback.format_exc()}")
                return False, f"Unable to connect to stream {stream_name} - {error}"

    def _get_first_stream_slice(self, stream):
        # We wrap the return output of stream_slices() because some implementations return types that are iterable,
        # but not iterators such as lists or tuples
        slices = iter(
            stream.stream_slices(
                cursor_field=stream.cursor_field,
                sync_mode=SyncMode.full_refresh,
            )
        )
        return next(slices)

    def _get_first_record_for_slice(self, stream, stream_slice):
        records_for_slice = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
        return next(records_for_slice)
