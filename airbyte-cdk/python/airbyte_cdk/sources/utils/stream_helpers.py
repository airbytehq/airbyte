#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import StreamData


class StreamHelper:
    def get_first_record(self, stream: Stream) -> StreamData:
        """
        Gets the first record for a stream.

        :param stream: stream
        :return: StreamData containing the first record in the stream
        """
        try:
            # Some streams need a stream slice to read records (e.g. if they have a SubstreamSlicer)
            stream_slice = self.get_stream_slice(stream)
            records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
            return next(records)
        except StopIteration:
            return {}

    @staticmethod
    def get_stream_slice(stream: Stream) -> Optional[Mapping[str, Any]]:
        """
        Gets the first stream_slice from a given stream's stream_slices.

        :param stream: stream
        :return: First stream slice from 'stream_slices' generator
        """
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
