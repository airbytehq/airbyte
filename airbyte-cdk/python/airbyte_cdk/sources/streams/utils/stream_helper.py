#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import Stream, StreamData


def get_first_stream_slice(stream) -> Optional[Mapping[str, Any]]:
    """
    Gets the first stream_slice from a given stream's stream_slices.
    :param stream: stream
    :raises StopIteration: if there is no first slice to return (the stream_slices generator is empty)
    :return: first stream slice from 'stream_slices' generator (`None` is a valid stream slice)
    """
    # We wrap the return output of stream_slices() because some implementations return types that are iterable,
    # but not iterators such as lists or tuples
    slices = iter(
        stream.stream_slices(
            cursor_field=stream.cursor_field,
            sync_mode=SyncMode.full_refresh,
        )
    )
    return next(slices)


def get_first_record_for_slice(stream: Stream, stream_slice: Optional[Mapping[str, Any]]) -> StreamData:
    """
    Gets the first record for a stream_slice of a stream.
    :param stream: stream
    :param stream_slice: stream_slice
    :raises StopIteration: if there is no first record to return (the read_records generator is empty)
    :return: StreamData containing the first record in the slice
    """
    records_for_slice = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
    return next(records_for_slice)
