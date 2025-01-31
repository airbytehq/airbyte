#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, MutableMapping

from airbyte_cdk.sources.streams import Stream


_NO_STATE: MutableMapping[str, Any] = {}


def safe_max(arg1, arg2):
    if arg1 is None:
        return arg2
    if arg2 is None:
        return arg1
    return max(arg1, arg2)


def read_full_refresh(stream_instance: Stream):
    yield from stream_instance.read_only_records()


def read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]):
    stream_instance.state = stream_state.copy() if stream_state is not None else stream_state
    yield from stream_instance.read_only_records(stream_state)
