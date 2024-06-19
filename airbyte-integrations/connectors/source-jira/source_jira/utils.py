#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, MutableMapping

from airbyte_cdk import ConnectorStateManager, InternalConfig, Record
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger
from airbyte_protocol.models import AirbyteMessage, ConfiguredAirbyteStream, Type

_NO_STATE: MutableMapping[str, Any] = {}


def safe_max(arg1, arg2):
    if arg1 is None:
        return arg2
    if arg2 is None:
        return arg1
    return max(arg1, arg2)


def read_full_refresh(stream_instance: Stream):
    yield from _read(stream_instance, SyncMode.full_refresh, _NO_STATE)


def read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]):
    yield from _read(stream_instance, SyncMode.incremental, stream_state)


def _read(stream_instance: Stream, sync_mode: SyncMode, stream_state: MutableMapping[str, Any]):
    configured_stream = ConfiguredAirbyteStream.parse_obj(
        {
            "stream": {
                "name": stream_instance.name,
                "json_schema": {},
                "supported_sync_modes": ["full_refresh"] if sync_mode else ["full_refresh", "incremental"],
            },
            "sync_mode": sync_mode.value,
            "destination_sync_mode": "overwrite",
        }
    )
    stream_instance.state = stream_state
    for record in stream_instance.read(
        configured_stream,
        logging.getLogger("airbyte"),
        DebugSliceLogger(),
        stream_state,
        ConnectorStateManager(stream_instance_map={}),
        InternalConfig.parse_obj({}),
    ):
        if isinstance(record, dict):
            yield record
        elif isinstance(record, Record):
            yield record.data
        elif isinstance(record, AirbyteMessage):
            if record.type == Type.RECORD:
                yield record.record.data
        else:
            raise ValueError(f"Unknown record type '{type(record)}'")
