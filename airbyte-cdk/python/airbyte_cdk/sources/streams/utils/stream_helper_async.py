#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.core_async import AsyncStream


async def get_first_stream_slice(stream: AsyncStream) -> Optional[Mapping[str, Any]]:
    """
    Gets the first stream_slice from a given stream's stream_slices.
    :param stream: stream
    :raises StopIteration: if there is no first slice to return (the stream_slices generator is empty)
    :return: first stream slice from 'stream_slices' generator (`None` is a valid stream slice)
    """
    async for stream_slice in stream.stream_slices(cursor_field=stream.cursor_field, sync_mode=SyncMode.full_refresh):
        return stream_slice
    raise StopIteration(f"No slices in stream {stream.name}")


async def get_first_record_for_slice(stream: AsyncStream, stream_slice: Optional[Mapping[str, Any]]) -> StreamData:
    """
    Gets the first record for a stream_slice of a stream.
    :param stream: stream
    :param stream_slice: stream_slice
    :raises StopIteration: if there is no first record to return (the read_records generator is empty)
    :return: StreamData containing the first record in the slice
    """
    # We wrap the return output of read_records() because some implementations return types that are iterable,
    # but not iterators such as lists or tuples
    async for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
        return record
    raise StopIteration(f"No records in stream {stream.name}")
