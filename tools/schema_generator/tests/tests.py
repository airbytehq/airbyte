from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)

dummy_catalog = ConfiguredAirbyteCatalog(
    streams=[
        ConfiguredAirbyteStream(
            stream=AirbyteStream(name="mystream", json_schema={"type": "object"}),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.overwrite,
        )
    ]
)

print(dummy_catalog.json())
