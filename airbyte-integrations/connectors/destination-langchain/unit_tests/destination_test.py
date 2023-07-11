#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from airbyte_cdk.models.airbyte_protocol import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    Level,
    Type,
)
from destination_langchain.config import ConfigModel
from destination_langchain.destination import BATCH_SIZE, DestinationLangchain, embedder_map, indexer_map


def _generate_record_message(index: int):
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="example_stream", emitted_at=1234, data={"column_name": f"value {index}", "id": index}))


@patch.dict(embedder_map, {"openai": MagicMock()})
@patch.dict(indexer_map, {"pinecone": MagicMock()})
def test_write():
    """
    Basic test for the write method, batcher and document processor.
    """
    config = {
        "processing": {"text_fields": ["column_name"], "chunk_size": 1000},
        "embedding": {"mode": "openai", "openai_key": "mykey"},
        "indexing": {
            "mode": "pinecone",
            "pinecone_key": "mykey",
            "index": "myindex",
            "pinecone_environment": "myenv",
        },
    }
    config_model = ConfigModel.parse_obj(config)

    configured_catalog: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog.parse_obj(
        {
            "streams": [
                {
                    "stream": {
                        "name": "example_stream",
                        "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": False,
                        "default_cursor_field": ["column_name"],
                    },
                    "primary_key": [["id"]],
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append_dedup",
                }
            ]
        }
    )
    # messages are flushed after 32 records or after a state message, so this will trigger two batches to be processed
    input_messages = [_generate_record_message(i) for i in range(BATCH_SIZE + 5)]
    state_message = AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage())
    input_messages.append(state_message)
    # messages are also flushed once the input messages are exhausted, so this will trigger another batch
    input_messages.extend([_generate_record_message(i) for i in range(5)])

    mock_embedder = MagicMock()
    embedder_map["openai"].return_value = mock_embedder

    mock_indexer = MagicMock()
    indexer_map["pinecone"].return_value = mock_indexer
    mock_indexer.max_metadata_size = 1000
    post_sync_log_message = AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="post sync"))
    mock_indexer.post_sync.return_value = [post_sync_log_message]

    # Create the DestinationLangchain instance
    destination = DestinationLangchain()

    output_messages = destination.write(config, configured_catalog, input_messages)
    output_message = next(output_messages)
    # assert state message is
    assert output_message == state_message

    embedder_map["openai"].assert_called_with(config_model.embedding)
    indexer_map["pinecone"].assert_called_with(config_model.indexing, mock_embedder)
    mock_indexer.pre_sync.assert_called_with(configured_catalog)

    # 1 batches due to max batch size reached and 1 batch due to state message
    assert mock_indexer.index.call_count == 2

    output_message = next(output_messages)
    assert output_message == post_sync_log_message

    try:
        next(output_messages)
        assert False, "Expected end of message stream"
    except StopIteration:
        pass

    # 1 batch due to end of message stream
    assert mock_indexer.index.call_count == 3

    mock_indexer.post_sync.assert_called()
