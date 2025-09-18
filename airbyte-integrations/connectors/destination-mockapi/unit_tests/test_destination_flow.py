# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime

from destination_mockapi.destination import DestinationMockapi

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)


def test_destination_with_simulated_source_data():
    """Test destination connector with data that would come from a source"""

    # Your config
    config = {"api_url": "https://68cc13e1716562cf50764f2b.mockapi.io/api/v1", "batch_size": 10, "timeout": 30}

    # Configure catalog (tells destination what streams to expect)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="users",
                    json_schema={
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                            "avatar": {"type": "string"},
                        },
                    },
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="deals",
                    json_schema={
                        "type": "object",
                        "properties": {"id": {"type": "string"}, "name": {"type": "string"}, "avatar": {"type": "string"}},
                    },
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            ),
        ]
    )

    # Simulate messages from a source connector
    messages = [
        # User records (as they would come from a source)
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="users",
                data={
                    "id": "src_user_1",
                    "name": "John Doe from Source",
                    "email": "john.source@example.com",
                    "avatar": "https://example.com/john.jpg",
                },
                emitted_at=int(datetime.now().timestamp() * 1000),
            ),
        ),
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="users",
                data={
                    "id": "src_user_2",
                    "name": "Jane Smith from Source",
                    "email": "jane.source@example.com",
                    "avatar": "https://example.com/jane.jpg",
                },
                emitted_at=int(datetime.now().timestamp() * 1000),
            ),
        ),
        # Deal records
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="deals",
                data={"id": "src_deal_1", "name": "Big Deal from Source", "avatar": "https://example.com/deal1.jpg"},
                emitted_at=int(datetime.now().timestamp() * 1000),
            ),
        ),
    ]

    # Test the destination
    destination = DestinationMockapi()

    # This is how Airbyte calls your destination
    output_messages = list(destination.write(config, catalog, messages))

    print("✅ Destination processed the messages successfully!")
    print(f"Processed {len(output_messages)} state messages")


if __name__ == "__main__":
    test_destination_with_simulated_source_data()
