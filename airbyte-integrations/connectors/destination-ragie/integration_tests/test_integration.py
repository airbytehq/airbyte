import time
import uuid

import pytest
from destination_ragie.destination import DestinationRagie

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)


def make_record(stream_name: str, data: dict) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream_name,
            data=data,
            emitted_at=int(time.time()) * 1000,
        ),
    )


def make_state(stream_states: dict) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(data=stream_states),
    )


@pytest.fixture
def destination():
    return DestinationRagie()


@pytest.fixture
def mock_config():
    return {"api_key": "test_api_key"}  # Adjust keys per your RagieConfig


@pytest.fixture
def configured_catalog():
    stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="append_stream",
            json_schema={"type": "object", "properties": {"id": {"type": "string"}}},
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],  # Required field
        ),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )

    return ConfiguredAirbyteCatalog(streams=[stream])


def test_write_append(destination, mock_config, configured_catalog):
    test_id = f"test_{uuid.uuid4().hex[:8]}"
    record = make_record(
        "append_stream",
        {
            "id": test_id,
            "title": "Mocked Append Test",
            "message": "This is a CI test record.",
            "author": "CI",
            "category": "test",
            "tags": ["ci", "mock"],
        },
    )

    messages = [record, make_state({"append_stream": test_id})]
    output = list(destination.write(mock_config, configured_catalog, messages))

    assert any(msg.type == Type.STATE for msg in output)


def test_write_overwrite(destination, mock_config, configured_catalog):
    record = make_record(
        "append_stream",
        {
            "id": "overwrite_1",
            "title": "Mocked Overwrite Test",
            "message": "CI overwrite test record.",
            "author": "CI",
            "category": "overwrite",
            "tags": ["ci"],
        },
    )

    messages = [record, make_state({"append_stream": "overwrite_1"})]
    output = list(destination.write(mock_config, configured_catalog, messages))

    assert any(msg.type == Type.STATE for msg in output)
