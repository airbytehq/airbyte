#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import Stream, StreamData


def get_first_stream_slice(stream: Stream) -> Optional[Mapping[str, Any]]:
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
            cursor_field=stream.cursor_field,  # type: ignore[arg-type]
            sync_mode=SyncMode.full_refresh,
        )
    )
    return next(slices)


def get_first_record_for_slice(stream: Stream, stream_slice: Optional[Mapping[str, Any]]) -> StreamData:
    """
    Gets the first record for a stream_slice of a stream.

    :param stream: stream instance from which to read records
    :param stream_slice: stream_slice parameters for slicing the stream
    :raises StopIteration: if there is no first record to return (the read_records generator is empty)
    :return: StreamData containing the first record in the slice
    """
    # Store the original value of exit_on_rate_limit
    exit_on_rate_limit_has_setter = hasattr(stream.exit_on_rate_limit, "setter")
    original_exit_on_rate_limit = stream.exit_on_rate_limit

    try:
        # Ensure exit_on_rate_limit is safely set to True if possible
        if exit_on_rate_limit_has_setter:
            stream.exit_on_rate_limit = True  # type: ignore[misc] # we check for the setter method using exit_on_rate_limit_has_setter

        # We wrap the return output of read_records() because some implementations return types that are iterable,
        # but not iterators such as lists or tuples
        records_for_slice = iter(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))

        return next(records_for_slice)
    finally:
        # Restore the original exit_on_rate_limit value
        if exit_on_rate_limit_has_setter:
            stream.exit_on_rate_limit = original_exit_on_rate_limit  # type: ignore[misc] # we check for the setter method using exit_on_rate_limit_has_setter
