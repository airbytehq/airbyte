#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import sys

from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode


def configure_catalog():
    record = AirbyteMessage.parse_raw(sys.stdin.read())
    streams = []

    for stream in record.catalog.streams:
        configured_stream = ConfiguredAirbyteStream(
            stream=stream,
            sync_mode=stream.supported_sync_modes[0],
            destination_sync_mode=DestinationSyncMode.append,
        )
        if stream.source_defined_primary_key:
            configured_stream.primary_key = stream.source_defined_primary_key

        if stream.source_defined_cursor and stream.default_cursor_field:
            configured_stream.cursor_field = stream.default_cursor_field or None

        streams.append(configured_stream)

    configured_catalog = ConfiguredAirbyteCatalog(streams=streams)
    print(configured_catalog.json(exclude_unset=True))


if __name__ == "__main__":
    configure_catalog()
