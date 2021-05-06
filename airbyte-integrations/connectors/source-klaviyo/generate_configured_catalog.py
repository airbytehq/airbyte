from airbyte_cdk.models import ConfiguredAirbyteCatalog, AirbyteMessage, ConfiguredAirbyteStream, DestinationSyncMode


record = AirbyteMessage.parse_raw(input())
streams = [
    ConfiguredAirbyteStream(
        stream=stream,
        sync_mode=stream.supported_sync_modes[0],
        destination_sync_mode=DestinationSyncMode.append
    ) for stream in record.catalog.streams
]
configured_catalog = ConfiguredAirbyteCatalog(streams=streams)
print(configured_catalog.json(indent=4))
