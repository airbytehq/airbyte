#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.destinations.vector_db_based import ProcessingConfigModel, Writer
from airbyte_cdk.models.airbyte_protocol import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    Level,
    Type,
)


def _generate_record_message(index: int):
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="example_stream", emitted_at=1234, data={"column_name": f"value {index}", "id": index}))


BATCH_SIZE = 32


def test_write():
    """
    Basic test for the write method, batcher and document processor.
    """
    config_model = ProcessingConfigModel(chunk_overlap=0, chunk_size=1000, metadata_fields=None, text_fields=["column_name"])

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
    mock_embedder.embed_chunks.return_value = [[0] * 1536] * (BATCH_SIZE + 5 + 5)
    mock_embedder.embed_chunks.side_effect = lambda chunks: [[0] * 1536] * len(chunks)

    mock_indexer = MagicMock()
    post_sync_log_message = AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="post sync"))
    mock_indexer.post_sync.return_value = [post_sync_log_message]

    # Create the DestinationLangchain instance
    writer = Writer(config_model, mock_indexer, mock_embedder, BATCH_SIZE)

    output_messages = writer.write(configured_catalog, input_messages)
    output_message = next(output_messages)
    # assert state message is
    assert output_message == state_message

    mock_indexer.pre_sync.assert_called_with(configured_catalog)

    # 1 batches due to max batch size reached and 1 batch due to state message
    assert mock_indexer.index.call_count == 2
    assert mock_embedder.embed_chunks.call_count == 2

    output_message = next(output_messages)
    assert output_message == post_sync_log_message

    try:
        next(output_messages)
        assert False, "Expected end of message stream"
    except StopIteration:
        pass

    # 1 batch due to end of message stream
    assert mock_indexer.index.call_count == 3
    assert mock_embedder.embed_chunks.call_count == 3

    mock_indexer.post_sync.assert_called()
