from typing import List, Optional

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)

from airbyte_cdk.connector import TConfig
from airbyte_cdk.sources.embedded.tools import get_first


def get_stream(catalog: AirbyteCatalog, stream_name: str) -> Optional[AirbyteStream]:
    return get_first(catalog.streams, lambda s: s.name == stream_name)

def get_configured_stream(catalog: ConfiguredAirbyteCatalog, stream_name: str) -> Optional[ConfiguredAirbyteStream]:
    return get_first(catalog.streams, lambda s: s.name == stream_name)


def get_stream_names(catalog: AirbyteCatalog) -> List[str]:
    return [stream.name for stream in catalog.streams]


def to_configured_stream(
    stream: AirbyteStream,
    sync_mode: SyncMode = SyncMode.full_refresh,
    destination_sync_mode: DestinationSyncMode = DestinationSyncMode.append,
    cursor_field: Optional[List[str]] = None,
    primary_key: Optional[List[List[str]]] = None,
) -> ConfiguredAirbyteStream:
    return ConfiguredAirbyteStream(
        stream=stream, sync_mode=sync_mode, destination_sync_mode=destination_sync_mode, cursor_field=cursor_field, primary_key=primary_key
    )


def to_configured_catalog(configured_streams: List[ConfiguredAirbyteStream]) -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalog(streams=configured_streams)


def create_configured_catalog(stream_names: List[str], catalog: AirbyteCatalog, sync_mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
    configured_streams = []

    for stream_name in stream_names:
        stream = get_stream(catalog, stream_name)
        configured_streams.append(to_configured_stream(stream, sync_mode=sync_mode))

    return to_configured_catalog(configured_streams)
