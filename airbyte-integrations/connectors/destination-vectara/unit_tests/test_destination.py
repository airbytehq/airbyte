#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

from destination_vectara.destination import DestinationVectara

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


def test_write_indexes_records_and_emits_state():
    record = AirbyteRecordMessage(
        data={"id": 12, "title": "Test title", "text": "Hello world"},
        stream="users",
        namespace="tenant",
        emitted_at=0,
    )
    record_message = AirbyteMessage(type=Type.RECORD, record=record)
    state_message = AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"checkpoint": "1"}))
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="users",
                    namespace="tenant",
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )
    config = {
        "oauth2": {"client_id": "client-id", "client_secret": "client-secret"},
        "corpus_name": "test-corpus",
        "text_fields": ["text"],
        "title_field": "title",
        "metadata_fields": ["id"],
    }
    indexed_documents = []

    with patch("destination_vectara.destination.VectaraClient") as client_class:
        client_class.return_value.index_documents.side_effect = lambda docs: indexed_documents.extend(list(docs))
        output_messages = list(DestinationVectara().write(config, catalog, [record_message, state_message]))

    assert output_messages == [state_message]
    assert len(indexed_documents) == 1
    document = indexed_documents[0]
    assert document[:3] == (
        {"text": "Hello world"},
        {"id": 12, "_ab_stream": "tenant_users"},
        "Test title",
    )
    assert document[3].isdigit()
